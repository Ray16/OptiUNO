#!/usr/bin/env python3
"""Black-box objective: score one UNO configuration over a set of problems.

This is the decoupled, search-driver-agnostic evaluator. Given

  * a **problem set** (a JSON file listing ``.nl`` models, or a list of paths), and
  * one **UNO config** (a dict of ingredient options; a subset of the six ingredients
    in ``optiuno/uno_search_space.json``),

it solves every problem and returns exactly two numbers:

  reliability   fraction in [0, 1] of problems that reached an optimal solution
                (strict: ``Optimization status: Success`` AND
                ``Solution status: Feasible KKT point``).
  cum_cpu_time  cumulative UNO-reported CPU seconds over the whole set; a timeout
                contributes the full per-problem ``time_limit``.

The intent is that an external optimizer (Bayesian optimization, a genetic algorithm,
random search, complete enumeration, ...) calls this as a black box::

    from optiuno import make_objective
    f = make_objective("problems/sets/hs_model_all.json")
    reliability, cpu_time = f({"globalization_mechanism": "LS", "hessian_model": "LBFGS"})

It is built only on :func:`optiuno.run_uno` and the stdlib, and has **no dependency on
``quickRun/``** -- the ``quickRun`` openEvolve harness is a separate, coupled sibling.
The "solved" criterion is reimplemented here (a two-field check) so it matches the
project-wide definition in ``quickRun/harness/classify.py`` without importing it.

CLI:
    python -m optiuno.objective --problems SET.json \\
        --option globalization_mechanism=LS --option hessian_model=LBFGS [--json]

Stdlib only -- installs nothing.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .uno_runner import DEFAULT_TIME_LIMIT, run_uno
from .utils import REPO_ROOT, bundled_uno_bin

# --------------------------------------------------------------------------- #
# The searchable space, used to validate configs (a subset of these keys/values).
# --------------------------------------------------------------------------- #
_SEARCH_SPACE_PATH = Path(__file__).with_name("uno_search_space.json")
_SEARCH_SPACE_CACHE: dict | None = None


def _search_space() -> dict:
    """Load (and cache) the six-ingredient legal-value map from JSON."""
    global _SEARCH_SPACE_CACHE
    if _SEARCH_SPACE_CACHE is None:
        _SEARCH_SPACE_CACHE = json.loads(_SEARCH_SPACE_PATH.read_text())
    return _SEARCH_SPACE_CACHE


def validate_config(config: dict) -> None:
    """Raise ValueError if `config` has an unknown key or an illegal value.

    Only checks that each *provided* key/value is legal (a partial config is fine --
    unspecified ingredients fall back to UNO's own defaults). It does NOT reject bad
    *combinations* of legal values (e.g. interior_point+TR): those run and simply
    show up as low reliability, which is what the optimizer should observe.
    """
    allowed = _search_space()
    errors = []
    for key, value in config.items():
        if key not in allowed:
            errors.append(f"unknown option {key!r} (not in the search space)")
        elif value not in allowed[key]:
            errors.append(
                f"illegal value {value!r} for {key!r}; allowed: {allowed[key]}")
    if errors:
        raise ValueError("invalid UNO config: " + "; ".join(errors))


# --------------------------------------------------------------------------- #
# Problem-set loading
# --------------------------------------------------------------------------- #
def _resolve_entry(entry, base_dir: str | None) -> Path:
    """Resolve one problem-set entry (a stem or an .nl path) to an absolute Path.

    * an entry ending in ``.nl`` is treated as a path;
    * any other entry is a stem and requires ``base_dir`` (-> ``<base_dir>/<stem>.nl``);
    * relative paths resolve against the repo root, so callers can run from anywhere.
    """
    text = str(entry)
    if text.endswith(".nl"):
        path = Path(text)
    elif base_dir is not None:
        path = Path(base_dir) / f"{text}.nl"
    else:
        raise ValueError(
            f"problem entry {text!r} is a stem but no 'base_dir' was given; "
            "either add base_dir or use a full path ending in .nl")
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def load_problem_set(spec) -> list[Path]:
    """Resolve a problem-set spec to a list of existing ``.nl`` Paths.

    `spec` may be:
      * a path to a problem-set JSON -- either a bare array of entries, or an object
        ``{"problems": [...], "base_dir": "...", "name": "..."}``;
      * a list/tuple of entries (paths or, with no base_dir, full .nl paths);
      * an already-resolved list of Paths (passed through after an existence check).

    Raises FileNotFoundError (listing every missing file) if any entry is absent, so a
    mis-specified set fails loudly instead of silently scoring 0% solved.
    """
    base_dir = None
    if isinstance(spec, (list, tuple)):
        entries = list(spec)
    else:
        p = Path(spec)
        if p.suffix != ".json":
            raise ValueError(
                f"problem_set must be a .json file or a list of paths, got: {spec!r}")
        data = json.loads(p.read_text())
        if isinstance(data, dict):
            entries = data.get("problems")
            base_dir = data.get("base_dir")
            if entries is None:
                raise ValueError(f"{p}: object form must have a 'problems' array")
        elif isinstance(data, list):
            entries = data
        else:
            raise ValueError(f"{p}: expected a JSON array or object")

    if not entries:
        raise ValueError(f"problem set is empty: {spec!r}")

    paths = [_resolve_entry(e, base_dir) for e in entries]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            f"{len(missing)} problem file(s) not found: " + ", ".join(missing[:10])
            + (" ..." if len(missing) > 10 else ""))
    return paths


# --------------------------------------------------------------------------- #
# "Solved" / status classification (matches quickRun/harness/classify.py without
# importing it -- optiuno must not depend on quickRun).
# --------------------------------------------------------------------------- #
def is_solved(res) -> bool:
    """True iff UNO reached an optimal solution on this problem.

    Strict, project-wide criterion: ``Optimization status: Success`` AND
    ``Solution status: Feasible KKT point``.
    """
    return (res.optimization_status == "Success"
            and res.solution_status == "Feasible KKT point")


def _is_timeout(res) -> bool:
    """Timeout in the sense used for time accounting: watchdog fired, or UNO itself
    reported a time-limit termination."""
    if res.timed_out:
        return True
    return "time limit" in (res.optimization_status or "").lower()


def _category(res) -> str:
    """5-way status for detailed reporting: solved/unsolved/timeout/invalid/crash."""
    if res.banner == "strategy combination not initialized":
        return "invalid"
    if res.timed_out:
        return "timeout"
    opt, sol = res.optimization_status or "", res.solution_status or ""
    if opt == "" and sol == "":
        return "crash"
    if "time limit" in opt.lower():
        return "timeout"
    if is_solved(res):
        return "solved"
    return "unsolved"


def _charged_cpu(res, time_limit: float) -> float:
    """Per-problem CPU time to charge (mirrors quickRun benchmark.py:70-74).

    Normal case: UNO-reported CPU seconds. A timeout charges the full time_limit; a
    crash / unparseable run charges its wall time, capped at time_limit.
    """
    cpu = res.cpu_time
    if _is_timeout(res):
        return float(time_limit)
    if cpu is None:
        return float(min(res.wall_time or time_limit, time_limit))
    return float(cpu)


# --------------------------------------------------------------------------- #
# Core evaluation
# --------------------------------------------------------------------------- #
def evaluate_detailed(config: dict, problem_set, *,
                      time_limit: float = DEFAULT_TIME_LIMIT, workers: int = 8,
                      uno_bin=None, validate: bool = True) -> dict:
    """Solve `config` over `problem_set`; return metrics + per-problem rows.

    See :func:`evaluate` for the argument meanings. Returns a dict with keys:
    ``reliability``, ``cum_cpu_time``, ``n_problems``, ``n_solved``, ``config``,
    ``time_limit``, ``status_counts``, ``per_problem``.
    """
    config = dict(config or {})
    if validate:
        validate_config(config)

    problems = load_problem_set(problem_set)
    binary = str(uno_bin) if uno_bin is not None else str(bundled_uno_bin())

    def one(nl: Path) -> dict:
        res = run_uno(nl, options=config, uno_bin=binary, time_limit=time_limit)
        return {
            "problem": res.problem,
            "category": _category(res),
            "solved": is_solved(res),
            "cpu_time": _charged_cpu(res, time_limit),
            "objective": res.objective,
            "iterations": res.iterations,
            "optimization_status": res.optimization_status,
            "solution_status": res.solution_status,
        }

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        rows = list(pool.map(one, problems))

    n = len(rows)
    n_solved = sum(r["solved"] for r in rows)
    status_counts: dict[str, int] = {}
    for r in rows:
        status_counts[r["category"]] = status_counts.get(r["category"], 0) + 1

    return {
        "config": config,
        "time_limit": time_limit,
        "n_problems": n,
        "n_solved": n_solved,
        "reliability": n_solved / n if n else 0.0,
        "cum_cpu_time": sum(r["cpu_time"] for r in rows),
        "status_counts": status_counts,
        "per_problem": rows,
    }


def evaluate(config: dict, problem_set, *, time_limit: float = DEFAULT_TIME_LIMIT,
             workers: int = 8, uno_bin=None, validate: bool = True) -> tuple[float, float]:
    """Score one UNO config over a problem set -> ``(reliability, cum_cpu_time)``.

    config       dict of ingredient options (a subset of uno_search_space.json);
                 unspecified ingredients fall back to UNO's own defaults.
    problem_set  path to a problem-set JSON, or a list of .nl paths (see
                 :func:`load_problem_set`).
    time_limit   per-problem UNO time budget in seconds (default 20). A problem that
                 hits it is unsolved and charged the full budget.
    workers      concurrent solves (default 8). Does not affect the returned numbers --
                 cum_cpu_time is a sum of per-problem CPU times, not wall-clock.
    uno_bin      path to uno_ampl; defaults to the bundled build for reproducibility.
    validate     if True, reject unknown keys / illegal values (ValueError).

    Returns
        (reliability in [0, 1], cumulative UNO CPU seconds).
    """
    out = evaluate_detailed(config, problem_set, time_limit=time_limit,
                            workers=workers, uno_bin=uno_bin, validate=validate)
    return out["reliability"], out["cum_cpu_time"]


def make_objective(problem_set, *, time_limit: float = DEFAULT_TIME_LIMIT,
                   workers: int = 8, uno_bin=None, validate: bool = True):
    """Build a black-box objective ``config -> (reliability, cum_cpu_time)``.

    The problem set is resolved once, up front, so the returned callable only pays for
    solving. Hand it to an external optimizer's loop::

        f = make_objective("problems/sets/hs_model_all.json", time_limit=20)
        reliability, cpu = f({"globalization_mechanism": "LS"})

    Scalarization (how to trade reliability against CPU time) is left to the caller,
    since the objective is genuinely bi-objective.
    """
    problems = load_problem_set(problem_set)   # resolve + existence-check once

    def objective(config: dict) -> tuple[float, float]:
        return evaluate(config, problems, time_limit=time_limit, workers=workers,
                        uno_bin=uno_bin, validate=validate)

    return objective


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _parse_options(option_list, options_csv) -> dict:
    """Merge repeated --option KEY=VALUE and a --options "k=v,k=v" string into a dict."""
    items = list(option_list or [])
    if options_csv:
        items += [tok for tok in options_csv.split(",") if tok.strip()]
    opts = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"option must be key=value, got: {item!r}")
        key, value = item.split("=", 1)
        opts[key.strip()] = value.strip()
    return opts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Score one UNO config over a problem set; print reliability "
                    "(fraction solved) and cumulative UNO CPU time.")
    ap.add_argument("--problems", required=True, metavar="SET.json",
                    help="problem-set JSON (array of entries, or {problems, base_dir})")
    ap.add_argument("--option", action="append", metavar="KEY=VALUE", default=[],
                    help="ingredient option (repeatable), e.g. globalization_mechanism=LS")
    ap.add_argument("--options", default=None, metavar="K1=V1,K2=V2",
                    help="comma-separated options (merged with --option)")
    ap.add_argument("--time-limit", type=float, default=DEFAULT_TIME_LIMIT,
                    help=f"per-problem UNO time budget in seconds (default {DEFAULT_TIME_LIMIT})")
    ap.add_argument("--workers", type=int, default=8,
                    help="concurrent solves (default 8; does not affect the metrics)")
    ap.add_argument("--uno-bin", default=None,
                    help="path to uno_ampl (default: the bundled build)")
    ap.add_argument("--no-validate", action="store_true",
                    help="skip config validation against the search space")
    ap.add_argument("--json", action="store_true", help="print the result as JSON")
    args = ap.parse_args(argv)

    try:
        config = _parse_options(args.option, args.options)
        out = evaluate_detailed(
            config, args.problems, time_limit=args.time_limit, workers=args.workers,
            uno_bin=args.uno_bin, validate=not args.no_validate)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        out.pop("per_problem", None)
        print(json.dumps(out, indent=2))
    else:
        print(f"problems     : {out['n_problems']} (from {args.problems})")
        print(f"config       : {config if config else '(UNO defaults)'}")
        print(f"reliability  : {out['reliability']:.4f}  "
              f"({out['n_solved']}/{out['n_problems']} solved)")
        print(f"cum_cpu_time : {out['cum_cpu_time']:.4f} s")
        print(f"status_counts: {out['status_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
