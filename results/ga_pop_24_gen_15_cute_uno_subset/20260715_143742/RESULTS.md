# GA (NSGA-II) search results — cute_uno_subset

_Generated 20260715_143742 by `scripts/ga_search.py` (pymoo 0.6.2)._

## Setup

- **Search space:** the six UNO ingredients from `optiuno/uno_search_space.json`
  (240 nominal combinations).
- **Problem set:** `cute_uno_subset` — 425 HS `.nl` problems.
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
| run wall clock | 5242.27 |
| UNO time (sum of tic-toc) | 28853.27 |
| **GA overhead** | **-23611.00** |

- GA overhead is -450.4% of the run wall
  clock. Distinct configs solved (UNO calls): 188; total GA
  evaluations (incl. cache hits): 358.
- Full breakdown in `timing.json`.

## Preset baselines

| preset | reliability | cum_cpu_time (s) | combined_score |
|---|---|---|---|
| filtersqp | 0.9459 | 45.693 | 0.9697 |
| ipopt | 0.8494 | 34.603 | 0.8917 |
| funnelsqp | 0.9435 | 45.933 | 0.9670 |
| filterslp | 0.6282 | 60.669 | 0.6282 |

## Best configuration found (max combined_score)

| constraint_relaxation_strategy | inequality_handling_method | hessian_model | inertia_correction_strategy | globalization_mechanism | globalization_strategy | reliability | cum_cpu_time | combined_score |
|---|---|---|---|---|---|---|---|---|
| feasibility_restoration | inequality_constrained | exact | none | TR | fletcher_filter_method | 0.9459 | 45.693 | 0.9697 |

- vs **filtersqp**: reliability 0.9459 vs 0.9459  ·  time 45.693s vs 45.693s  ·  score 0.9697 vs 0.9697
- vs **ipopt**: reliability 0.9459 vs 0.8494  ·  time 45.693s vs 34.603s  ·  score 0.9697 vs 0.8917
- vs **funnelsqp**: reliability 0.9459 vs 0.9435  ·  time 45.693s vs 45.933s  ·  score 0.9697 vs 0.9670
- vs **filterslp**: reliability 0.9459 vs 0.6282  ·  time 45.693s vs 60.669s  ·  score 0.9697 vs 0.6282

## Pareto front (12 non-dominated configs)

| constraint_relaxation_strategy | inequality_handling_method | hessian_model | inertia_correction_strategy | globalization_mechanism | globalization_strategy | reliability | cum_cpu_time | combined_score |
|---|---|---|---|---|---|---|---|---|
| feasibility_restoration | inequality_constrained | zero | primal_dual | TR | funnel_method | 0.0000 | 10.441 | 0.0826 |
| feasibility_restoration | inequality_constrained | LSR1 | primal | TR | fletcher_filter_method | 0.0329 | 10.486 | 0.1155 |
| feasibility_restoration | inequality_constrained | zero | primal_dual | LS | waechter_filter_method | 0.0565 | 15.832 | 0.1301 |
| feasibility_restoration | inequality_constrained | zero | primal_dual | LS | funnel_method | 0.0612 | 16.394 | 0.1339 |
| feasibility_restoration | inequality_constrained | exact | primal_dual | LS | waechter_filter_method | 0.3082 | 16.402 | 0.3809 |
| feasibility_restoration | inequality_constrained | exact | primal_dual | LS | funnel_method | 0.3200 | 18.003 | 0.3900 |
| feasibility_restoration | inequality_constrained | exact | none | LS | waechter_filter_method | 0.6753 | 22.413 | 0.7379 |
| feasibility_restoration | inequality_constrained | exact | none | LS | funnel_method | 0.6776 | 23.828 | 0.7379 |
| feasibility_restoration | interior_point | exact | primal_dual | LS | waechter_filter_method | 0.8494 | 34.603 | 0.8917 |
| feasibility_restoration | interior_point | exact | primal_dual | LS | funnel_method | 0.8941 | 34.735 | 0.9362 |
| feasibility_restoration | interior_point | exact | primal | LS | funnel_method | 0.8988 | 42.551 | 0.9279 |
| feasibility_restoration | inequality_constrained | exact | none | TR | fletcher_filter_method | 0.9459 | 45.693 | 0.9697 |

Full front configs also in `front_configs.json` / `pareto_front.csv`; plots in
`pareto_final.png` (vs. presets, log time axis) and `pareto_evolution.png`.

## Search coverage

- Distinct configs evaluated: **188** of 240 nominal
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
