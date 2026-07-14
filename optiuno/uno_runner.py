#!/usr/bin/env python3
"""Drive the UNO solver (`uno_ampl`) from Python via subprocess.

One call solves one AMPL `.nl` file with a chosen configuration and returns a
structured `UnoResult`. A configuration is any mix of:
  * a preset          -> preset=<name>        (ipopt / filtersqp / funnelsqp / filterslp)
  * custom options    -> key=value ...        (the run-time-options / strategy blocks)
Custom options are placed after `preset=` on the command line, so they override
the preset -- matching UNO's own parse order.

UNO is treated as a read-only external dependency: it is invoked only through
its command-line options, never modified.

Locating the binary (system-first, via optiuno.utils.select_uno_bin): pass
uno_bin=..., else set the environment variable UNO_AMPL_BIN, else `uno_ampl` on
PATH, else fall back to the prebuilt UNO bundled at `external/uno/`. When the
resolved binary lives in a self-contained UNO release layout (a sibling `deps/`
directory next to `lib/`, as in the bundled `external/uno/`), the matching
`lib/` and `deps/` are prepended to `LD_LIBRARY_PATH` automatically.

Important behavior this module accounts for (verified against the UNO source):
  * `uno_ampl` returns exit code 0 even when a solve fails (iteration limit,
    evaluation error, ...). It returns 1 only on a setup/parse error, printing
    `uno_ampl failed with the following error: <msg>` to stdout. So the outcome
    is classified from the printed `Optimization status:`, not the return code.
  * UNO echoes the *actually composed* method as a banner, e.g.
    `Uno 2.8.0 (TR Fletcher-filter ... SQP method ...)`, or
    `Uno 2.8.0 (strategy combination not initialized)` for an invalid combo.
    That banner is captured in `UnoResult.banner` so callers can detect the
    silently-rewritten / invalid-combination cases.

CLI:
    python -m optiuno.uno_runner <problem.nl> --preset ipopt
    python -m optiuno.uno_runner <problem.nl> --option globalization_mechanism=LS \\
        --option hessian_model=exact --json

Library:
    from optiuno.uno_runner import run_uno            # or: from optiuno import run_uno
    res = run_uno("problems/CUTE/hs071/hs071.nl", preset="ipopt")
    print(res.outcome, res.objective, res.iterations)

Stdlib only -- installs nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .utils import select_uno_bin

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
ENV_BIN = "UNO_AMPL_BIN"          # env var pointing at the uno_ampl binary

# Default per-problem UNO time budget (seconds). Passed to UNO as time_limit=
# and used to derive the subprocess watchdog when no explicit timeout is given.
DEFAULT_TIME_LIMIT = 20.0

# Closed sets of `Optimization status:` values (from UNO's OptimizationStatus).
_SOLVED_STATES = {"Success"}
_BUDGET_STATES = {"Iteration limit", "Time limit", "User termination"}
_ERROR_STATES = {"Evaluation error", "Algorithmic error", "Unknown"}

# Outcome categories returned in UnoResult.outcome.
OUTCOME_SOLVED = "solved"     # converged (Optimization status: Success)
OUTCOME_BUDGET = "budget"     # ran out of iteration/time budget (valid config)
OUTCOME_ERROR = "error"       # solver-level failure on this instance
OUTCOME_FAILED = "failed"     # could not run: setup/parse error or no output
OUTCOME_TIMEOUT = "timeout"   # exceeded the wall-clock timeout

_NUM = r"([-+0-9.eEnaN]+)"    # tolerant numeric token (also matches nan/inf-ish)

# The composed-method banner, e.g. "Uno 2.8.0 (TR Fletcher-filter ... method)".
_RE_BANNER = re.compile(r"^Uno [\d.]+ \((?P<desc>.+)\)\s*$", re.MULTILINE)

# stdout label -> (regex, cast). Labels are matched as substrings so the
# box-drawing prefixes (┌ │ └) on the residual lines don't matter.
_FIELDS = {
    "optimization_status":      (r"Optimization status:\s*(.+)", str),
    "solution_status":          (r"Solution status:\s*(.+)", str),
    "objective":                (rf"Objective value:\s*{_NUM}", float),
    "primal_feasibility":       (rf"Primal feasibility:\s*{_NUM}", float),
    "stationarity_residual":    (rf"Stationarity residual:\s*{_NUM}", float),
    "complementarity_residual": (rf"Complementarity residual:\s*{_NUM}", float),
    "cpu_time":                 (rf"CPU time:\s*{_NUM}s", float),
    "iterations":               (r"Iterations:\s*(\d+)", int),
    "objective_evals":          (r"Objective evaluations:\s*(\d+)", int),
    "constraint_evals":         (r"Constraints evaluations:\s*(\d+)", int),
    "objective_gradient_evals": (r"Objective gradient evaluations:\s*(\d+)", int),
    "jacobian_evals":           (r"Jacobian evaluations:\s*(\d+)", int),
    "hessian_evals":            (r"Hessian evaluations:\s*(\d+)", int),
    "subproblems":              (r"Number of subproblems solved:\s*(\d+)", int),
}
# UNO's stdout line on a setup/parse failure (exit code 1).
_SETUP_ERROR_RE = r"uno_ampl failed with the following error:\s*(.+)"


# --------------------------------------------------------------------------- #
# Result type
# --------------------------------------------------------------------------- #
@dataclass
class UnoResult:
    """Parsed outcome of a single `uno_ampl` run."""
    outcome: str
    optimization_status: str | None = None
    solution_status: str | None = None
    objective: float | None = None
    primal_feasibility: float | None = None
    stationarity_residual: float | None = None
    complementarity_residual: float | None = None
    cpu_time: float | None = None
    iterations: int | None = None
    objective_evals: int | None = None
    constraint_evals: int | None = None
    objective_gradient_evals: int | None = None
    jacobian_evals: int | None = None
    hessian_evals: int | None = None
    subproblems: int | None = None
    returncode: int | None = None
    timed_out: bool = False
    error: str | None = None
    solution_file: str | None = None
    problem: str | None = None            # .nl stem, for convenience in sweeps
    wall_time: float | None = None        # wall-clock seconds around the subprocess
    banner: str | None = None             # composed-method description UNO printed
    options: dict = field(default_factory=dict)
    cmd: list = field(default_factory=list)
    stdout: str | None = None

    @property
    def ok(self) -> bool:
        """True if UNO ran and produced a result (solved or hit a budget)."""
        return self.outcome in (OUTCOME_SOLVED, OUTCOME_BUDGET)

    def to_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Binary resolution
# --------------------------------------------------------------------------- #
def resolve_uno_bin(explicit: str | None = None) -> str:
    """Locate the uno_ampl binary: explicit arg -> $UNO_AMPL_BIN -> PATH -> bundled.

    Thin wrapper over :func:`optiuno.utils.select_uno_bin` (the single UNO-location
    authority): a system UNO is preferred, with the bundled ``external/uno`` build
    as the fallback. Raises FileNotFoundError with guidance if none is usable.
    """
    return select_uno_bin(explicit)


def _bundled_env(binary: str) -> dict | None:
    """Env with LD_LIBRARY_PATH wired up for a self-contained UNO release.

    Detected by a `deps/` sibling of `lib/` two levels up from the binary
    (`<root>/bin/uno_ampl` -> `<root>/{lib,deps}`), which system installs lack.
    Returns None to inherit the current environment when not a bundled layout.
    """
    base = Path(binary).resolve().parent.parent
    lib, deps = base / "lib", base / "deps"
    if not deps.is_dir():
        return None
    existing = os.environ.get("LD_LIBRARY_PATH", "")
    ld = f"{lib}:{deps}" + (f":{existing}" if existing else "")
    return {**os.environ, "LD_LIBRARY_PATH": ld}


# --------------------------------------------------------------------------- #
# Parsing / classification
# --------------------------------------------------------------------------- #
def _safe_cast(text: str, cast):
    try:
        return cast(text.strip())
    except (TypeError, ValueError):
        return None


def parse_stdout(text: str) -> dict:
    """Extract every known summary field from uno_ampl's stdout (missing->None)."""
    fields = {}
    for key, (pattern, cast) in _FIELDS.items():
        m = re.search(pattern, text)          # first match (Primal feasibility x2)
        fields[key] = _safe_cast(m.group(1), cast) if m else None
    return fields


def classify(returncode: int | None, optimization_status: str | None) -> str:
    """Map (returncode, printed status) onto an outcome category."""
    if returncode != 0 or optimization_status is None:
        return OUTCOME_FAILED
    if optimization_status in _SOLVED_STATES:
        return OUTCOME_SOLVED
    if optimization_status in _BUDGET_STATES:
        return OUTCOME_BUDGET
    if optimization_status in _ERROR_STATES:
        return OUTCOME_ERROR
    return OUTCOME_ERROR                        # any unmapped status -> error


# --------------------------------------------------------------------------- #
# Option formatting
# --------------------------------------------------------------------------- #
def _fmt_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"    # UNO uses true/false for bools
    return str(value)


def _build_argv(uno_bin, nl_path, preset, options, write_solution, extra_args):
    """Assemble the uno_ampl command line in UNO's expected order.

    [bin, nl, (-AMPL), option_file=, preset=, <custom options>, <extra_args>].
    -AMPL must be argv[2]; custom options come after preset= so they override it.
    """
    argv = [uno_bin, str(nl_path)]
    if write_solution:
        argv.append("-AMPL")                    # must be argv[2]
    opts = dict(options or {})
    for special in ("option_file", "preset"):   # honor UNO's parse precedence
        if special == "preset" and preset is not None:
            argv.append(f"preset={preset}")
        if special in opts:
            argv.append(f"{special}={_fmt_value(opts.pop(special))}")
    for key, value in opts.items():
        argv.append(f"{key}={_fmt_value(value)}")
    argv.extend(extra_args or [])
    return argv


# --------------------------------------------------------------------------- #
# Core API
# --------------------------------------------------------------------------- #
def run_uno(nl_path, options=None, *, preset=None, uno_bin=None, time_limit=None,
            timeout=None, write_solution=False, capture_stdout=False,
            log_path=None, extra_args=None) -> UnoResult:
    """Solve one .nl with UNO and return a structured UnoResult.

    nl_path        : path to the AMPL .nl model.
    options        : dict of custom run-time-options (override the preset).
    preset         : preset name (e.g. "ipopt"), or None.
    uno_bin        : path to uno_ampl (else $UNO_AMPL_BIN, else PATH, else bundled external/uno).
    time_limit     : UNO's own time budget (added as time_limit=<v> unless already
                     in options); also sets the default watchdog to time_limit+10.
    timeout        : explicit wall-clock watchdog (s); overrides the time_limit
                     default. On expiry outcome="timeout".
    write_solution : add -AMPL so UNO writes <stub>.sol (path in .solution_file).
    capture_stdout : keep UNO's raw stdout in .stdout.
    log_path       : if given, write the command + full output to this file.
    extra_args     : extra raw CLI tokens appended verbatim.
    """
    opts_record = {**({"preset": preset} if preset else {}), **(options or {})}
    nl = Path(nl_path)

    try:
        binary = resolve_uno_bin(uno_bin)
    except FileNotFoundError as exc:
        return UnoResult(outcome=OUTCOME_FAILED, error=str(exc),
                         options=opts_record, problem=nl.stem)

    if not nl.is_file():
        return UnoResult(outcome=OUTCOME_FAILED, options=opts_record, problem=nl.stem,
                         error=f"model file not found: {nl}")

    build_opts = dict(options or {})
    if time_limit is not None and "time_limit" not in build_opts:
        build_opts["time_limit"] = time_limit
    argv = _build_argv(binary, nl, preset, build_opts, write_solution, extra_args)

    env = _bundled_env(binary)
    watchdog = timeout if timeout is not None else (
        time_limit + 10.0 if time_limit is not None else None)

    timed_out = False
    returncode = None
    stderr = ""
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(argv, capture_output=True, text=True,
                              timeout=watchdog, env=env)
        out = proc.stdout or ""
        stderr = proc.stderr or ""
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        raw = exc.stdout or ""
        out = raw.decode(errors="replace") if isinstance(raw, bytes) else raw
    wall = time.perf_counter() - t0

    fields = parse_stdout(out)
    m = _RE_BANNER.search(out)
    banner = m.group("desc") if m else None

    outcome = OUTCOME_TIMEOUT if timed_out else classify(
        returncode, fields["optimization_status"])

    error = None
    if outcome == OUTCOME_FAILED:
        m2 = re.search(_SETUP_ERROR_RE, out)
        error = m2.group(1).strip() if m2 else (stderr or "").strip()[:300] or None

    sol_file = None
    if write_solution and not timed_out:
        candidate = nl.with_suffix(".sol")
        if candidate.is_file():
            sol_file = str(candidate)

    if log_path is not None:
        log_path = Path(log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("$ " + " ".join(argv) + "\n\n" + out)

    return UnoResult(
        outcome=outcome,
        returncode=returncode,
        timed_out=timed_out,
        error=error,
        solution_file=sol_file,
        options=opts_record,
        cmd=argv,
        stdout=out if capture_stdout else None,
        problem=nl.stem,
        wall_time=wall,
        banner=banner,
        **fields,
    )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _parse_options(option_list, options_csv) -> dict:
    """Merge --option k=v (repeatable) and --options "k1=v1,k2=v2" into a dict."""
    opts = {}
    items = list(option_list or [])
    if options_csv:
        items += [tok for tok in options_csv.split(",") if tok.strip()]
    for item in items:
        if "=" not in item:
            raise ValueError(f"option must be key=value, got: {item!r}")
        key, value = item.split("=", 1)
        opts[key.strip()] = value.strip()
    return opts


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Solve an AMPL .nl with UNO (uno_ampl) using a preset and/or "
                    "custom run-time-options.")
    ap.add_argument("nl", help="path to the AMPL .nl model")
    ap.add_argument("--preset", default=None,
                    help="UNO preset (e.g. ipopt, filtersqp, funnelsqp, filterslp)")
    ap.add_argument("--option", action="append", metavar="KEY=VALUE", default=[],
                    help="custom run-time-option (repeatable); overrides the preset")
    ap.add_argument("--options", default=None, metavar="K1=V1,K2=V2",
                    help="comma-separated custom options (merged with --option)")
    ap.add_argument("--uno-bin", default=None,
                    help=f"path to uno_ampl (else ${ENV_BIN}, else PATH, else bundled external/uno)")
    ap.add_argument("--time-limit", type=float, default=None,
                    help="UNO time budget in seconds (added as time_limit=)")
    ap.add_argument("--timeout", type=float, default=None,
                    help="wall-clock seconds before giving up (outcome=timeout)")
    ap.add_argument("--write-solution", action="store_true",
                    help="pass -AMPL so UNO writes <stub>.sol")
    ap.add_argument("--print-stdout", action="store_true",
                    help="echo UNO's raw stdout")
    ap.add_argument("--json", action="store_true",
                    help="print the result as JSON")
    args = ap.parse_args(argv)

    try:
        options = _parse_options(args.option, args.options)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    res = run_uno(
        args.nl, options=options, preset=args.preset, uno_bin=args.uno_bin,
        time_limit=args.time_limit, timeout=args.timeout,
        write_solution=args.write_solution, capture_stdout=args.print_stdout,
    )

    if args.print_stdout and res.stdout:
        print(res.stdout)

    if args.json:
        d = res.to_dict()
        if not args.print_stdout:
            d.pop("stdout", None)
        print(json.dumps(d, indent=2))
    else:
        print(f"problem : {args.nl}")
        cfg = res.options or {}
        print(f"config  : {cfg if cfg else '(defaults)'}")
        print(f"outcome : {res.outcome}")
        print(f"banner  : {res.banner}")
        print(f"opt status : {res.optimization_status}")
        print(f"sol status : {res.solution_status}")
        print(f"objective  : {res.objective}")
        print(f"iterations : {res.iterations}")
        print(f"cpu_time   : {res.cpu_time}")
        if res.solution_file:
            print(f"solution   : {res.solution_file}")
        if res.error:
            print(f"error      : {res.error}")

    return 0 if res.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
