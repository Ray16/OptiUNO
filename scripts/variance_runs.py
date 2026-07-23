#!/usr/bin/env python3
"""Repeated benchmark sweeps to estimate CPU-time noise.

Runs each reference configuration R times (cache keyed by rep) and reports
mean, empirical variance, and standard deviation of the cumulative CPU time.
Reliability is checked for stability across reps as a sanity condition.

Usage: scripts/variance_runs.py [--reps 10] [--fronts results/front_configs.json]
The optional JSON file adds evolved front configurations (list of option
dicts, e.g. dumped after the evolution run) to the reference set.
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from optiuno.harness.benchmark import evaluate_config  # noqa: E402
from run_evolution import PRESET_INGREDIENTS  # noqa: E402  (sibling in scripts/)

RUN_DIR = REPO_ROOT / "results" / "quickRun" / "openevolve_run"
OUT = RUN_DIR / "variance.md"
OUT_JSON = RUN_DIR / "variance.json"


def reference_configs(fronts_file: str | None) -> dict:
    configs = {
        "preset-filtersqp": {"preset": "filtersqp"},
        "preset-ipopt": {"preset": "ipopt"},
        "ingredients-filtersqp": PRESET_INGREDIENTS["filtersqp"],
        "ingredients-ipopt": PRESET_INGREDIENTS["ipopt"],
    }
    if fronts_file:
        for i, cfg in enumerate(json.loads(Path(fronts_file).read_text())):
            configs[f"front-{i}"] = cfg
    return configs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--fronts", default=None)
    args = ap.parse_args()

    rows, raw = [], {}
    for label, cfg in reference_configs(args.fronts).items():
        times, rels = [], []
        for rep in range(args.reps):
            out = evaluate_config(cfg, label=f"var-{label}", rep=rep)
            times.append(out["cum_cpu_time"])
            rels.append(out["reliability"])
        mean = statistics.mean(times)
        var = statistics.variance(times) if len(times) > 1 else 0.0
        rows.append((label, min(rels), max(rels), mean, var,
                     statistics.stdev(times) if len(times) > 1 else 0.0,
                     min(times), max(times)))
        raw[label] = {"config": cfg, "cum_cpu_times": times,
                      "reliabilities": rels}
        print(f"{label:24s} rel=[{min(rels):.3f},{max(rels):.3f}] "
              f"time mean={mean:.3f}s var={var:.5f} sd={statistics.stdev(times):.3f}s")

    lines = [
        "# Empirical variance of cumulative CPU time",
        "",
        f"R = {args.reps} repetitions of the full {123}-problem sweep per "
        "configuration. CPU time is UNO's self-reported process CPU time, "
        "summed over the test set.",
        "",
        "| Configuration | Reliability (min-max) | Mean time (s) | "
        "Variance (s^2) | Std dev (s) | Min (s) | Max (s) |",
        "|---|---|---|---|---|---|---|",
    ]
    for label, rmin, rmax, mean, var, sd, tmin, tmax in rows:
        lines.append(f"| {label} | {rmin:.3f}-{rmax:.3f} | {mean:.3f} | "
                     f"{var:.5f} | {sd:.3f} | {tmin:.3f} | {tmax:.3f} |")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    OUT_JSON.write_text(json.dumps(raw, indent=1))
    print(f"wrote {OUT} and {OUT_JSON}")


if __name__ == "__main__":
    main()
