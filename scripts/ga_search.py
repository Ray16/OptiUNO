#!/usr/bin/env python3
"""Genetic-algorithm (NSGA-II) search for the best UNO configuration.

Searches the six-ingredient categorical space in ``optiuno/uno_search_space.json``
over a problem set (default ``problems/sets/hs_model_all.json``), scoring each
configuration with the decoupled black-box objective ``optiuno.objective`` -- the
two competing objectives are **reliability** (fraction of problems that reach an
optimal solution, maximized) and **cumulative UNO time** (minimized). By default
the time is the real "tic-toc" wall clock measured around each ``uno_ampl``
subprocess (``--time-source wall``; pass ``cpu`` for UNO's self-reported CPU
seconds instead). The GA is **not** hand-coded: it uses
`pymoo <https://pymoo.org>`_'s NSGA-II for categorical variables (`Choice` +
`MixedVariableGA` + `RankAndCrowdingSurvival`), which returns a Pareto front
directly.

Solves run **serially by default** (``--workers 1``) so the summed UNO tic-toc time
is comparable to the run's wall clock; this lets the run report the **GA overhead**
= run wall clock − time spent inside UNO (see ``timing.json`` / RESULTS.md).

Outputs mimic the openEvolve ``results/quickRun/`` artifacts, written to a
timestamped folder
``results/ga_pop_<pop-size>_gen_<generations>_<set-name>/<YYYYmmdd_HHMMSS>/``:

  evaluations.csv     one row per distinct config evaluated (baselines + GA)
  ga_history.csv      one row per evaluation call, in order, tagged by generation
  front_configs.json  the Pareto-front config dicts (drop-in for front tooling)
  pareto_front.csv    each front config's ingredients + reliability/time/score

Every results CSV leads with a ``preset`` column: the name of the UNO built-in
preset whose six ingredients the row's config matches (``filtersqp``, ``ipopt``,
``funnelsqp``, or ``filterslp``), or ``custom`` if it matches none. All four
presets are also evaluated as baselines (as six-ingredient configs).
  pareto_final.png    all evaluated configs + final front + UNO presets (log x)
  pareto_evolution.png the front snapshot at each GA generation
  timing.json         run wall clock, summed UNO time, and the GA overhead
  RESULTS.md          narrative summary: baselines, front, best config, timing

Run it with an interpreter that has pymoo + numpy + matplotlib, e.g.::

    /home/sdinh/anaconda3/bin/python scripts/ga_search.py [--generations N] ...

The UNO solver is invoked only through the shared ``optiuno`` library, read-only;
nothing in UNO is modified. The binary is chosen system-first (``--uno-bin`` ->
``$UNO_AMPL_BIN`` -> ``uno_ampl`` on PATH -> bundled ``external/uno``), so an
HSL-enabled build can be selected to use MA27/MA57. Fixed run-time-options that are
not part of the search space (e.g. the linear solver) are passed with ``--option``::

    python scripts/ga_search.py --uno-bin /path/to/uno_ampl --option linear_solver=MA27
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
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
        '    python -m pip install pymoo\n'
        f"(import error: {exc})")

import numpy as np
import matplotlib
matplotlib.use("Agg")            # headless: write PNGs, never open a window
import matplotlib.pyplot as plt  # noqa: E402

from optiuno.objective import evaluate_detailed  # noqa: E402
from optiuno.uno_runner import (  # noqa: E402
    DEFAULT_TIME_LIMIT, resolve_uno_bin, _bundled_env)

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
DEFAULT_SEARCH_SPACE = REPO_ROOT / "optiuno" / "uno_search_space.json"
DEFAULT_PROBLEM_SET = REPO_ROOT / "problems" / "sets" / "hs_model_all.json"

TIME_SCALE = 60.0  # CPU-time normalization for the scalar score (as in quickRun)

# All four UNO built-in presets, as explicit six-ingredient configs, used as
# reference points AND as the vocabulary for the "preset" column (see
# match_preset). The six ingredients here mirror UNO's `Presets::set` bundles
# (uno/options/Presets.cpp); each real preset also sets ~15-30 non-ingredient
# numerics (tolerances, filter/funnel params, TR radius) that this six-ingredient
# view intentionally leaves at UNO defaults -- so a GA config with identical
# ingredients is genuinely the same run and is labelled with the preset name.
# (`filtersqp`/`ipopt` match quickRun/scripts/run_evolution.py:PRESET_INGREDIENTS;
# `funnelsqp`/`filterslp` are the two additional built-ins.)
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
    "funnelsqp": {
        "constraint_relaxation_strategy": "feasibility_restoration",
        "inequality_handling_method": "inequality_constrained",
        "hessian_model": "exact",
        "inertia_correction_strategy": "none",
        "globalization_mechanism": "TR",
        "globalization_strategy": "funnel_method",
    },
    "filterslp": {
        "constraint_relaxation_strategy": "feasibility_restoration",
        "inequality_handling_method": "inequality_constrained",
        "hessian_model": "zero",
        "inertia_correction_strategy": "none",
        "globalization_mechanism": "TR",
        "globalization_strategy": "fletcher_filter_method",
    },
}
PRESET_STYLE = {
    "filtersqp": ("tab:red", "s"),
    "ipopt": ("tab:orange", "D"),
    "funnelsqp": ("tab:purple", "^"),
    "filterslp": ("tab:brown", "v"),
}


def match_preset(options: dict) -> str:
    """Name of the UNO preset whose six ingredients equal ``options`` (compared
    over the six search-space keys only), or ``"custom"`` if none match. This is
    the value of the leading ``preset`` column in every results CSV."""
    for name, ingredients in PRESET_INGREDIENTS.items():
        if all(options.get(k) == v for k, v in ingredients.items()):
            return name
    return "custom"


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

    def __init__(self, problems, time_limit, workers, out_dir, time_source="wall",
                 verbose=True, per_individual=True, uno_bin=None, extra_options=None):
        self.problems = problems
        self.time_limit = time_limit
        self.workers = workers
        self.time_source = time_source
        self.uno_bin = uno_bin            # which uno_ampl to run (None -> bundled)
        self.extra_options = dict(extra_options or {})  # fixed opts, e.g. linear_solver
        self.verbose = verbose            # print anything at all
        self.per_individual = per_individual  # stream one line per population member
        self.cache: dict[tuple, dict] = {}
        self.gen = 0  # bumped by the GA callback AT EACH GENERATION'S END; while a
        # generation is being evaluated it lags by one, so the generation currently
        # being evaluated is `self.gen + 1` (initial population -> gen 1).
        self._live_gen = None  # generation whose header was last printed
        self._ind_idx = 0      # population index within the current live generation
        # Real (tic-toc) wall seconds spent *inside* UNO subprocesses, summed over
        # every cache MISS (a cache hit re-uses a prior solve and calls no UNO).
        # This is the "UNO time" subtracted from the run's wall clock to get the
        # GA overhead; it is only comparable to wall clock when workers == 1.
        self.total_uno_time = 0.0
        self.n_uno_calls = 0  # distinct-config solves actually run (cache misses)

        self._eval_fh = open(out_dir / "evaluations.csv", "w", newline="")
        self._eval = csv.writer(self._eval_fh)
        self._eval.writerow([
            "preset", "config_hash", "label", "options_json", "n_problems",
            "n_solved", "reliability", "cum_cpu_time", "combined_score",
            "status_counts_json"])
        self._hist_fh = open(out_dir / "ga_history.csv", "w", newline="")
        self._hist = csv.writer(self._hist_fh)
        self._hist.writerow([
            "preset", "timestamp", "generation", "config_json", "valid",
            "reliability", "cum_cpu_time", "combined_score", "n_solved",
            "status_counts_json"])

    def evaluate(self, config: dict, label: str) -> dict:
        key = tuple(sorted(config.items()))
        rec = self.cache.get(key)
        hit = rec is not None
        if rec is None:
            call_t0 = time.perf_counter()
            det = evaluate_detailed(config, self.problems,
                                    time_limit=self.time_limit,
                                    workers=self.workers, validate=True,
                                    time_source=self.time_source,
                                    uno_bin=self.uno_bin,
                                    extra_options=self.extra_options)
            eval_wall = time.perf_counter() - call_t0
            # Only cache MISSES actually run UNO -> accumulate real UNO wall time.
            self.total_uno_time += det["cum_wall_time"]
            self.n_uno_calls += 1
            rec = {
                "config_hash": config_hash(config, self.time_limit),
                "label": label,
                "options": dict(config),
                "n_problems": det["n_problems"],
                "n_solved": det["n_solved"],
                "reliability": det["reliability"],
                "cum_cpu_time": det["cum_cpu_time"],
                "cum_wall_time": det["cum_wall_time"],
                "eval_wall": eval_wall,   # measured wall to evaluate this config
                "combined_score": combined_score(det["reliability"],
                                                 det["cum_cpu_time"]),
                "status_counts": det["status_counts"],
            }
            self.cache[key] = rec
            self._eval.writerow([
                match_preset(rec["options"]), rec["config_hash"], rec["label"],
                json.dumps(rec["options"], sort_keys=True),
                rec["n_problems"], rec["n_solved"],
                f"{rec['reliability']:.6f}", f"{rec['cum_cpu_time']:.4f}",
                f"{rec['combined_score']:.6f}",
                json.dumps(rec["status_counts"])])
            self._eval_fh.flush()

        self._hist.writerow([
            match_preset(config), f"{time.time():.3f}", self.gen,
            json.dumps(config, sort_keys=True), 1,
            f"{rec['reliability']:.6f}", f"{rec['cum_cpu_time']:.4f}",
            f"{rec['combined_score']:.6f}", rec["n_solved"],
            json.dumps(rec["status_counts"])])
        self._hist_fh.flush()

        # Stream one line per GA population member the moment it finishes (live),
        # not batched at the generation boundary. Baselines (label != "ga") are
        # printed separately by main().
        if self.verbose and self.per_individual and label == "ga":
            self._print_member(config, rec, hit)
        return rec

    def _print_member(self, config: dict, rec: dict, hit: bool):
        current_gen = self.gen + 1                 # gen currently being evaluated
        if current_gen != self._live_gen:
            self._live_gen = current_gen
            self._ind_idx = 0
            print(f"generation {current_gen}:", flush=True)
        ew = rec.get("eval_wall")
        wall = f"{ew:6.3f}s" if ew is not None else "   n/a"
        cached = " (cached)" if hit else ""
        solved = f"{rec['n_solved']}/{rec['n_problems']}"
        print(f"    pop {self._ind_idx:>2}  reliability={rec['reliability']:.4f}  "
              f"time={rec['cum_cpu_time']:7.3f}s  solved={solved:>7}  "
              f"eval_wall={wall}{cached}  [{_fmt_config(config, list(config))}]",
              flush=True)
        self._ind_idx += 1

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


# Short labels for the six ingredients, used in the per-individual printout.
SHORT_KEYS = {
    "constraint_relaxation_strategy": "relax",
    "inequality_handling_method": "ineq",
    "hessian_model": "hess",
    "inertia_correction_strategy": "inertia",
    "globalization_mechanism": "mech",
    "globalization_strategy": "strat",
}


def _fmt_config(options: dict, keys) -> str:
    """Compact one-line rendering of a config: abbreviated keys, full values."""
    return " ".join(f"{SHORT_KEYS.get(k, k)}={options[k]}" for k in keys)


class FrontSnapshot(Callback):
    """Fires at each generation's END: records the front for the evolution plot,
    advances the evaluator's generation counter, and (unless quiet) prints a
    one-line generation summary. The per-population-member lines are streamed
    live during evaluation by ``Evaluator._print_member`` (not here)."""

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
        ev.gen = gen                             # generation just completed
        if not self.log:
            return
        best_rel, best_cpu = max(((r, c) for c, r in pts), key=lambda t: t[0])
        n_eval = getattr(algorithm.evaluator, "n_eval", "?")
        print(f"  -> gen {gen:>3} summary  evals={n_eval:<5} "
              f"distinct={len(ev.cache):<4} front={len(pts):<3} "
              f"best_reliability={best_rel:.4f} @ {best_cpu:.2f}s", flush=True)


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
    ax.set_xlabel("cumulative UNO time over test set (s, log scale)")
    ax.set_ylabel("reliability (fraction of problems solved)")
    ax.set_title(f"Final Pareto front vs. UNO presets ({n_problems} problems, NSGA-II)")
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
    ax.set_xlabel("cumulative UNO time over test set (s)")
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
                     pymoo_version, timestamp, space_size, timing):
    ncols = keys + ["reliability", "cum_cpu_time", "combined_score"]
    src = timing["time_source"]
    time_word = "real (tic-toc) wall-clock" if src == "wall" else "UNO-reported CPU"

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
            f"{r['reliability']:.4f}  ·  time {best['cum_cpu_time']:.3f}s vs "
            f"{r['cum_cpu_time']:.3f}s  ·  score {best['combined_score']:.4f} vs "
            f"{r['combined_score']:.4f}")

    text = f"""# GA (NSGA-II) search results — {problem_set}

_Generated {timestamp} by `scripts/ga_search.py` (pymoo {pymoo_version})._

## Setup

- **Search space:** the six UNO ingredients from `optiuno/uno_search_space.json`
  ({space_size} nominal combinations).
- **Problem set:** `{problem_set}` — {n_problems} HS `.nl` problems.
- **Objective (bi-objective):** maximize reliability (fraction reaching a Feasible
  KKT point), minimize cumulative {time_word} time (`time_source={src}`). Scalar
  tiebreak `combined_score = reliability + 0.1·max(0, 1 − cum_time/{TIME_SCALE:.0f})`.
- **Optimizer:** pymoo NSGA-II (`MixedVariableGA` + `RankAndCrowdingSurvival`),
  pop_size={pop_size}, generations={generations}, seed={seed}.
- **Per-problem budget:** time_limit={time_limit}s. **Solves per config:**
  workers={timing['workers']}.
- **UNO binary:** `{timing['uno_bin']}`. **Fixed options (every solve):**
  {timing['extra_options'] if timing['extra_options'] else '(none — UNO defaults)'}.

## Timing (GA overhead)

**GA overhead = run wall clock − time spent inside UNO.** The UNO time is the sum of
the real tic-toc wall clock measured around each `uno_ampl` subprocess, over every
cache miss (a re-proposed config is served from cache and runs no UNO). This is
directly comparable to the run's wall clock only when `workers=1` (serial).

{_md_table(["metric", "seconds"],
           [["run wall clock", f"{timing['run_wall_s']:.2f}"],
            ["UNO time (sum of tic-toc)", f"{timing['uno_wall_s']:.2f}"],
            ["**GA overhead**", f"**{timing['ga_overhead_s']:.2f}**"]])}

- GA overhead is {(timing['ga_overhead_fraction'] or 0) * 100:.1f}% of the run wall
  clock. Distinct configs solved (UNO calls): {timing['uno_calls']}; total GA
  evaluations (incl. cache hits): {timing['n_evaluations']}.
- Full breakdown in `timing.json`.

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

- Time carries run-to-run noise (wall-clock more so than CPU: it also picks up
  process spawn, I/O and machine load); reliability is noise-free. Front points
  within a fraction of a second are statistically indistinguishable.
- Silent-rewrite detection (UNO running a different config than requested on
  unconstrained/bound-only problems) is a quickRun-harness feature and is **not**
  tracked by the decoupled `optiuno.objective` evaluator used here.
- The space is small ({space_size} points); a complete enumeration + non-dominated
  filter is a feasible exact alternative / ground-truth check.
"""
    path.write_text(text)


# --------------------------------------------------------------------------- #
# UNO binary / extra-option helpers
# --------------------------------------------------------------------------- #
def _parse_options(items) -> dict:
    """Parse repeated ``KEY=VALUE`` strings into a dict (fixed UNO options)."""
    opts = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"--option must be KEY=VALUE, got: {item!r}")
        key, value = item.split("=", 1)
        opts[key.strip()] = value.strip()
    return opts


def _advertised_linear_solvers(uno_bin) -> list | None:
    """Linear solvers the given uno_ampl reports via ``--strategies`` (or None if
    that can't be determined). Used to fail fast on e.g. linear_solver=MA27 against
    a build that lacks HSL, instead of silently scoring every problem as unsolved."""
    try:
        out = subprocess.run([str(uno_bin), "--strategies"], capture_output=True,
                             text=True, timeout=30, env=_bundled_env(str(uno_bin)))
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"Linear solvers?:\s*(.+)", out.stdout or "")
    if not m:
        return None
    return [s.strip() for s in m.group(1).split(",") if s.strip()]


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
    ap.add_argument("--workers", type=int, default=8,
                    help="concurrent solves (default 8, 1 = serial or no parallel pool). "
                         "Keep at 1 so the tic-toc UNO time is comparable to the "
                         "run's wall clock for the GA-overhead measurement.")
    ap.add_argument("--time-source", choices=("wall", "cpu"), default="wall",
                    help="time objective: 'wall' (real tic-toc around each UNO solve, "
                         "default) or 'cpu' (UNO-reported CPU seconds)")
    ap.add_argument("--uno-bin", default=None,
                    help="path to uno_ampl. Default is system-first (optiuno.utils."
                         "select_uno_bin): $UNO_AMPL_BIN -> PATH -> bundled build. "
                         "Point this at a UNO built with HSL to use MA27/MA57.")
    ap.add_argument("--option", action="append", metavar="KEY=VALUE", default=[],
                    help="fixed UNO run-time-option applied to every solve, outside "
                         "the searched ingredients (repeatable), e.g. "
                         "--option linear_solver=MA27")
    ap.add_argument("--out", default=None,
                    help="output dir (default: "
                         "results/ga_pop_<pop>_gen_<gens>_<set>/<timestamp>/)")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress all per-generation output")
    ap.add_argument("--no-population", action="store_true",
                    help="only print the one-line per-generation summary, not each "
                         "population member's result/wall time")
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

    # Resolve which uno_ampl to run (system-first unless --uno-bin given) and the
    # fixed extra options, then fail fast (before creating any output) if a
    # requested linear_solver is absent from the chosen binary.
    try:
        uno_bin = resolve_uno_bin(args.uno_bin)
        extra_options = _parse_options(args.option)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    ls = extra_options.get("linear_solver")
    if ls:
        avail = _advertised_linear_solvers(uno_bin)
        if avail is not None and ls not in avail:
            print(f"error: linear_solver={ls} is not available in {uno_bin}\n"
                  f"       this binary advertises: {', '.join(avail)}\n"
                  f"       point --uno-bin (or $UNO_AMPL_BIN) at a UNO built with HSL.",
                  file=sys.stderr)
            return 2

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_group = f"ga_pop_{args.pop_size}_gen_{args.generations}_{set_name}"
    out_dir = Path(args.out) if args.out else (
        REPO_ROOT / "results" / run_group / timestamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"output dir: {out_dir}")
    print(f"uno binary: {uno_bin}")
    print(f"fixed options: {extra_options if extra_options else '(none)'}")

    # Real (tic-toc) wall clock for the whole run; GA overhead = this - UNO time.
    run_t0 = time.perf_counter()

    evaluator = Evaluator(args.problems, args.time_limit, args.workers, out_dir,
                          time_source=args.time_source, verbose=not args.quiet,
                          per_individual=not args.no_population,
                          uno_bin=uno_bin, extra_options=extra_options)

    # 1) Baselines first (so every plot has reference points), logged as gen 0.
    print("Evaluating preset baselines ...", flush=True)
    presets = {}
    for name, ingredients in PRESET_INGREDIENTS.items():
        rec = evaluator.evaluate(ingredients, label=f"baseline-{name}")
        presets[name] = rec
        print(f"  {name:10s} reliability={rec['reliability']:.4f} "
              f"cumUNO={rec['cum_cpu_time']:.3f}s score={rec['combined_score']:.4f}",
              flush=True)

    # 2) Run NSGA-II over the categorical space.
    print(f"Running NSGA-II: pop={args.pop_size} gens={args.generations} "
          f"seed={args.seed} (per-population output below; "
          f"--no-population for summary only) ...", flush=True)
    problem = UnoProblem(search_space, evaluator)
    algorithm = MixedVariableGA(pop_size=args.pop_size,
                                survival=RankAndCrowdingSurvival())
    snapshot = FrontSnapshot(log=not args.quiet)
    # pymoo runs on an internal COPY of `algorithm`; the result carries the copy
    # that actually ran (its evaluator holds the true n_eval).
    result = minimize(problem, algorithm, ("n_gen", args.generations),
                      seed=args.seed, callback=snapshot, verbose=args.verbose)

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
        w.writerow(["preset"] + keys
                   + ["reliability", "cum_cpu_time", "combined_score"])
        for p in front:
            w.writerow([match_preset(p["options"])]
                       + [p["options"][k] for k in keys]
                       + [f"{p['reliability']:.6f}", f"{p['cum_cpu_time']:.4f}",
                          f"{p['combined_score']:.6f}"])

    plot_final(out_dir / "pareto_final.png", all_recs, front, presets,
               best["n_problems"])
    plot_evolution(out_dir / "pareto_evolution.png", snapshot.snapshots, presets)

    # 5) Timing: GA overhead = real run wall clock - real UNO (tic-toc) time.
    run_wall = time.perf_counter() - run_t0
    uno_wall = evaluator.total_uno_time
    ga_overhead = run_wall - uno_wall
    ran_algo = getattr(result, "algorithm", None)  # the copy pymoo actually ran
    n_evaluations = getattr(getattr(ran_algo, "evaluator", None), "n_eval", None)
    timing = {
        "time_source": args.time_source,
        "workers": args.workers,
        "uno_bin": str(uno_bin),
        "extra_options": extra_options,
        "run_wall_s": round(run_wall, 4),
        "uno_wall_s": round(uno_wall, 4),
        "ga_overhead_s": round(ga_overhead, 4),
        "ga_overhead_fraction": round(ga_overhead / run_wall, 4) if run_wall else None,
        "uno_calls": evaluator.n_uno_calls,
        "n_evaluations": n_evaluations,
        "n_distinct_configs": len(all_recs),
    }
    (out_dir / "timing.json").write_text(json.dumps(timing, indent=2) + "\n")

    write_results_md(
        out_dir / "RESULTS.md", keys=keys, presets=presets, front=front, best=best,
        all_recs=all_recs, n_problems=best["n_problems"], problem_set=set_name,
        pop_size=args.pop_size, generations=args.generations, seed=args.seed,
        time_limit=args.time_limit, pymoo_version=_pymoo_version(),
        timestamp=timestamp, space_size=space_size, timing=timing)

    # 6) Console summary.
    print(f"\nDistinct configs evaluated: {len(all_recs)} / {space_size} nominal")
    print(f"Pareto front size: {len(front)}")
    print("Best config (max combined_score):")
    for k in keys:
        print(f"    {k} = {best['options'][k]}")
    print(f"  reliability={best['reliability']:.4f} "
          f"cumUNO={best['cum_cpu_time']:.3f}s ({args.time_source}) "
          f"score={best['combined_score']:.4f}")
    print(f"\nTiming ({args.time_source} source, workers={args.workers}):")
    print(f"  run wall clock : {run_wall:8.2f} s")
    print(f"  UNO time (sum) : {uno_wall:8.2f} s  ({evaluator.n_uno_calls} solves)")
    print(f"  GA overhead    : {ga_overhead:8.2f} s"
          + (f"  ({100 * ga_overhead / run_wall:.1f}% of run)" if run_wall else ""))
    if args.workers != 1:
        print("  NOTE: workers != 1 -> UNO wall clocks overlap; overhead is not "
              "directly meaningful. Re-run with --workers 1.")
    print(f"\nWrote results to: {out_dir}")
    return 0


def _pymoo_version() -> str:
    import pymoo
    return getattr(pymoo, "__version__", "unknown")


if __name__ == "__main__":
    raise SystemExit(main())
