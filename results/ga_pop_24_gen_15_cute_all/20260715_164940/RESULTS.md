# GA (NSGA-II) search results — cute_all

_Generated 20260715_164940 by `scripts/ga_search.py` (pymoo 0.6.2)._

## Setup

- **Search space:** the six UNO ingredients from `optiuno/uno_search_space.json`
  (240 nominal combinations).
- **Problem set:** `cute_all` — 727 HS `.nl` problems.
- **Objective (bi-objective):** maximize reliability (fraction reaching a Feasible
  KKT point), minimize cumulative real (tic-toc) wall-clock time (`time_source=wall`). Scalar
  tiebreak `combined_score = reliability + 0.1·max(0, 1 − cum_time/60)`.
- **Optimizer:** pymoo NSGA-II (`MixedVariableGA` + `RankAndCrowdingSurvival`),
  pop_size=24, generations=15, seed=1.
- **Per-problem budget:** time_limit=20.0s. **Solves per config:**
  workers=8.
- **UNO binary:** `/home/sdinh/sandbox/OptiUNO/external/uno/bin/uno_ampl`. **Fixed options (every solve):**
  (none — UNO defaults).

## Timing (GA overhead)

**GA overhead = run wall clock − time spent inside UNO.** The UNO time is the sum of
the real tic-toc wall clock measured around each `uno_ampl` subprocess, over every
cache miss (a re-proposed config is served from cache and runs no UNO). This is
directly comparable to the run's wall clock only when `workers=1` (serial).

| metric | seconds |
|---|---|
| run wall clock | 83349.13 |
| UNO time (sum of tic-toc) | 439011.15 |
| **GA overhead** | **-355662.02** |

- GA overhead is -426.7% of the run wall
  clock. Distinct configs solved (UNO calls): 191; total GA
  evaluations (incl. cache hits): 358.
- Full breakdown in `timing.json`.

## Preset baselines

| preset | reliability | cum_cpu_time (s) | combined_score |
|---|---|---|---|
| filtersqp | 0.7950 | 3463.393 | 0.7950 |
| ipopt | 0.7015 | 1091.853 | 0.7015 |
| funnelsqp | 0.7909 | 3541.034 | 0.7909 |
| filterslp | 0.4924 | 2795.077 | 0.4924 |

## Best configuration found (max combined_score)

| constraint_relaxation_strategy | inequality_handling_method | hessian_model | inertia_correction_strategy | globalization_mechanism | globalization_strategy | reliability | cum_cpu_time | combined_score |
|---|---|---|---|---|---|---|---|---|
| feasibility_restoration | inequality_constrained | exact | primal | LS | funnel_method | 0.8019 | 2344.611 | 0.8019 |

- vs **filtersqp**: reliability 0.8019 vs 0.7950  ·  time 2344.611s vs 3463.393s  ·  score 0.8019 vs 0.7950
- vs **ipopt**: reliability 0.8019 vs 0.7015  ·  time 2344.611s vs 1091.853s  ·  score 0.8019 vs 0.7015
- vs **funnelsqp**: reliability 0.8019 vs 0.7909  ·  time 2344.611s vs 3541.034s  ·  score 0.8019 vs 0.7909
- vs **filterslp**: reliability 0.8019 vs 0.4924  ·  time 2344.611s vs 2795.077s  ·  score 0.8019 vs 0.4924

## Pareto front (7 non-dominated configs)

| constraint_relaxation_strategy | inequality_handling_method | hessian_model | inertia_correction_strategy | globalization_mechanism | globalization_strategy | reliability | cum_cpu_time | combined_score |
|---|---|---|---|---|---|---|---|---|
| feasibility_restoration | inequality_constrained | LSR1 | primal | TR | funnel_method | 0.0344 | 71.162 | 0.0344 |
| feasibility_restoration | inequality_constrained | exact | primal_dual | LS | funnel_method | 0.3177 | 410.428 | 0.3177 |
| feasibility_restoration | interior_point | exact | primal_dual | LS | waechter_filter_method | 0.7015 | 1091.853 | 0.7015 |
| feasibility_restoration | interior_point | exact | primal_dual | LS | funnel_method | 0.7359 | 1297.774 | 0.7359 |
| feasibility_restoration | inequality_constrained | exact | primal | LS | fletcher_filter_method | 0.7964 | 2276.793 | 0.7964 |
| feasibility_restoration | inequality_constrained | exact | primal | LS | waechter_filter_method | 0.8006 | 2326.109 | 0.8006 |
| feasibility_restoration | inequality_constrained | exact | primal | LS | funnel_method | 0.8019 | 2344.611 | 0.8019 |

Full front configs also in `front_configs.json` / `pareto_front.csv`; plots in
`pareto_final.png` (vs. presets, log time axis) and `pareto_evolution.png`.

## Search coverage

- Distinct configs evaluated: **191** of 240 nominal
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
