# GA (NSGA-II) search results — hs_model_all

_Generated 20260714_202336 by `scripts/ga_search.py` (pymoo 0.6.2)._

## Setup

- **Search space:** the six UNO ingredients from `optiuno/uno_search_space.json`
  (240 nominal combinations).
- **Problem set:** `hs_model_all` — 121 HS `.nl` problems.
- **Objective (bi-objective):** maximize reliability (fraction reaching a Feasible
  KKT point), minimize cumulative real (tic-toc) wall-clock time (`time_source=wall`). Scalar
  tiebreak `combined_score = reliability + 0.1·max(0, 1 − cum_time/60)`.
- **Optimizer:** pymoo NSGA-II (`MixedVariableGA` + `RankAndCrowdingSurvival`),
  pop_size=24, generations=15, seed=1.
- **Per-problem budget:** time_limit=20.0s. **Solves per config:**
  workers=1.
- **UNO binary:** `/home/sdinh/sandbox/Uno/build/uno_ampl`. **Fixed options (every solve):**
  {'linear_solver': 'MA27'}.

## Timing (GA overhead)

**GA overhead = run wall clock − time spent inside UNO.** The UNO time is the sum of
the real tic-toc wall clock measured around each `uno_ampl` subprocess, over every
cache miss (a re-proposed config is served from cache and runs no UNO). This is
directly comparable to the run's wall clock only when `workers=1` (serial).

| metric | seconds |
|---|---|
| run wall clock | 7252.22 |
| UNO time (sum of tic-toc) | 7190.42 |
| **GA overhead** | **61.80** |

- GA overhead is 0.9% of the run wall
  clock. Distinct configs solved (UNO calls): 193; total GA
  evaluations (incl. cache hits): 358.
- Full breakdown in `timing.json`.

## Preset baselines

| preset | reliability | cum_cpu_time (s) | combined_score |
|---|---|---|---|
| filtersqp | 0.9669 | 3.177 | 1.0616 |
| ipopt | 0.9256 | 1.213 | 1.0236 |

## Best configuration found (max combined_score)

| constraint_relaxation_strategy | inequality_handling_method | hessian_model | inertia_correction_strategy | globalization_mechanism | globalization_strategy | reliability | cum_cpu_time | combined_score |
|---|---|---|---|---|---|---|---|---|
| feasibility_restoration | interior_point | exact | primal_dual | LS | funnel_method | 0.9669 | 1.479 | 1.0645 |

- vs **filtersqp**: reliability 0.9669 vs 0.9669  ·  time 1.479s vs 3.177s  ·  score 1.0645 vs 1.0616
- vs **ipopt**: reliability 0.9669 vs 0.9256  ·  time 1.479s vs 1.213s  ·  score 1.0645 vs 1.0236

## Pareto front (3 non-dominated configs)

| constraint_relaxation_strategy | inequality_handling_method | hessian_model | inertia_correction_strategy | globalization_mechanism | globalization_strategy | reliability | cum_cpu_time | combined_score |
|---|---|---|---|---|---|---|---|---|
| feasibility_restoration | interior_point | exact | primal_dual | LS | waechter_filter_method | 0.9256 | 1.213 | 1.0236 |
| feasibility_restoration | interior_point | exact | primal | LS | funnel_method | 0.9587 | 1.218 | 1.0566 |
| feasibility_restoration | interior_point | exact | primal_dual | LS | funnel_method | 0.9669 | 1.479 | 1.0645 |

Full front configs also in `front_configs.json` / `pareto_front.csv`; plots in
`pareto_final.png` (vs. presets, log time axis) and `pareto_evolution.png`.

## Search coverage

- Distinct configs evaluated: **193** of 240 nominal
  (the config cache makes re-proposed configs free).
- Generations: 15, population 24.

## Notes

- Time carries run-to-run noise (wall-clock more so than CPU: it also picks up
  process spawn, I/O and machine load); reliability is noise-free. Front points
  within a fraction of a second are statistically indistinguishable.
- Silent-rewrite detection (UNO running a different config than requested on
  unconstrained/bound-only problems) is a quickRun-harness feature and is **not**
  tracked by the decoupled `optiuno.objective` evaluator used here.
- The space is small (240 points); a complete enumeration + non-dominated
  filter is a feasible exact alternative / ground-truth check.
