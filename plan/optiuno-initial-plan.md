# OptiUNO — Initial Project Plan

> Status: **planning only — not approved for implementation.** Saved for further
> planning before any code is written.

## Context

OptiUNO aims to discover UNO strategy configurations that beat its hand-picked
`presets`. UNO composes a solver at runtime from strategy building blocks; the
option keys are the search variables and a performance metric over a benchmark
set is the objective. The repo is currently planning-only (README + paper), so
this plan scaffolds the first end-to-end experiment pipeline from scratch.

**Key facts established during research (drive the design):**
- `unopy` (`pip install unopy`, Python 3.10+) solves models built from **Python
  callbacks** via `unopy.Model` + `UnoSolver`. Options are set with
  `set_preset(name)` and `set_option(key, value)`, then `optimize(model)`.
  Results expose `optimization_status`, `solution_objective`, `number_iterations`,
  `cpu_time`, `number_subproblems_solved`, and feasibility measures. Reference:
  `interfaces/Python/example/example_hs015.py` in the UNO repo.
- **Search variables** (the "run-time-options"): `constraint_relaxation_strategy`,
  `inequality_handling_method` (`interior_point` | `inequality_constrained`),
  `globalization_mechanism` (`LS` | `TR`), `globalization_strategy`
  (`fletcher_filter_method` | `waechter_filter_method` | `funnel_method` | merit),
  `hessian_model` (`exact` | `LBFGS` | `identity` | `zero`),
  `inertia_correction_strategy` (`primal` | `primal_dual` | `none`).
- **Feasibility is structured**: presets show consistent combos, e.g. IPOPT =
  `interior_point` + `LS` + `waechter_filter_method` + `primal_dual`; filterSQP =
  `inequality_constrained` + `TR` + `fletcher_filter_method` + `none`. Many
  cross-combinations are invalid and must be excluded before searching.

## Decisions (confirmed with user)
- **Test problems**: start with a **hand-coded Hock-Schittkowski subset** (callbacks,
  like `hs015`); wire CUTEst→callbacks later.
- **Two independent runscripts**: an **enumeration** driver and an **openEvolve**
  driver, sharing the same core runner. Enumeration results validate openEvolve.
- **Metric**: **robustness then speed** — lexicographic (maximize # solved, then
  minimize CPU time).

## Rules to honor (from CLAUDE.md)
- Do not commit (user commits manually). Do not modify UNO source. Do not modify
  the environment — only check for `unopy`/`openevolve` and *suggest* installs.
  Stay within `OptiUNO/`. Update `LOGBOOK.md` (append) and `STATUS.md` (overwrite)
  at session end.

## Proposed layout
```
OptiUNO/
  problems/            # hand-coded HS problems as callback modules
    __init__.py        # PROBLEMS registry: name -> builder returning unopy.Model + known optimum
    hs015.py           # first problem, ported from the unopy example
    ...                # a handful more (e.g. hs001, hs071)
  optiuno/
    runner.py          # core: run ONE (problem, config) -> normalized result dict
    config_space.py    # option keys/values + feasibility rules (infeasible combos)
    metrics.py         # robustness-then-speed scoring/aggregation
  run_enumeration.py   # driver 1: sweep feasible configs x problems -> results table
  run_openevolve/      # driver 2: initial_program.py, evaluator.py, config.yaml
  results/             # CSV/JSON outputs (git-ignored or committed by user)
```

## Steps

### 1. Test set — hand-coded HS subset (`problems/`)
- Port `hs015` from `interfaces/Python/example/example_hs015.py` into
  `problems/hs015.py` as a builder returning a configured `unopy.Model` plus its
  known optimum and a solve tolerance.
- Add a few more HS problems (mix of sizes / constraint types) and register them
  in `problems/__init__.py` (`PROBLEMS = {name: builder}`).
- Each builder is solver-agnostic (no options set) so both drivers reuse them.

### 2. Core runscript with unopy (`optiuno/runner.py`)
- `run_case(problem_builder, config_dict) -> result` that: builds the model,
  creates `UnoSolver`, applies `config_dict` via `set_option`/`set_preset`, calls
  `optimize`, and returns a normalized dict: `status`, `objective`, `iterations`,
  `cpu_time`, `subproblems`, and a `solved` bool (status OK **and**
  `|objective - known_opt| <= tol`).
- `run_case` is the atomic unit of work: ONE problem solved under ONE config.
  Both drivers are loops over it (enumeration sweeps configs×problems; the
  openEvolve evaluator calls it per problem for the one evolved config). The
  problem is a solver-agnostic builder; the config is a dict of option key→value
  (a preset name is shorthand). Raw per-(problem,config) results are preserved;
  aggregation happens later in `metrics.py`.
- Wrap `optimize` defensively: catch exceptions/nonzero status and per-case
  timeout so a bad config yields `solved=False` rather than crashing the sweep.
- Add a startup check that `unopy` imports; if missing, print a suggested
  `pip install unopy` (do **not** install).

### 3. Feasible config space + exclusions (`optiuno/config_space.py`)
Infeasibility is tracked in **two layers**, both traceable (every exclusion carries
a `source` and a human-readable `reason` — no silent dropping):

**Layer 1 — a priori rules (structural).** Encode each option key and its allowed
values, then express compatibility constraints as **predicates with reason
strings** (not an enumerated blacklist), derived from the presets/paper, e.g.
`interior_point` ⇒ `LS` + `waechter_filter_method` + `primal_dual` (+ barrier);
`inequality_constrained` ⇒ inertia `none` + filter/funnel; `hessian_model=zero` ⇒
SLP-style only.
- `infeasible_reasons(config) -> [reasons]`; `feasible_configs()` yields the
  Cartesian product minus rule violations.
- **Validation guard**: assert the four known presets (`filtersqp`, `ipopt`,
  `funnelsqp`, `filterslp`) all pass the rules — a rule that excludes a real preset
  is a bug, caught at startup.

**Layer 2 — empirical exclusions (discovered by running).** Some combos error in
ways the rules can't predict. A config that **fails on 100% of problems**
(conservative threshold — partial failures stay in the results table, since
class-specific success is scientifically relevant) is promoted to a persisted
ledger `results/infeasible.json`, each record = `{config, source:"rule"|"empirical",
reason, detail?}`.
- Both drivers read the ledger at startup to skip known-dead configs; the
  openEvolve evaluator also appends newly discovered all-fail configs.
- Drivers print a summary: *N feasible, M excluded (K by rule, L empirical)*.
- **Infeasible ≠ lost**: a config that solves some problems but is slow/worse is
  kept in results with a poor score, never added to the ledger.

### 4a. Enumeration driver (`run_enumeration.py`)
- Sweep `feasible_configs() × PROBLEMS`, call `run_case`, write a tidy results
  table to `results/enumeration.csv` (one row per config×problem).
- This is the ground-truth ranking used to check openEvolve.

### 4b. openEvolve driver (`run_openevolve/`)
- `evaluator.py` maps an evolved config → calls the shared `runner`/`metrics` over
  the problem set → returns `{combined_score, solved_count, mean_cpu_time}`.
- `initial_program.py` seeds a known-good preset config; `config.yaml` sets
  iterations and the LLM backend.
- Check `openevolve` import; if missing, suggest `pip install openevolve` and note
  it needs an LLM API key (do not install/configure).

### 5. Metrics & selection (`optiuno/metrics.py`)
- Aggregate per-config across problems: primary = **# solved** (robustness),
  secondary = **total/mean CPU time** over solved problems (speed); expose
  `number_iterations`/`subproblems` as machine-independent cross-checks.
- `combined_score` for openEvolve encodes the same lexicographic preference
  (e.g. `solved_count` dominant term + small speed bonus) so both drivers optimize
  the same objective.
- Provide a `rank_configs()` helper and a short comparison of the enumeration
  winner vs. the openEvolve winner vs. the stock presets.

## Verification
- **Smoke test**: run `run_case` on `hs015` with the `filtersqp` preset; assert
  `solved=True` and `objective ≈ 306.5` (matches the unopy example) — confirms the
  unopy wiring end-to-end.
- **Feasibility check**: print `feasible_configs()` count and the excluded list;
  spot-check that the four known presets are all in the feasible set.
- **Enumeration run**: execute `run_enumeration.py` on the small problem set and
  inspect `results/enumeration.csv` — every row has a status and finite/`NaN` time;
  no crash on infeasible configs.
- **openEvolve dry run**: a few iterations; confirm the evaluator returns scores
  and the best-found config appears in the enumeration table with a comparable
  score (cross-validation between the two drivers).
- If `unopy`/`openevolve` aren't installed, verification stops at the import-check
  stage and reports the suggested install commands (per environment rule).

## Out of scope for this first pass
CUTEst→callback bridge, multi-objective handling, per-problem-class specialization,
and statistical timing robustness — noted for later iterations.
