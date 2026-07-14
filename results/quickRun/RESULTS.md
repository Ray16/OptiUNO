# OptiUNO experiment results

*Status: full 150-iteration openEvolve search completed 2026-07-13 on the
claude-code (subscription) backend, model `sonnet`. Harness validated
against the paper; baselines and CPU-time variance measured.*

## Setup

- **Solver:** UNO v2.8.0 release binaries (`external/uno/bin/uno_ampl`),
  invoked on AMPL `.nl` files with `option=value` pairs. Strategies compiled
  in: QP/LP = {BQPD, HiGHS}, linear = {MUMPS, SSIDS}, all six ingredient
  option sets complete.
- **Test set:** 123 Hock–Schittkowski problems (Vanderbei AMPL translations,
  `.mod → .nl` via the AMPL demo module). Excluded: hs35i, hs76i (source
  unavailable), hs068, hs069 (need `funcadd.c`/`myerf`; UNO's ASL crashes).
  See `models/untranslatable.md`.
- **Objectives:** reliability = fraction solved (termination "Feasible KKT
  point" within a 20 s/problem limit); cumulative CPU time = sum of UNO's
  self-reported CPU seconds (timeouts contribute the full limit).
- **Search space:** the six ingredient options — note that Uno 2.8.0
  *accepts* `interior_point`+`TR` (prohibited in the 2.2.0 paper), so all
  240 nominal combinations are runnable; UNO's own failures/rewrites are
  classified by the harness.

## Harness validation (arXiv:2406.13454)

See `results/preset_validation.md`. All 123 test problems appear in the
paper's per-instance tables. Solved/failed agreement is **120/123 (97.6%)
for both presets**; ~50 problems have *identical* objective-evaluation
counts despite the 2.2.0 → 2.8.0 version gap. Disagreements: 2.8.0 newly
solves hs085 and hs114 (solver improvements); ours terminates at an
infeasible stationary point on hs061/hs093 which the paper counts solved
(version and/or model-translation differences — the paper used the
Neumaier/COCONUT AMPL translations, we use Vanderbei's).

**Verdict: PASS** — the python↔UNO connection reproduces published behavior.

## Baselines (123 problems)

| Configuration | Reliability | Cum. CPU time (mean of R=10) | Std dev |
|---|---|---|---|
| preset `filtersqp` | 0.976 (120/123) | 1.44 s | 0.12 s |
| preset `ipopt` | 0.984 (121/123) | 2.58 s | 0.30 s |
| `filtersqp` ingredients only | 0.976 (120/123) | 1.33 s | 0.22 s |
| `ipopt` ingredients only | 0.927 (114/123) | 5.00 s | 0.22 s |

Two observations:

1. **The `ipopt` preset's edge over its bare ingredients is large**
   (0.984/2.6 s vs 0.927/5.0 s): the preset's ~30 non-ingredient option
   settings (barrier parameters, tolerances, …) matter. The six-ingredient
   search is therefore a *lower bound* on what configuration tuning can do.
2. **CPU-time noise is 5–15% relative sd** (see `results/variance.md`), so
   Pareto points closer than ~0.3 s in time are statistically
   indistinguishable; reliability is noise-free across repetitions.

## Evolution search (150 iterations, completed)

**Run:** openEvolve 0.3.1, `claude_code` provider (model `sonnet`), MAP-Elites
over (reliability × cum_cpu_time), 3 islands, seeded with the `filtersqp`
ingredient configuration. **156 evaluations logged, 36 distinct
configurations tried** (the LLM re-proposed duplicates; the config-hash cache
made repeats free). Full evaluation log: `evolution_history.csv`
(config JSON, reliability, cumulative CPU time, combined score, status
counts, in evaluation order). Figures: `pareto_evolution.png`,
`pareto_final.png`. Front configs: `front_configs.json`.

### Final Pareto front (reliability ↑, cumulative CPU time ↓)

| Reliability | Cum. CPU | Ingredients (ineq. handling / Hessian / inertia / mech / strategy) |
|---|---|---|
| 0.976 (120/123) | 1.33 s | inequality_constrained / exact / none / **TR / fletcher_filter** (= filtersqp ingredients, the seed) |
| 0.967 (119/123) | 1.16 s | inequality_constrained / exact / none / **TR / funnel** |
| 0.171 (21/123) | 1.01 s | inequality_constrained / exact / **primal_dual** / LS / funnel |
| 0.163 (20/123) | 0.83 s | inequality_constrained / exact / **primal_dual** / LS / fletcher_filter |
| 0.000 (0/123) | 0.58 s | inequality_constrained / LSR1 / **primal_dual** / TR / waechter_filter |

### Findings

1. **No six-ingredient combination beat the `filtersqp` ingredients on
   reliability** (0.976). The genuinely new, interesting front point is
   **TR + funnel_method + exact + no inertia correction**: 119/123 at
   1.16 s — ~13% faster than the filtersqp ingredients, one problem less
   solved. The funnel method appears in no preset (and not even in the
   paper's wheel), so this is a new, competitive combination.
2. **The `ipopt` *preset* (0.984, 2.58 s) remains the reliability champion
   and is unreachable in ingredient space**: the best interior-point
   ingredient config found was 0.943 / 18.3 s. Its ~30 non-ingredient
   option settings (barrier schedule, tolerances) do the heavy lifting —
   consistent with the baseline gap (0.984 preset vs 0.927 bare
   ingredients).
3. **A broken region of the space:** `inertia_correction_strategy =
   primal_dual` combined with `inequality_handling_method =
   inequality_constrained` (SQP-type subproblems) fails with "Algorithmic
   error / Suboptimal point" on essentially every problem, regardless of
   the other ingredients. These configs fail *fast*, which is why they
   occupy the low-reliability end of the front (nothing dominates them on
   time). This is exactly the "some combinations do not work at all"
   phenomenon the README predicted — now with a concrete culprit pair.
4. **The front converged after ~39 evaluations** (see
   `pareto_evolution.png`); iterations 40–150 re-proposed known configs or
   dominated variants. For a 240-point discrete space, evolutionary search
   spends most of its budget on duplicates — complete enumeration (~36
   already covered, 204 to go) is the natural next step and was deliberately
   deferred.

### Caveats

- CPU-time error bars: preset markers in `pareto_final.png` carry the R=10
  standard deviations from `variance.md`; evolved-front points are
  single-sweep measurements (per instruction, no variance runs were
  performed for them), so ±0.1–0.3 s applies to close comparisons.
- Reliability counts "Feasible KKT point" only; 11 of the 123 problems are
  unconstrained/bound-only and UNO silently rewrites the globalization
  strategy to a merit function there (detected and counted per run,
  `n_rewritten`), so strategy comparisons are effectively over 112
  constrained problems.
