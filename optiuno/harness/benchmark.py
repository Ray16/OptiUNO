"""Evaluate one UNO configuration over the whole HS test set.

Metrics (the two competing objectives of the OptiUNO search):
  reliability   -- fraction of test problems solved (Feasible KKT point)
  cum_cpu_time  -- cumulative UNO-reported CPU seconds over all problems;
                   an unsolved/crashed run contributes its consumed time,
                   a timeout contributes the full time limit.

Results are cached by configuration hash: only ~240 distinct six-ingredient
combinations exist, so evolution and later enumeration share evaluations.
"""
from __future__ import annotations

import csv
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# This module is a submodule of the top-level `optiuno` package (never run
# standalone), so it reaches the UNO driver and its siblings via relative imports.
from ..uno_runner import DEFAULT_TIME_LIMIT, run_uno
from ..utils import bundled_uno_bin

from .classify import classify

# optiuno/harness/benchmark.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
NL_DIR = REPO_ROOT / "problems" / "HS_model"                       # HS test set at the repo root
CACHE_DIR = REPO_ROOT / "results" / "quickRun" / "cache"
LOG_ROOT = REPO_ROOT / "results" / "quickRun" / "openevolve_run" / "logs"
EVAL_CSV = REPO_ROOT / "results" / "quickRun" / "openevolve_run" / "evaluations.csv"
# Pinned to the bundled self-contained build (now at the repo root, external/uno)
# for reproducible benchmark results, sourced from the single UNO-location helper.
UNO_BIN = bundled_uno_bin()

DEFAULT_WORKERS = 8


def test_problems() -> list[Path]:
    return sorted(NL_DIR.glob("*.nl"))


def config_hash(options: dict, time_limit: float) -> str:
    payload = json.dumps({"options": options, "time_limit": time_limit},
                         sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()[:12]


def evaluate_config(options: dict, time_limit: float = DEFAULT_TIME_LIMIT,
                    workers: int = DEFAULT_WORKERS, use_cache: bool = True,
                    label: str | None = None, rep: int = 0) -> dict:
    """Run `options` on every test problem; return metrics + per-problem rows."""
    problems = test_problems()
    if not problems:
        raise RuntimeError(f"no .nl files under {NL_DIR}")

    chash = config_hash(options, time_limit)
    cache_key = f"{chash}_r{rep}"
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if use_cache and cache_file.exists():
        return json.loads(cache_file.read_text())

    log_dir = LOG_ROOT / cache_key

    def one(nl: Path) -> dict:
        res = run_uno(nl, options=options, uno_bin=UNO_BIN, time_limit=time_limit,
                      log_path=log_dir / f"{nl.stem}.log")
        cls = classify(res)
        cpu = res.cpu_time
        if cls["category"] == "timeout" or cpu is None:
            cpu = time_limit if cls["category"] == "timeout" else min(
                res.wall_time or time_limit, time_limit)
        return {
            "problem": res.problem,
            "category": cls["category"],
            "rewritten": cls["rewritten"],
            "detail": cls["detail"],
            "objective": res.objective,
            "iterations": res.iterations,
            "objective_evaluations": res.objective_evals,
            "cpu_time": float(cpu),
        }

    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(one, problems))

    n = len(rows)
    n_solved = sum(r["category"] == "solved" for r in rows)
    status_counts: dict[str, int] = {}
    for r in rows:
        status_counts[r["category"]] = status_counts.get(r["category"], 0) + 1
    n_rewritten = sum(bool(r["rewritten"]) for r in rows)

    out = {
        "config_hash": chash,
        "rep": rep,
        "label": label or chash,
        "options": dict(options),
        "time_limit": time_limit,
        "n_problems": n,
        "n_solved": n_solved,
        "reliability": n_solved / n,
        "cum_cpu_time": sum(r["cpu_time"] for r in rows),
        "n_rewritten": n_rewritten,
        "status_counts": status_counts,
        "per_problem": rows,
    }

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(out, indent=1))
    _append_eval_row(out)
    return out


def _append_eval_row(out: dict) -> None:
    EVAL_CSV.parent.mkdir(parents=True, exist_ok=True)
    new = not EVAL_CSV.exists()
    with open(EVAL_CSV, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["config_hash", "rep", "label", "options_json",
                        "n_problems", "n_solved", "reliability",
                        "cum_cpu_time", "n_rewritten", "status_counts_json"])
        w.writerow([out["config_hash"], out["rep"], out["label"],
                    json.dumps(out["options"], sort_keys=True),
                    out["n_problems"], out["n_solved"],
                    f"{out['reliability']:.6f}", f"{out['cum_cpu_time']:.4f}",
                    out["n_rewritten"], json.dumps(out["status_counts"])])
