# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Scope: this file documents the **`quickRun/` subproject**. The project-wide rules
(never commit, never modify UNO source, never modify the environment, stay inside
`OptiUNO/`, session logging) live in the parent `../CLAUDE.md` and still apply here.

## What `quickRun/` is

A self-contained OptiUNO experiment pipeline: use **openEvolve** (LLM-driven
evolutionary search) to find UNO run-time configurations that maximize
**reliability** (fraction of problems solved) while minimizing **cumulative CPU
time**, over a 123-problem Hock–Schittkowski test set, using a bundled UNO
v2.8.0 binary. The search space is UNO's **six "ingredient" options** only.

This is distinct from the root-level tooling (`../scripts/`, `../problems/CUTE/`),
which scrapes and converts the separate 727-problem COCONUT/CUTE corpus and uses
the *system* UNO binary via `$UNO_AMPL_BIN`. `quickRun/` does not depend on it.

## Architecture (data flow)

The pipeline is layered; each layer only knows the one below it:

1. `../optiuno/uno_runner.py` — `run_uno(nl, options, ..., uno_bin=..., time_limit=...)`:
   one `option=value` subprocess call to `uno_ampl`, regex-parses status/objective/CPU/
   iterations and the **composed-method banner**, returns a typed `UnoResult`. Stdlib-only.
   Never raises on a solver failure. This is the single merged driver (the old
   `harness/uno_runner.py` and `scripts/uno_runner.py` were merged into it); it resolves
   the binary via `uno_bin`/`$UNO_AMPL_BIN`/PATH and auto-adds the bundled `lib`/`deps` to
   `LD_LIBRARY_PATH` when it sees the `external/uno` release layout. `benchmark.py` imports
   it (adding the repo root to `sys.path`) and passes `uno_bin=external/uno/bin/uno_ampl`.
2. `harness/classify.py` — turns one result into `{category, rewritten, detail}`.
   Categories: `solved` / `unsolved` / `timeout` / `invalid` / `crash`.
   **Key idea:** `uno_ampl` exits 0 even on failed solves, so classification keys
   off the printed `Optimization status:` / `Solution status:`, not the exit code.
   `rewritten_ingredients()` parses UNO's banner back into ingredients and flags
   the **silently-rewritten** case (run succeeds but tested a *different* config
   than requested — the dangerous case; see the paper's §5.3.5).
3. `harness/benchmark.py` — `evaluate_config(options)`: sweeps one config over all
   `.nl` problems (ThreadPool, 8 workers), aggregates `reliability`, `cum_cpu_time`,
   `n_rewritten`, per-problem rows. **Config-hash cache** (`harness/cache/*.json`,
   keyed by `sha1(options+time_limit)[:12]` + `_r<rep>`): only ~240 distinct
   ingredient combinations exist, so evolution and enumeration share evaluations.
4. `evolve/evaluator.py` — the openEvolve entry point. Imports `UNO_CONFIG` from the
   evolved program, **validates** it against `ALLOWED` (rejects unknown keys/values
   → score 0), calls `evaluate_config`, returns `{combined_score, reliability,
   cum_cpu_time}` + artifacts (unsolved list, silent-rewrite count). Appends every
   evaluation to `results/evolution_history.csv`. `combined_score = reliability +
   0.1·max(0, 1 − cum_cpu_time/60)` (reliability dominates, CPU time breaks ties).
5. `evolve/initial_program.py` — the **only** thing openEvolve mutates: a 6-key dict
   between `EVOLVE-BLOCK-START/END`, seeded with the `filtersqp` ingredients. Legal
   values are documented in its comments *and* enforced by `evaluator.ALLOWED`.

The six ingredients and their legal values (also in `results/quickRun/uno-options.md`):
`constraint_relaxation_strategy` (only `feasibility_restoration`),
`inequality_handling_method` (`inequality_constrained`|`interior_point`),
`hessian_model` (`exact`|`LBFGS`|`LSR1`|`identity`|`zero`),
`inertia_correction_strategy` (`primal`|`primal_dual`|`none`),
`globalization_mechanism` (`TR`|`LS`), `globalization_strategy`
(`merit_function`|`fletcher_filter_method`|`waechter_filter_method`|`funnel_method`).

## Path convention & what is / isn't committed

Every script sets `ROOT = <quickRun>/` and reads/writes **relative to it**:
`models/nl/*.nl`, `results/`, `harness/cache/`, `references/`.

Committed: `evolve/`, `harness/*.py`, `harness/cache/` (75 cached evaluations),
`scripts/`, and `external/uno/` (the entire self-contained v2.8.0 binary + libs).

**NOT committed — must be recreated before a run:**
- `.venv/` — no `setup.sh` is committed; create a venv and install
  `openevolve` (0.3.1), `amplpy`, `numpy`, `matplotlib`, `pyyaml`. `amplpy` needs
  the AMPL `base` engine module and a license that permits `write` (**AMPL for
  Academics**, not Community Edition — CE blocks `write`). *Suggest* these to the
  user; do not install them yourself (parent rule).
- `models/mod/*.mod` + `models/nl/*.nl` — the HS test set. Source `.mod` files come
  from Vanderbei (many index links are dead; recovered via the bulk `cute.tar.gz`,
  zero-padded names). `scripts/translate_models.py` produces `models/nl/`.
- `references/arxiv-2406.13454/…/statistics_table.tex` — needed only by
  `validate_presets.py`.
- `results/` — the code writes here, but the **finished outputs are checked in one
  level up at `../results/quickRun/`** (RESULTS.md, evaluations.csv,
  evolution_history.csv, pareto plots, preset_validation.md, uno-options.md). Read
  those for prior findings; a fresh run regenerates them under `quickRun/results/`.

## Commands

All scripts assume the venv Python and are run from `quickRun/`:

```bash
# 0. (one-time) translate Vanderbei .mod -> .nl  (needs models/mod + amplpy)
.venv/bin/python scripts/translate_models.py      # -> models/nl/, models/untranslatable.md

# 1. sanity-check the harness against the published paper (arXiv:2406.13454)
.venv/bin/python scripts/validate_presets.py      # -> results/preset_validation.md

# 2. run the evolutionary search (two LLM backends)
#    a) Anthropic API  (needs $ANTHROPIC_API_KEY)   default model claude-sonnet-5
.venv/bin/python scripts/run_evolution.py [--model NAME] [--iterations N] [--smoke]
#    b) Claude Code CLI subscription (no API key; OAuth)   default model "sonnet"
.venv/bin/python scripts/run_evolution.py --claude-code
#    --smoke = 5-iteration end-to-end test. Baselines (both presets) are always
#    evaluated first so every plot has reference points.

# 3. plots + variance
.venv/bin/python scripts/plot_pareto.py           # -> results/pareto_*.png, front_configs.json
.venv/bin/python scripts/variance_runs.py --reps 10 [--fronts results/front_configs.json]

# run one config manually (library or CLI)
.venv/bin/python -c "from harness.benchmark import evaluate_config; print(evaluate_config({'preset':'ipopt'}))"
```

`run_evolution.py` writes an *effective* config (`results/openevolve_effective_config.yaml`)
with the chosen model substituted, then invokes `.venv/bin/openevolve-run` — it does
**not** use openEvolve's `--primary-model` flag (that path drops per-model fields like
`max_budget_usd`, which the `claude` CLI then rejects as the literal string "None").

## Gotchas established by prior runs (see ../results/quickRun/ + ../LOGBOOK.md)

- **UNO 2.8.0 accepts `interior_point` + `TR`** (the 2.2.0 paper prohibited it), so all
  240 nominal ingredient combinations are runnable; invalid/rewritten/failed configs
  are caught by the harness, not by refusing to run.
- **Dead region:** `inertia_correction_strategy=primal_dual` × `inequality_constrained`
  → "Algorithmic error" on essentially every problem. Fails *fast*.
- **Silent rewrite:** requesting a filter/funnel strategy on the ~11 unconstrained/
  bound-only problems is rewritten to `LS merit_function` (counted as `n_rewritten`);
  strategy comparisons are effectively over the ~112 constrained problems.
- **The six-ingredient search is a lower bound.** The `ipopt` *preset* (0.984 rel)
  beats its bare ingredients (0.927) because ~30 non-ingredient options (barrier
  schedule, tolerances) carry it — those are outside the current search space.
- **CPU-time noise** is 5–15% relative sd; reliability is noise-free. Pareto points
  within ~0.3 s are statistically indistinguishable.
- The evolutionary driver re-proposes duplicates heavily (156 evals → 36 distinct
  configs); the config-hash cache makes repeats free. Complete enumeration over the
  ~240-point space is the deferred fallback.
