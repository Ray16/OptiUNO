#!/usr/bin/env python3
"""Genetic-algorithm (NSGA-II) search for the best UNO configuration.

Searches the six-ingredient categorical space in ``optiuno/uno_search_space.json``
over a problem set (default ``problems/sets/hs_model_all.json``), scoring each
configuration with the decoupled black-box objective ``optiuno.objective`` -- the
two competing objectives are **reliability** (fraction of problems that reach an
optimal solution, maximized) and **cumulative UNO CPU time** (minimized). The GA
is **not** hand-coded: it uses `pymoo <https://pymoo.org>`_'s NSGA-II for
categorical variables (`Choice` + `MixedVariableGA` + `RankAndCrowdingSurvival`),
which returns a Pareto front directly.

Outputs mimic the openEvolve ``results/quickRun/`` artifacts, written to a
timestamped folder ``results/ga_<set-name>/<YYYYmmdd_HHMMSS>/``:

  evaluations.csv     one row per distinct config evaluated (baselines + GA)
  ga_history.csv      one row per evaluation call, in order, tagged by generation
  front_configs.json  the Pareto-front config dicts (drop-in for front tooling)
  pareto_front.csv    each front config's ingredients + reliability/time/score
  pareto_final.png    all evaluated configs + final front + UNO presets (log x)
  pareto_evolution.png the front snapshot at each GA generation
  RESULTS.md          narrative summary: baselines, front, best config, coverage

Run it with an interpreter that has pymoo + numpy + matplotlib, e.g.::

    /home/sdinh/anaconda3/bin/python scripts/ga_search.py [--generations N] ...

The UNO solver is invoked only through the shared ``optiuno`` library (bundled
binary, read-only); nothing in UNO is modified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Repo root on sys.path so `optiuno` imports whatever interpreter runs this.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# --- pymoo (fail fast with the install command if missing) ------------------ #
try:
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.core.variable import Choice
    from pymoo.core.mixed import MixedVariableGA
    from pymoo.algorithms.moo.nsga2 import RankAndCrowdingSurvival
    from pymoo.core.callback import Callback
    from pymoo.optimize import minimize
except ImportError as exc:  # noqa: BLE001
    sys.exit(
        "pymoo is required for this script but is not installed.\n"
        "Install it (into the interpreter you run this with), e.g.:\n"
        '    "/home/sdinh/anaconda3/bin/python" -m pip install pymoo\n'
        f"(import error: {exc})")

import numpy as np
import matplotlib
matplotlib.use("Agg")            # headless: write PNGs, never open a window
import matplotlib.pyplot as plt  # noqa: E402

from optiuno.objective import evaluate_detailed  # noqa: E402
from optiuno.uno_runner import DEFAULT_TIME_LIMIT  # noqa: E402

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
DEFAULT_SEARCH_SPACE = REPO_ROOT / "optiuno" / "uno_search_space.json"
DEFAULT_PROBLEM_SET = REPO_ROOT / "problems" / "sets" / "hs_model_all.json"

TIME_SCALE = 60.0  # CPU-time normalization for the scalar score (as in quickRun)

# The two UNO presets, as explicit six-ingredient configs, used as reference
# points (identical to quickRun/scripts/run_evolution.py:PRESET_INGREDIENTS).
PRESET_INGREDIENTS = {
    "filtersqp": {
        "constraint_relaxation_strategy": "feasibility_restoration",
        "inequality_handling_method": "inequality_constrained",
        "hessian_model": "exact",
        "inertia_correction_strategy": "none",
        "globalization_mechanism": "TR",
        "globalization_strategy": "fletcher_filter_method",
    },
    "ipopt": {
        "constraint_relaxation_strategy": "feasibility_restoration",
        "inequality_handling_method": "interior_point",
        "hessian_model": "exact",
        "inertia_correction_strategy": "primal_dual",
        "globalization_mechanism": "LS",
        "globalization_strategy": "waechter_filter_method",
    },
}
PRESET_STYLE = {"filtersqp": ("tab:red", "s"), "ipopt": ("tab:orange", "D")}


# --------------------------------------------------------------------------- #
# Scoring / hashing (kept identical to the quickRun definitions)
# --------------------------------------------------------------------------- #
def combined_score(reliability: float, cum_cpu_time: float) -> float:
    """Reliability dominates; faster cumulative CPU time breaks ties."""
    return reliability + 0.1 * max(0.0, 1.0 - cum_cpu_time / TIME_SCALE)


def config_hash(options: dict, time_limit: float) -> str:
    payload = json.dumps({"options": options, "time_limit": time_limit},
                         sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()[:12]


def pareto_front(points: list[dict]) -> list[dict]:
    """Non-dominated set: maximize reliability, minimize cum_cpu_time.

    `points` are dicts with keys 'reliability' and 'cum_cpu_time'. Returns the
    front deduped by (round(time,4), round(reliability,6)), sorted by time.
    """
    front = []
    for p in points:
        dominated = any(
            q is not p
            and q["reliability"] >= p["reliability"]
            and q["cum_cpu_time"] <= p["cum_cpu_time"]
            and (q["reliability"] > p["reliability"]
                 or q["cum_cpu_time"] < p["cum_cpu_time"])
            for q in points)
        if not dominated:
            front.append(p)
    seen, deduped = set(), []
    for p in sorted(front, key=lambda r: (r["cum_cpu_time"], -r["reliability"])):
        key = (round(p["cum_cpu_time"], 4), round(p["reliability"], 6))
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped


# --------------------------------------------------------------------------- #
# Evaluation with a cache + CSV logging
# --------------------------------------------------------------------------- #
class Evaluator:
    """Wraps optiuno.objective with a config cache and the two CSV logs.

    * `evaluations.csv` gets one row per DISTINCT config (on a cache miss).
    * `ga_history.csv` gets one row per call (hit or miss), tagged by generation.
    Mirrors the quickRun split (distinct configs vs. every evaluation).
    """

    def __init__(self, problems, time_limit, workers, out_dir):
        self.problems = problems
        self.time_limit = time_limit
        self.workers = workers
        self.cache: dict[tuple, dict] = {}
        self.gen = 0  # bumped by the GA callback; baselines are logged as gen 0

        self._eval_fh = open(out_dir / "evaluations.csv", "w", newline="")
        self._eval = csv.writer(self._eval_fh)
        self._eval.writerow([
            "config_hash", "label", "options_json", "n_problems", "n_solved",
            "reliability", "cum_cpu_time", "combined_score", "status_counts_json"])
        self._hist_fh = open(out_dir / "ga_history.csv", "w", newline="")
        self._hist = csv.writer(self._hist_fh)
        self._hist.writerow([
            "timestamp", "generation", "config_json", "valid", "reliability",
            "cum_cpu_time", "combined_score", "n_solved", "status_counts_json"])

    def evaluate(self, config: dict, label: str) -> dict:
        key = tuple(sorted(config.items()))
        rec = self.cache.get(key)
        if rec is None:
            det = evaluate_detailed(config, self.problems,
                                    time_limit=self.time_limit,
                                    workers=self.workers, validate=True)
            rec = {
                "config_hash": config_hash(config, self.time_limit),
                "label": label,
                "options": dict(config),
                "n_problems": det["n_problems"],
                "n_solved": det["n_solved"],
                "reliability": det["reliability"],
                "cum_cpu_time": det["cum_cpu_time"],
                "combined_score": combined_score(det["reliability"],
                                                 det["cum_cpu_time"]),
                "status_counts": det["status_counts"],
            }
            self.cache[key] = rec
            self._eval.writerow([
                rec["config_hash"], rec["label"],
                json.dumps(rec["options"], sort_keys=True),
                rec["n_problems"], rec["n_solved"],
                f"{rec['reliability']:.6f}", f"{rec['cum_cpu_time']:.4f}",
                f"{rec['combined_score']:.6f}",
                json.dumps(rec["status_counts"])])
            self._eval_fh.flush()

        self._hist.writerow([
            f"{time.time():.3f}", self.gen,
            json.dumps(config, sort_keys=True), 1,
            f"{rec['reliability']:.6f}", f"{rec['cum_cpu_time']:.4f}",
            f"{rec['combined_score']:.6f}", rec["n_solved"],
            json.dumps(rec["status_counts"])])
        self._hist_fh.flush()
        return rec

    def close(self):
        self._eval_fh.close()
        self._hist_fh.close()


# --------------------------------------------------------------------------- #
# pymoo problem + callback
# --------------------------------------------------------------------------- #
class UnoProblem(ElementwiseProblem):
    """Bi-objective categorical problem: minimize [1 - reliability, cum_cpu_time]."""

    def __init__(self, search_space: dict, evaluator: Evaluator):
        self._keys = list(search_space)          # preserve JSON order
        self._evaluator = evaluator
        variables = {k: Choice(options=list(v)) for k, v in search_space.items()}
        super().__init__(vars=variables, n_obj=2, n_ieq_constr=0)

    def _evaluate(self, X, out, *args, **kwargs):
        config = {k: X[k] for k in self._keys}
        rec = self._evaluator.evaluate(config, label="ga")
        out["F"] = [1.0 - rec["reliability"], rec["cum_cpu_time"]]


class FrontSnapshot(Callback):
    """Record the non-dominated set after each generation (and log progress)."""

    def __init__(self, log=True):
        super().__init__()
        self.snapshots: list[tuple[int, list[tuple[float, float]]]] = []
        self.log = log

    def notify(self, algorithm):
        gen = int(algorithm.n_gen)
        F = algorithm.opt.get("F")               # [[1-rel, cpu], ...]
        pts = [(float(cpu), 1.0 - float(inv_rel)) for inv_rel, cpu in F]
        self.snapshots.append((gen, pts))
        ev = algorithm.problem._evaluator
        ev.gen = gen                             # tag the next generation's evals
        if self.log:
            best_rel, best_cpu = max(((r, c) for c, r in pts), key=lambda t: t[0])
            n_eval = getattr(algorithm.evaluator, "n_eval", "?")
            print(f"  gen {gen:>3}  evals={n_eval:<5} distinct={len(ev.cache):<4} "
                  f"front={len(pts):<3} best_reliability={best_rel:.4f} "
                  f"@ {best_cpu:.2f}s", flush=True)


# --------------------------------------------------------------------------- #
# Plots (styled to match quickRun/scripts/plot_pareto.py)
# --------------------------------------------------------------------------- #
def _add_presets(ax, presets: dict):
    for name, rec in presets.items():
        color, marker = PRESET_STYLE.get(name, ("k", "x"))
        ax.scatter([rec["cum_cpu_time"]], [rec["reliability"]], marker=marker,
                   c=color, s=70, label=f"preset {name}", zorder=4)


def plot_final(path, all_points, front, presets, n_problems):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter([p["cum_cpu_time"] for p in all_points],
               [p["reliability"] for p in all_points],
               s=12, c="lightgray", label="all evaluated configs", zorder=1)
    xs = [p["cum_cpu_time"] for p in front]
    ys = [p["reliability"] for p in front]
    ax.step(xs, ys, where="post", color="tab:blue", zorder=2)
    ax.scatter(xs, ys, s=45, c="tab:blue", label="final Pareto front", zorder=3)
    _add_presets(ax, presets)
    ax.set_xscale("log")
    ax.set_xlabel("cumulative CPU time over test set (s, log scale)")
    ax.set_ylabel("reliability (fraction of problems solved)")
    ax.set_title(f"Final Pareto front vs. UNO presets ({n_problems} HS problems, NSGA-II)")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_evolution(path, snapshots, presets):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    # thin to at most ~6 evenly-spaced generations to avoid clutter
    if len(snapshots) > 6:
        idx = np.linspace(0, len(snapshots) - 1, 6).round().astype(int)
        snaps = [snapshots[i] for i in sorted(set(idx))]
    else:
        snaps = snapshots
    colors = plt.cm.viridis(np.linspace(0, 1, len(snaps)))
    for (gen, pts), color in zip(snaps, colors):
        pts = sorted(pts, key=lambda t: t[0])       # by cpu
        xs = [c for c, _ in pts]
        ys = [r for _, r in pts]
        ax.step(xs, ys, where="post", marker="o", ms=4, color=color,
                label=f"after gen {gen}")
    _add_presets(ax, presets)
    ax.set_xlabel("cumulative CPU time over test set (s)")
    ax.set_ylabel("reliability (fraction of problems solved)")
    ax.set_title("Pareto front over GA generations")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# RESULTS.md
# --------------------------------------------------------------------------- #
def _md_table(headers, rows) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def write_results_md(path, *, keys, presets, front, best, all_recs, n_problems,
                     problem_set, pop_size, generations, seed, time_limit,
                     pymoo_version, timestamp, space_size):
    ncols = keys + ["reliability", "cum_cpu_time", "combined_score"]

    def cfg_row(rec):
        return ([rec["options"][k] for k in keys]
                + [f"{rec['reliability']:.4f}", f"{rec['cum_cpu_time']:.3f}",
                   f"{rec['combined_score']:.4f}"])

    preset_rows = [
        [name] + [f"{r['reliability']:.4f}", f"{r['cum_cpu_time']:.3f}",
                  f"{r['combined_score']:.4f}"]
        for name, r in presets.items()]

    best_vs = []
    for name, r in presets.items():
        best_vs.append(
            f"- vs **{name}**: reliability {best['reliability']:.4f} vs "
            f"{r['reliability']:.4f}  ·  CPU {best['cum_cpu_time']:.3f}s vs "
            f"{r['cum_cpu_time']:.3f}s  ·  score {best['combined_score']:.4f} vs "
            f"{r['combined_score']:.4f}")

    text = f"""# GA (NSGA-II) search results — {problem_set}

_Generated {timestamp} by `scripts/ga_search.py` (pymoo {pymoo_version})._

## Setup

- **Search space:** the six UNO ingredients from `optiuno/uno_search_space.json`
  ({space_size} nominal combinations).
- **Problem set:** `{problem_set}` — {n_problems} HS `.nl` problems.
- **Objective (bi-objective):** maximize reliability (fraction reaching a Feasible
  KKT point), minimize cumulative UNO CPU time. Scalar tiebreak
  `combined_score = reliability + 0.1·max(0, 1 − cum_cpu_time/{TIME_SCALE:.0f})`.
- **Optimizer:** pymoo NSGA-II (`MixedVariableGA` + `RankAndCrowdingSurvival`),
  pop_size={pop_size}, generations={generations}, seed={seed}.
- **Per-problem budget:** time_limit={time_limit}s. **UNO binary:** bundled
  `external/uno` build (pinned via `optiuno`).

## Preset baselines

{_md_table(["preset", "reliability", "cum_cpu_time (s)", "combined_score"], preset_rows)}

## Best configuration found (max combined_score)

{_md_table(ncols, [cfg_row(best)])}

{chr(10).join(best_vs)}

## Pareto front ({len(front)} non-dominated configs)

{_md_table(ncols, [cfg_row(p) for p in front])}

Full front configs also in `front_configs.json` / `pareto_front.csv`; plots in
`pareto_final.png` (vs. presets, log time axis) and `pareto_evolution.png`.

## Search coverage

- Distinct configs evaluated: **{len(all_recs)}** of {space_size} nominal
  (the config cache makes re-proposed configs free).
- Generations: {generations}, population {pop_size}.

## Notes

- CPU time carries ~5–15% run-to-run noise; reliability is noise-free. Front
  points within a fraction of a second are statistically indistinguishable.
- Silent-rewrite detection (UNO running a different config than requested on
  unconstrained/bound-only problems) is a quickRun-harness feature and is **not**
  tracked by the decoupled `optiuno.objective` evaluator used here.
- The space is small ({space_size} points); a complete enumeration + non-dominated
  filter is a feasible exact alternative / ground-truth check.
"""
    path.write_text(text)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--problems", default=str(DEFAULT_PROBLEM_SET),
                    help="problem-set JSON (default: problems/sets/hs_model_all.json)")
    ap.add_argument("--search-space", default=str(DEFAULT_SEARCH_SPACE),
                    help="search-space JSON (default: optiuno/uno_search_space.json)")
    ap.add_argument("--pop-size", type=int, default=24)
    ap.add_argument("--generations", type=int, default=15)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--time-limit", type=float, default=DEFAULT_TIME_LIMIT)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=None,
                    help="output dir (default: results/ga_<set>/<timestamp>/)")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress the per-generation progress line")
    ap.add_argument("--verbose", action="store_true",
                    help="also print pymoo's built-in per-generation table")
    args = ap.parse_args(argv)

    search_space = json.loads(Path(args.search_space).read_text())
    keys = list(search_space)
    space_size = int(np.prod([len(v) for v in search_space.values()]))

    ps_path = Path(args.problems)
    try:
        set_name = json.loads(ps_path.read_text()).get("name") or ps_path.stem
    except (json.JSONDecodeError, OSError):
        set_name = ps_path.stem

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out) if args.out else (
        REPO_ROOT / "results" / f"ga_{set_name}" / timestamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"output dir: {out_dir}")

    evaluator = Evaluator(args.problems, args.time_limit, args.workers, out_dir)

    # 1) Baselines first (so every plot has reference points), logged as gen 0.
    print("Evaluating preset baselines ...", flush=True)
    presets = {}
    for name, ingredients in PRESET_INGREDIENTS.items():
        rec = evaluator.evaluate(ingredients, label=f"baseline-{name}")
        presets[name] = rec
        print(f"  {name:10s} reliability={rec['reliability']:.4f} "
              f"cumCPU={rec['cum_cpu_time']:.3f}s score={rec['combined_score']:.4f}",
              flush=True)

    # 2) Run NSGA-II over the categorical space.
    print(f"Running NSGA-II: pop={args.pop_size} gens={args.generations} "
          f"seed={args.seed} (one line per generation below) ...", flush=True)
    problem = UnoProblem(search_space, evaluator)
    algorithm = MixedVariableGA(pop_size=args.pop_size,
                                survival=RankAndCrowdingSurvival())
    snapshot = FrontSnapshot(log=not args.quiet)
    minimize(problem, algorithm, ("n_gen", args.generations), seed=args.seed,
             callback=snapshot, verbose=args.verbose)

    # 3) Final front over ALL distinct evaluated configs (incl. baselines).
    all_recs = list(evaluator.cache.values())
    front = pareto_front(all_recs)
    best = max(all_recs, key=lambda r: r["combined_score"])
    evaluator.close()

    # 4) Artifacts.
    (out_dir / "front_configs.json").write_text(
        json.dumps([p["options"] for p in front], indent=1))

    with open(out_dir / "pareto_front.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(keys + ["reliability", "cum_cpu_time", "combined_score"])
        for p in front:
            w.writerow([p["options"][k] for k in keys]
                       + [f"{p['reliability']:.6f}", f"{p['cum_cpu_time']:.4f}",
                          f"{p['combined_score']:.6f}"])

    plot_final(out_dir / "pareto_final.png", all_recs, front, presets,
               best["n_problems"])
    plot_evolution(out_dir / "pareto_evolution.png", snapshot.snapshots, presets)

    write_results_md(
        out_dir / "RESULTS.md", keys=keys, presets=presets, front=front, best=best,
        all_recs=all_recs, n_problems=best["n_problems"], problem_set=set_name,
        pop_size=args.pop_size, generations=args.generations, seed=args.seed,
        time_limit=args.time_limit, pymoo_version=_pymoo_version(),
        timestamp=timestamp, space_size=space_size)

    # 5) Console summary.
    print(f"\nDistinct configs evaluated: {len(all_recs)} / {space_size} nominal")
    print(f"Pareto front size: {len(front)}")
    print("Best config (max combined_score):")
    for k in keys:
        print(f"    {k} = {best['options'][k]}")
    print(f"  reliability={best['reliability']:.4f} "
          f"cumCPU={best['cum_cpu_time']:.3f}s score={best['combined_score']:.4f}")
    print(f"\nWrote results to: {out_dir}")
    return 0


def _pymoo_version() -> str:
    import pymoo
    return getattr(pymoo, "__version__", "unknown")


if __name__ == "__main__":
    raise SystemExit(main())
