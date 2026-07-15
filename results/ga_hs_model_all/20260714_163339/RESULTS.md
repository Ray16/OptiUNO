# GA (NSGA-II) search results — hs_model_all

_Generated 20260714_163339 by `scripts/ga_search.py` (pymoo 0.6.2)._

## Setup

- **Search space:** the six UNO ingredients from `optiuno/uno_search_space.json`
  (240 nominal combinations).
- **Problem set:** `hs_model_all` — 121 HS `.nl` problems.
- **Objective (bi-objective):** maximize reliability (fraction reaching a Feasible
  KKT point), minimize cumulative UNO CPU time. Scalar tiebreak
  `combined_score = reliability + 0.1·max(0, 1 − cum_cpu_time/60)`.
- **Optimizer:** pymoo NSGA-II (`MixedVariableGA` + `RankAndCrowdingSurvival`),
  pop_size=24, generations=15, seed=1.
- **Per-problem budget:** time_limit=20.0s. **UNO binary:** bundled
  `external/uno` build (pinned via `optiuno`).

## Preset baselines

| preset | reliability | cum_cpu_time (s) | combined_score |
|---|---|---|---|
| filtersqp | 0.9669 | 4.877 | 1.0588 |
| ipopt | 0.9174 | 11.614 | 0.9980 |

## Best configuration found (max combined_score)

| constraint_relaxation_strategy | inequality_handling_method | hessian_model | inertia_correction_strategy | globalization_mechanism | globalization_strategy | reliability | cum_cpu_time | combined_score |
|---|---|---|---|---|---|---|---|---|
| feasibility_restoration | inequality_constrained | exact | none | TR | fletcher_filter_method | 0.9669 | 4.877 | 1.0588 |

- vs **filtersqp**: reliability 0.9669 vs 0.9669  ·  CPU 4.877s vs 4.877s  ·  score 1.0588 vs 1.0588
- vs **ipopt**: reliability 0.9669 vs 0.9174  ·  CPU 4.877s vs 11.614s  ·  score 1.0588 vs 0.9980

## Pareto front (3 non-dominated configs)

| constraint_relaxation_strategy | inequality_handling_method | hessian_model | inertia_correction_strategy | globalization_mechanism | globalization_strategy | reliability | cum_cpu_time | combined_score |
|---|---|---|---|---|---|---|---|---|
| feasibility_restoration | interior_point | LSR1 | primal | TR | fletcher_filter_method | 0.0000 | 1.579 | 0.0974 |
| feasibility_restoration | inequality_constrained | exact | primal_dual | LS | fletcher_filter_method | 0.1570 | 3.225 | 0.2517 |
| feasibility_restoration | inequality_constrained | exact | none | TR | fletcher_filter_method | 0.9669 | 4.877 | 1.0588 |

Full front configs also in `front_configs.json` / `pareto_front.csv`; plots in
`pareto_final.png` (vs. presets, log time axis) and `pareto_evolution.png`.

## Search coverage

- Distinct configs evaluated: **195** of 240 nominal
  (the config cache makes re-proposed configs free).
- Generations: 15, population 24.

## Notes

- CPU time carries ~5–15% run-to-run noise; reliability is noise-free. Front
  points within a fraction of a second are statistically indistinguishable.
- Silent-rewrite detection (UNO running a different config than requested on
  unconstrained/bound-only problems) is a quickRun-harness feature and is **not**
  tracked by the decoupled `optiuno.objective` evaluator used here.
- The space is small (240 points); a complete enumeration + non-dominated
  filter is a feasible exact alternative / ground-truth check.
