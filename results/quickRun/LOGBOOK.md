# LOGBOOK

Append-only history of the OptiUNO project. Never edit or remove existing entries — only add new dated ones.

---

## 2026-07-13 — Start

First session. Read `README.md` and `UNO.pdf` (Vanaret & Leyffer, *Implementing a unified solver for nonlinearly constrained optimization*, MPC 2026, 44 pp.) to load project context. No files were created or modified beyond this logbook.

### README.md — the project brief

OptiUNO seeks *optimal configurations of UNO* rather than an optimal solution to a single NLP. The framing is a meta-optimization:

- **Variables** = UNO's `run-time-options` (the strategy combination)
- **Objective** = a performance metric over a test set (CPU time, variance in time, iteration count — deliberately left open, possibly multi-objective)
- **Optimizer** = openEvolve or Google's AlphaEvolve, with complete enumeration as the fallback if evolutionary search underperforms
- **Test set** = e.g. Hock–Schittkowski from Vanderbei's AMPL nonlinear models

The README flags up front that some option combinations simply do not work, so the harness must catch failures, and asks whether the best options depend on the problem class. The research product would be a methodology + findings write-up, including a comparison of openEvolve vs. AlphaEvolve vs. complete enumeration. The idea originated from Nick Gould asking Sven whether he had explored all the configurations.

### UNO.pdf — the authoritative description of the search space

The paper abstracts Lagrange–Newton methods (SQP and interior-point alike) into **eight ingredients in four layers**:

| Layer | Ingredients | Strategies named in the paper |
|---|---|---|
| Reformulation | constraint relaxation strategy; inequality handling method | ℓ1 relaxation, feasibility restoration; inequality-constrained, equality-constrained, interior-point |
| Subproblem | Hessian model; inertia correction strategy | exact, quasi-Newton, identity, zero; none, primal, primal-dual |
| Subproblem solver | subproblem solver | QP (BQPD), LP (HiGHS), linear (MA57/MA27/MUMPS) |
| Globalization | globalization strategy; globalization mechanism | merit function (ℓ1) vs. filter method; line search vs. trust region |

Points that bear directly on the capstone:

**The ~186 number is a Cartesian product with holes.** §5.2 says the count of combinations is exactly the size of the Cartesian product of the eight ingredients, that not all of them yield sensible or convergent algorithms, and that UNO 2.2.0 *explicitly prohibits* interior-point + trust-region (KNITRO's step decomposition would be needed; the authors plan to lift this in a later version). Other ingredients are also auto-overridden rather than freely chosen — §5.3.5 lists cases where UNO picks the ingredient for you:

- the subproblem solver is chosen by whether the subproblems have curvature (QP solver if yes, LP solver otherwise);
- if the reformulated problem is unconstrained, the constraint relaxation strategy is forced to `NoRelaxation`, the globalization strategy to `l1MeritFunction`, and (absent curvature) the subproblem solver to `BoxLPSolver`;
- an "exact" Hessian model with no explicit matrix or linear operator supplied silently degrades to "zero" (with a warning printed).

Consequence for the harness: it must distinguish **invalid**, **silently rewritten**, and **genuinely failed** configurations — three cases, not two. The silently-rewritten case is the trap: it will look like a valid data point for a configuration that was never actually run.

**Only two presets exist** in UNO 2.2.0 — `filtersqp` (trust-region restoration filter SQP) and `ipopt` (line-search restoration filter interior-point) — and both are documented as incomplete relative to the solvers they mimic (no second-order correction steps; the `ipopt` preset additionally lacks scaling, least-square multipliers, iterative refinement, iterative bound relaxations, non-monotone techniques, and soft feasibility restoration). That is the baseline to beat, and it is a beatable one.

**The paper's own metric is objective evaluations, not CPU time.** §7 benchmarks on 429 small CUTE problems translated to AMPL, reporting performance profiles (Fig. 4) and a shifted geometric mean (shift *s* = 10, failures counted as 10⁶ evaluations). Table 2: `filtersqp` 18.08, `ipopt` 48.45 vs. filterSQP 18.73, IPOPT 34.63, SNOPT 61.02, MINOS 159.78, LANCELOT 92.27, LOQO 71.44, CONOPT 43.15. That shifted-geometric-mean-with-failure-penalty is a ready-made, defensible objective function for the evolutionary search, and it already encodes the failure handling the README worries about.

Note the paper's benchmark is CUTE, not the Hock–Schittkowski/Vanderbei set proposed in the README — though the CUTE subset in Table 1 contains a large number of `hsNNN` instances anyway. Public log files: https://github.com/cvanaret/nonlinear_optimization_solver_benchmark

**Other facts worth carrying forward:** Uno 2.2.0 is ~10,000 lines of C++17, MIT-licensed, with C/Julia (`UnoSolver.jl`)/Python/Fortran/AMPL interfaces. Termination criteria (§5.3.7) are richer than "converged / did not converge" — feasible KKT point, feasible FJ point, infeasible stationary point, small trust region, and a loose-tolerance fallback are all distinct exits and should be recorded as distinct outcomes by the harness. Future Uno releases plan quasi-Newton (L-BFGS, SR1), iterative linear solvers, SLP-EQP, and a parallel line search — i.e. the search space will grow.

### Discrepancies found

- `CLAUDE.md` points at `RelevantFiles/Implementing a unified solver for nonlinearly constrained optimization.pdf`, but that directory does not exist — the paper now lives at the top level as `UNO.pdf`. The reference needs updating.
- `CLAUDE.md` instructs reading `LOGBOOK.md` and `STATUS.md` at session start; neither existed. This file is the first; `STATUS.md` still needs to be created.

### Open questions / next steps

- Choose the performance metric (single- vs. multi-objective; objective evaluations vs. CPU time vs. iterations).
- Enumerate the legal option space from UNO's docs and build a runner that classifies invalid / silently-rewritten / failed configurations.
- Decide test set: Vanderbei Hock–Schittkowski (per README) vs. the 429-problem CUTE set used by the paper (which enables direct comparison against Table 2).

---

## 2026-07-13 — Catalogued the UNO run-time option space

Transcribed the complete set of UNO run-time options from the manual into two new files (same content, two formats — keep them in sync):

- `uno-options.json` — machine-readable; intended as the input to the search driver.
- `uno-options.md` — human-readable, one table per option category.

Sources: https://unosolver.readthedocs.io/en/latest/options/ and https://unosolver.readthedocs.io/en/latest/presets/ (both retrieved 2026-07-13). The manual does not state which Uno version it documents.

### What the option space actually looks like

**90 options in total, of which 17 have a finite value set.** Those 17 are the discrete search space; the remaining 73 are continuous / integer / boolean / string hyperparameters (tolerances, factors, radii, barrier coefficients, …).

The six *ingredient* options — the primary optimization variables:

| Option | Values |
|---|---|
| `constraint_relaxation_strategy` | `feasibility_restoration` |
| `inequality_handling_method` | `inequality_constrained`, `interior_point` |
| `hessian_model` | `exact`, `LBFGS`, `LSR1`, `identity`, `zero` |
| `inertia_correction_strategy` | `primal`, `primal_dual`, `none` |
| `globalization_mechanism` | `TR`, `LS` |
| `globalization_strategy` | `merit_function`, `fletcher_filter_method`, `waechter_filter_method`, `funnel_method` |

Subproblem solvers (build-dependent — must be probed against the actual binary, not assumed): `QP_solver` ∈ {BQPD, HiGHS}, `LP_solver` ∈ {BQPD, HiGHS}, `linear_solver` ∈ {MA57, MA27, MA86, MUMPS, SSIDS}. Remaining categorical options: `preset`, `logger`, `progress_norm`, `residual_norm` (L1/L2/INF), `filter_type` (only `standard`), `barrier_function` (only `log`), `BQPD_kmax_heuristic` (filtersqp/minotaur), and the integer enum `funnel_update_strategy` ∈ {1,2,3}.

### Manual vs. paper — three findings

1. **The manual exposes only ONE constraint relaxation strategy.** UNO.pdf §4.2 describes two (ℓ1 relaxation *and* feasibility restoration), but `constraint_relaxation_strategy` accepts only `feasibility_restoration`. Either ℓ1 relaxation is not user-selectable, or the docs lag the code. **Open question for Sven — this directly changes the size of the search space.**
2. **The manual is AHEAD of the paper in two places** (good news — the space is bigger than UNO.pdf suggests): `hessian_model` now offers `LBFGS` and `LSR1`, which the paper lists as *future* work; and `globalization_strategy` offers `funnel_method`, which does not appear in the paper's wheel of strategies at all.
3. **Naming inconsistency inside the manual itself:** the presets page sets `filter_switching_infeasibility_exponent`, while the options page calls the same option `switching_infeasibility_exponent`. Verify against the binary before scripting either name.

### Derived sanity check on the "186 configurations" claim

Cartesian product of the six ingredients as documented: 1 × 2 × 5 × 3 × 2 × 4 = **240**. Removing the prohibited `interior_point` + `TR` combinations (1 × 1 × 5 × 3 × 1 × 4 = 60) leaves **180** nominally-legal combinations — the same ballpark as the README's "at least 186". This is a *derived* count, not a figure from the manual; treat it as a sanity check only. Multiplying in the solver choices and the two norms inflates it substantially.

### Recorded in the JSON for the harness

- `known_invalid_combinations` — currently one entry: `interior_point` + `TR` (UNO.pdf §5.2).
- `silent_overrides` — the three cases from UNO.pdf §5.3.5 where Uno rewrites your configuration instead of rejecting it (LP-solver swap when the subproblem has no curvature; `NoRelaxation`/`l1MeritFunction`/`BoxLPSolver` forced for unconstrained reformulations; `hessian_model = exact` degrading to `zero` when no Hessian is supplied). This is the dangerous class: the run *succeeds* and looks like a valid data point for a configuration that was never actually tested.
- Both presets (`filtersqp`, `ipopt`) with their full option settings — the baselines to beat — plus the `auto` selection rule (ipopt if 2000 ≤ n+m or 50000 ≤ nnz(∇c)+nnz(∇²L), else filtersqp).

### Next steps (unchanged from the Start entry, plus)

- Confirm with Sven whether ℓ1 relaxation is selectable; if so, the docs are incomplete and the JSON needs a new value.
- Probe an actual Uno build to determine which QP/LP/linear solvers are compiled in, and to resolve the `switching_infeasibility_exponent` naming question.
- Still open: performance metric, test set, and the runner that classifies invalid / silently-rewritten / failed configurations.

---

## 2026-07-13 — Built the full testing environment (openEvolve × UNO × HS set)

Implemented the plan in `plan-26-07-13-openEvolve.md` (multi-objective search over the six ingredient options: maximize reliability = fraction solved, minimize cumulative CPU time; empirical time variance reported for reference). Decisions made with Sven: openEvolve driver, Anthropic API backend with **claude-sonnet-5 as the default, overridable model**, project-local setup only (`.venv/`, `external/`), full HS test set.

### Interface decision (answers a question from the plan)

`unopy` (pip) defines problems **via Python callbacks only — it cannot read `.nl` files**. The native `uno_ampl` executable reads `.nl` directly and takes `option=value` pairs on the command line → used `uno_ampl` throughout. The system-wide `/usr/local/bin/uno_ampl` is broken (missing `libhighs.so.1`); instead the **self-contained UNO v2.8.0 release binaries** (published 2026-07-10) live in `external/uno/`.

### What was built (everything inside OptiUNO/, nothing committed)

- **Setup:** `.gitignore`, `setup.sh`, `.venv/` (openevolve 0.3.1, amplpy + AMPL demo module, numpy, matplotlib), `external/uno/` (v2.8.0 binaries).
- **Test set:** 125 HS-family `.mod` from Vanderbei (about 100 individual URLs are dead on the index — recovered via the bulk `cute.tar.gz`, where names are zero-padded, `hs015.mod` not `hs15.mod`); translated to `.nl` with the AMPL demo license by truncating each model at its `solve;` statement (`scripts/translate_models.py`). **Final set: 123 problems.** Excluded and reported in `models/untranslatable.md`: hs35i/hs76i (dead links, not in the archive), hs068/hs069 (`myerf`/funcadd.c — UNO's ASL crashes: "function myerf not available").
- **Harness:** `harness/uno_runner.py` (subprocess + watchdog, parses status/CPU/evaluations and the composed-method banner), `harness/classify.py` (solved / unsolved / timeout / invalid / crash **plus banner-based silent-override detection**), `harness/benchmark.py` (parallel sweep, config-hash cache, appends to `results/evaluations.csv`).
- **Evolution:** `evolve/initial_program.py` (EVOLVE-BLOCK dict of the six options, filtersqp init), `evolve/evaluator.py` (validates values, sweeps, `combined_score = reliability + 0.1·max(0, 1 − t/60)`, logs every evaluation to `results/evolution_history.csv`), `evolve/config.yaml` (Anthropic OpenAI-compat endpoint, MAP-Elites features = the two objectives), `scripts/run_evolution.py` (`--model`/`OPTIUNO_EVOLVE_MODEL` override, default claude-sonnet-5; `--smoke` for 5 iterations).
- **Analysis:** `scripts/validate_presets.py`, `scripts/variance_runs.py`, `scripts/plot_pareto.py`, partial `results/RESULTS.md`.

### Findings

1. **Uno 2.8.0 accepts `interior_point` + `TR`** — the combination the paper (and our `uno-options.json` `known_invalid_combinations`) records as prohibited in 2.2.0. It instantiates ("TR … primal-dual interior-point method") and fails *algorithmically* on hs015 rather than being rejected. The searchable space is all 240 nominal combinations; the JSON entry needs a version caveat.
2. **`--strategies` banner typo:** the binary prints `LFBGS`, but the accepted option value is `LBFGS` (verified both ways). The manual is right, the banner is wrong. Also resolved: this build has QP/LP = {BQPD, HiGHS}, linear = {MUMPS, SSIDS}; `constraint_relaxation_strategy` really has only `feasibility_restoration`.
3. **Silent-override detection works and fires:** requesting `funnel_method` yields "LS merit …" banners on the 11 unconstrained/bound-only problems — exactly the §5.3.5 rewrite, now measurable per run (`n_rewritten`).
4. **Validation vs arXiv:2406.13454 (tex source in `references/`): PASS.** All 123 problems appear in the paper's per-instance tables; solved/failed agreement 120/123 (97.6%) for both presets; ~50 problems have identical objective-evaluation counts across 2.2.0→2.8.0. Differences: 2.8.0 newly solves hs085/hs114; hs061/hs093 end at infeasible stationary points for us. Caveat: the paper used Neumaier/COCONUT AMPL translations, we use Vanderbei's.
5. **Baselines (123 problems, R=10):** preset filtersqp 0.976 rel / 1.44±0.12 s; preset ipopt 0.984 / 2.58±0.30 s; filtersqp-ingredients-only 0.976 / 1.33 s; **ipopt-ingredients-only only 0.927 / 5.00 s** — the ipopt preset's non-ingredient options carry real weight, so the six-ingredient search lower-bounds what full-option tuning could achieve.
6. **Noise floor:** cumulative-CPU-time sd is 5–15% relative; reliability is exactly reproducible across repetitions (`results/variance.md`).

### Blocked / next

- **The evolution run needs `ANTHROPIC_API_KEY`** (not set in the session environment). Then: `scripts/run_evolution.py --smoke`, full run (150 iterations), `scripts/plot_pareto.py`, `scripts/variance_runs.py --fronts results/front_configs.json`, complete `results/RESULTS.md`.
- Comparison to complete enumeration deliberately deferred (user decision).

---

## 2026-07-13 — Smoke test passed on the subscription (claude-code) backend

Sven asked whether the search can run without an API key, on the Claude subscription. **Yes:** openEvolve 0.3.1 ships a `claude_code` provider that shells out to `claude -p` using the CLI's OAuth session. Wired in as `scripts/run_evolution.py --claude-code` (config `evolve/config-claude-code.yaml`, default model `sonnet`; README updated earlier with general run instructions).

Three obstacles found and fixed on the way:

1. **A stale 7-char `ANTHROPIC_API_KEY` in the environment breaks the CLI** — a set key takes precedence over the claude.ai login, then gets rejected (HTTP 401 from the API; "Invalid API key" from the CLI). The driver now strips the variable from the child environment in `--claude-code` mode. *Sven: consider unsetting/fixing it in the shell profile.*
2. **openEvolve bug:** `ClaudeCodeLLM` passes `--max-budget-usd None` (the per-model `max_budget_usd` defaults to `None`, not the documented 1.0) → every CLI call fails. Mitigation: set `max_budget_usd: 1.0` per-model in the yaml.
3. **openEvolve bug:** the CLI's `--primary-model` override calls `rebuild_models()`, which recreates the model entry with *only* name+weight, silently dropping `max_budget_usd` (and any other per-model field). Mitigation: the driver no longer uses `--primary-model`; it writes `results/openevolve_effective_config.yaml` with the model name substituted and passes that.

**Smoke test (5 iterations, model `sonnet`): PASS.** The LLM genuinely mutated the six-option dict — evaluated configs include reliability 0.935 / 23.6 s and 0.943 / 18.3 s (slower interior-point-flavored variants) alongside the initial filtersqp config (0.976 / 1.33 s, still best after 5 iterations, as expected). MAP-Elites cells populated across islands; checkpointing and best-program tracking work; history in `results/evolution_history.csv`.

**Next:** full run `scripts/run_evolution.py --claude-code` (150 iterations), then `plot_pareto.py` and `variance_runs.py --fronts results/front_configs.json`, and complete `results/RESULTS.md`.

---

## 2026-07-13 — Full 150-iteration search completed; Pareto plots produced

Ran the full openEvolve search (`scripts/run_evolution.py --claude-code`, model `sonnet`, ~1h20m wall). Per Sven's instruction: no variance runs for the evolved configs. All deliverables in `results/`: `evolution_history.csv` (every configuration tried, with reliability and cumulative CPU time), `pareto_evolution.png`, `pareto_final.png` (log time axis), `front_configs.json`, updated `RESULTS.md`; raw UNO logs per config under `results/logs/`.

**Numbers:** 156 evaluations, only **36 distinct configurations** (the LLM re-proposed duplicates; the cache made them free). Front converged after ~39 evaluations.

**Headline findings** (details in `results/RESULTS.md`):
1. Nothing beat the `filtersqp` ingredients on reliability (0.976, 120/123, 1.33 s — the seed config).
2. **New competitive non-preset combination: TR + funnel_method + exact Hessian + no inertia correction** — 119/123 at 1.16 s (~13% faster, −1 problem). The funnel method is in no preset and not in the paper's wheel.
3. **Broken ingredient pair identified:** `primal_dual` inertia correction × `inequality_constrained` (SQP) → "Algorithmic error" on essentially all problems, for every Hessian/globalization tested. The README's "some combinations do not work at all," now with a concrete culprit.
4. The `ipopt` *preset* (0.984, 2.58 s) stays the reliability champion and is unreachable in six-ingredient space (best interior-point ingredient config: 0.943/18.3 s) — the preset's non-ingredient options carry it.
5. Method note: evolutionary search over a 240-point discrete space wastes most of its budget on duplicates — strengthens the case for the deferred complete-enumeration comparison (36/240 already cached).

---

## 2026-07-14 — First Final Results

First complete end-to-end result of the OptiUNO experiment: a full 150-iteration openEvolve search over the six UNO ingredient options (multi-objective: maximize reliability, minimize cumulative CPU time), run on the claude-code subscription backend (model `sonnet`) against the 123-problem Hock–Schittkowski test set, UNO v2.8.0.

### Final Pareto front (reliability ↑, cumulative CPU time ↓)

| Reliability | Cum. CPU | Ingredients (mech / strategy / Hessian / ineq. handling / inertia) |
|---|---|---|
| **0.976** (120/123) | 1.33 s | **TR / fletcher_filter / exact / inequality_constrained / none** (= filtersqp ingredients, the seed) |
| **0.967** (119/123) | 1.16 s | **TR / funnel / exact / inequality_constrained / none** — *new, non-preset* |
| 0.171 (21/123) | 1.01 s | LS / funnel / exact / inequality_constrained / primal_dual |
| 0.163 (20/123) | 0.83 s | LS / fletcher_filter / exact / inequality_constrained / primal_dual |
| 0.000 (0/123) | 0.58 s | TR / waechter_filter / LSR1 / inequality_constrained / primal_dual |

Reference points: preset `filtersqp` 0.976 / 1.44±0.12 s; preset `ipopt` **0.984** / 2.58±0.30 s (R=10, from the earlier variance measurement; per instruction, no variance runs were performed for the evolved configurations).

### Conclusions of this first experiment

1. **No six-ingredient combination beats the filtersqp ingredients on reliability.** The search's genuine discovery is **TR + funnel method** (0.967 / 1.16 s): ~13 % faster at the cost of one problem, a combination that exists in no preset and not even in the paper's strategy wheel.
2. **The `ipopt` preset remains the overall reliability champion (0.984)** and is unreachable within ingredient space — its ~30 non-ingredient option settings (barrier schedule, tolerances) are what carry it. Extending the search space beyond the six ingredients is the obvious follow-up.
3. **`primal_dual` inertia correction × inequality-constrained SQP is a dead region** — "Algorithmic error" on essentially every problem regardless of the other ingredients. These configs fail *fast*, which is why they populate the low-reliability tail of the front.
4. **Search-method observation:** 156 evaluations produced only 36 distinct configurations, and the front converged after ~39 evaluations — on a 240-point discrete space, the evolutionary driver spends most of its budget re-proposing duplicates. This strengthens the case for the deferred complete enumeration (36/240 combos already cached, reusable).

### Deliverables (all under `results/`)

- `evolution_history.csv` — all 156 evaluations: config JSON, reliability, cumulative CPU time, combined score, status counts, in evaluation order.
- `pareto_evolution.png`, `pareto_final.png` — front over evolution progress; final front vs. presets (log time axis), both visually verified.
- `front_configs.json` — the front configurations, machine-readable (input for later variance runs / enumeration comparison).
- `RESULTS.md` — full write-up (setup, validation, baselines, findings, caveats).
- `logs/<config-hash>/<problem>.log` — raw UNO logs for every run.
