#!/usr/bin/env python3
"""Pareto-front figures for the OptiUNO search.

  results/pareto_evolution.png  front after successive evolution steps,
                                color-graded by evaluation index
  results/pareto_final.png      final front vs. the preset baselines,
                                with variance error bars when available

Data sources: results/evolution_history.csv (one row per openEvolve
evaluation, in order) and results/variance.json (optional error bars).
Objectives: maximize reliability, minimize cumulative CPU time. A point is
non-dominated if no other point has both >= reliability and <= time (one
strictly better).
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "results" / "evolution_history.csv"
VARIANCE = ROOT / "results" / "variance.json"
FRONT_JSON = ROOT / "results" / "front_configs.json"


def load_history() -> list[dict]:
    rows = []
    with open(HISTORY) as fh:
        for row in csv.DictReader(fh):
            if int(row["valid"]):
                rows.append({
                    "config": json.loads(row["config_json"]),
                    "reliability": float(row["reliability"]),
                    "time": float(row["cum_cpu_time"]),
                })
    return rows


def pareto_front(points: list[dict]) -> list[dict]:
    front = []
    for p in points:
        dominated = any(
            (q["reliability"] >= p["reliability"] and q["time"] <= p["time"])
            and (q["reliability"] > p["reliability"] or q["time"] < p["time"])
            for q in points)
        if not dominated:
            front.append(p)
    # unique by objectives, sorted by time
    seen, uniq = set(), []
    for p in sorted(front, key=lambda r: (r["time"], -r["reliability"])):
        key = (round(p["time"], 4), round(p["reliability"], 6))
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


def baselines() -> dict:
    """Preset reference points (mean over variance reps when available)."""
    out = {}
    if VARIANCE.exists():
        for label, rec in json.loads(VARIANCE.read_text()).items():
            if label.startswith("preset-"):
                t = rec["cum_cpu_times"]
                out[label.replace("preset-", "")] = {
                    "reliability": rec["reliabilities"][0],
                    "time": sum(t) / len(t),
                    "sd": float(np.std(t, ddof=1)) if len(t) > 1 else 0.0,
                }
    return out


def plot_evolution(rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(8, 5.5))
    n = len(rows)
    checkpoints = sorted({max(1, round(n * f)) for f in
                          (0.1, 0.25, 0.5, 0.75, 1.0)})
    cmap = plt.get_cmap("viridis")
    for i, k in enumerate(checkpoints):
        front = pareto_front(rows[:k])
        xs = [p["time"] for p in front]
        ys = [p["reliability"] for p in front]
        ax.step(xs, ys, where="post", marker="o", ms=4,
                color=cmap(i / max(1, len(checkpoints) - 1)),
                label=f"after {k} evaluations")
    _add_baselines(ax)
    ax.set_xlabel("cumulative CPU time over test set (s)")
    ax.set_ylabel("reliability (fraction of problems solved)")
    ax.set_title("Pareto front over openEvolve evaluations")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ROOT / "results" / "pareto_evolution.png", dpi=150)
    print("wrote results/pareto_evolution.png")


def plot_final(rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter([p["time"] for p in rows], [p["reliability"] for p in rows],
               s=12, c="lightgray", label="all evaluated configs", zorder=1)
    front = pareto_front(rows)
    xs = [p["time"] for p in front]
    ys = [p["reliability"] for p in front]
    ax.step(xs, ys, where="post", color="tab:blue", zorder=2)
    ax.scatter(xs, ys, s=45, c="tab:blue", label="final Pareto front", zorder=3)
    _add_baselines(ax, error_bars=True)
    ax.set_xscale("log")  # evaluated configs span ~0.5s to ~200s
    ax.set_xlabel("cumulative CPU time over test set (s, log scale)")
    ax.set_ylabel("reliability (fraction of problems solved)")
    ax.set_title("Final Pareto front vs. UNO presets (123 HS problems)")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ROOT / "results" / "pareto_final.png", dpi=150)
    print("wrote results/pareto_final.png")

    FRONT_JSON.write_text(json.dumps([p["config"] for p in front], indent=1))
    print(f"wrote {FRONT_JSON} ({len(front)} configs)")


def _add_baselines(ax, error_bars: bool = False) -> None:
    marks = {"filtersqp": ("tab:red", "s"), "ipopt": ("tab:orange", "D")}
    for name, ref in baselines().items():
        color, marker = marks.get(name, ("k", "x"))
        if error_bars and ref.get("sd"):
            ax.errorbar(ref["time"], ref["reliability"], xerr=ref["sd"],
                        fmt=marker, color=color, ms=8, capsize=4,
                        label=f"preset {name}", zorder=4)
        else:
            ax.scatter([ref["time"]], [ref["reliability"]], marker=marker,
                       c=color, s=70, label=f"preset {name}", zorder=4)


def main() -> None:
    if not HISTORY.exists():
        sys.exit(f"{HISTORY} not found - run the evolution first "
                 "(scripts/run_evolution.py)")
    rows = load_history()
    if not rows:
        sys.exit("no valid evaluations in history yet")
    plot_evolution(rows)
    plot_final(rows)


if __name__ == "__main__":
    main()
