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

Locating the binary (no hard-coded paths): pass uno_bin=..., else set the
environment variable UNO_AMPL_BIN, else `uno_ampl` must be on PATH.

Important behavior this module accounts for (verified against the UNO source):
  * `uno_ampl` returns exit code 0 even when a solve fails (iteration limit,
    evaluation error, ...). It returns 1 only on a setup/parse error, printing
    `uno_ampl failed with the following error: <msg>` to stdout. So the outcome
    is classified from the printed `Optimization status:`, not the return code.

CLI:
    python scripts/uno_runner.py <problem.nl> --preset ipopt
    python scripts/uno_runner.py <problem.nl> --option globalization_mechanism=LS \\
        --option hessian_model=exact --json

Library:
    from uno_runner import run_uno
    res = run_uno("problems/CUTE/hs071/hs071.nl", preset="ipopt")
    print(res.outcome, res.objective, res.iterations)

Stdlib only -- installs nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
ENV_BIN = "UNO_AMPL_BIN"          # env var pointing at the uno_ampl binary
DEFAULT_BIN_NAME = "uno_ampl"     # looked up on PATH as a last resort

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
    """Locate the uno_ampl binary: explicit arg -> $UNO_AMPL_BIN -> PATH.

    Raises FileNotFoundError with guidance if none is usable.
    """
    candidates = [explicit, os.environ.get(ENV_BIN), shutil.which(DEFAULT_BIN_NAME)]
    for cand in candidates:
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            return str(Path(cand).resolve())
    raise FileNotFoundError(
        "Could not locate the 'uno_ampl' binary. Pass uno_bin=... (or --uno-bin), "
        f"set the {ENV_BIN} environment variable to its path, or put it on PATH.")


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


def classify(returncode: int, optimization_status: str | None) -> str:
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
def run_uno(nl_path, *, preset=None, options=None, uno_bin=None, timeout=None,
            write_solution=False, capture_stdout=False, extra_args=None) -> UnoResult:
    """Solve one .nl with UNO and return a structured UnoResult.

    nl_path        : path to the AMPL .nl model.
    preset         : preset name (e.g. "ipopt"), or None.
    options        : dict of custom run-time-options (override the preset).
    uno_bin        : path to uno_ampl (else $UNO_AMPL_BIN, else PATH).
    timeout        : wall-clock seconds; on expiry outcome="timeout".
    write_solution : add -AMPL so UNO writes <stub>.sol (path in .solution_file).
    capture_stdout : keep UNO's raw stdout in .stdout.
    extra_args     : extra raw CLI tokens appended verbatim.
    """
    opts_record = {**({"preset": preset} if preset else {}), **(options or {})}

    try:
        binary = resolve_uno_bin(uno_bin)
    except FileNotFoundError as exc:
        return UnoResult(outcome=OUTCOME_FAILED, error=str(exc), options=opts_record)

    nl = Path(nl_path)
    if not nl.is_file():
        return UnoResult(outcome=OUTCOME_FAILED, options=opts_record,
                         error=f"model file not found: {nl}")

    argv = _build_argv(binary, nl, preset, options, write_solution, extra_args)

    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return UnoResult(outcome=OUTCOME_TIMEOUT, timed_out=True,
                         options=opts_record, cmd=argv)

    out = proc.stdout or ""
    fields = parse_stdout(out)
    outcome = classify(proc.returncode, fields["optimization_status"])

    error = None
    if outcome == OUTCOME_FAILED:
        m = re.search(_SETUP_ERROR_RE, out)
        error = m.group(1).strip() if m else (proc.stderr or "").strip()[:300] or None

    sol_file = None
    if write_solution:
        candidate = nl.with_suffix(".sol")
        if candidate.is_file():
            sol_file = str(candidate)

    return UnoResult(
        outcome=outcome,
        returncode=proc.returncode,
        error=error,
        solution_file=sol_file,
        options=opts_record,
        cmd=argv,
        stdout=out if capture_stdout else None,
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
                    help=f"path to uno_ampl (else ${ENV_BIN}, else PATH)")
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
        args.nl, preset=args.preset, options=options, uno_bin=args.uno_bin,
        timeout=args.timeout, write_solution=args.write_solution,
        capture_stdout=args.print_stdout,
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
