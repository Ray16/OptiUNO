# Status

_Last updated: 2026-07-23 (dissolved the `quickRun/` subproject into the existing top-level
dirs: the openEvolve harness + engine now live under `optiuno/harness/` + `optiuno/evolve/`,
its 5 scripts under `scripts/`, and its data under `results/quickRun/{cache,openevolve_run}/`)_

## Current state

The CUTE benchmark is fully prepared (scraped + converted to `.nl` in two variants), the **UNO
Python driver** exists, and a **reusable, search-driver-agnostic black-box evaluator** exists
too: `optiuno.objective.evaluate(config, problem_set) -> (reliability, cum_cpu_time)`. Two
search drivers run on top of the objective/harness: an **NSGA-II GA** (`scripts/ga_search.py`)
and the **openEvolve** LLM-driven search (`scripts/run_evolution.py` over `optiuno/evolve/` +
`optiuno/harness/`). Complete enumeration over the ~240-point ingredient space remains the
ground-truth fallback.

- `problems/CUTE/` — **727** COCONUT Library2 CUTE problems, one folder per problem. Each folder
  has: `.mod` (always), `.gms`/`.dag`/`.res` (when available), a `metadata.json`, and **two
  generated `.nl` files**:
  - **`<name>.nl`** — AMPL presolve **OFF**: the faithful, unsimplified problem. **Primary file
    for benchmarking.**
  - **`<name>_presolve.nl`** — AMPL presolve **ON**: the reduced problem. (Faithful vs. presolved
    differ for 65 problems; identical for 662.)
  - `in_uno_429_subset` flags the 425 problems in UNO's small subset; `feasible`: 510 true / 8
    false / 209 unknown.
- `problems/CUTE/summary.csv` — per-problem metadata + feasibility + subset flag + per-file
  availability.
- `problems/CUTE/nl_conversion_report.csv` — last conversion run's per-problem result.
- `problems/HS_model/` — the **121-problem HS test set** (`.nl` files) used by the openEvolve/GA
  search and by the evaluator's example set. (`translate_models.py` regenerates it from
  user-provided Vanderbei `.mod` sources expected at `problems/HS_model/mod/`.)
- `problems/sets/` — **problem-set JSON files** (the input format the black-box evaluator reads):
  - `hs_model_all.json` — all 121 HS stems (`base_dir: problems/HS_model`, flat layout).
  - `cute_uno_subset.json` — UNO's benchmark subset present in CUTE: **425** problems.
  - `cute_all.json` — all **727** CUTE problems (full nested `.nl` paths).

## `optiuno/` package (the shared library)

Imported by everything. `uno_runner.py`, `utils.py`, and `objective.py` are stdlib-only; the
`harness/` + `evolve/` subpackages add the openEvolve dependencies. The old cross-project
dependency arrow (`quickRun → optiuno`) is now internal: `harness`/`evolve` depend on
`uno_runner`/`utils`; `objective.py` stays deliberately import-light and does **not** import the
harness.

- `optiuno/uno_runner.py` — `run_uno(nl, options=, preset=, uno_bin=, time_limit=) -> UnoResult`.
  One `uno_ampl` subprocess; regex-parses status/objective/CPU/iterations + the composed banner;
  never raises on a solver failure. Also a CLI (`python -m optiuno.uno_runner`).
- `optiuno/utils.py` — `select_uno_bin` (system-first), `bundled_uno_bin` (pins
  `external/uno/bin/uno_ampl`), and `REPO_ROOT`.
- `optiuno/objective.py` — the black-box objective for external optimizers:
  `evaluate(config, problem_set, *, time_limit=20, workers=8, uno_bin=None, ...)` →
  `(reliability, cum_cpu_time)`, plus `evaluate_detailed()`, `load_problem_set()`, `is_solved()`,
  `make_objective()`. Config is validated against `uno_search_space.json`. `extra_options` kwarg
  injects fixed unvalidated UNO options (e.g. `linear_solver=MA27`). CLI:
  `python -m optiuno.objective --problems SET.json --option k=v ...`.
- **`optiuno/harness/`** — the **openEvolve evaluation core** (moved from `quickRun/harness/`):
  - `benchmark.py` — `evaluate_config(options)` sweeps one config over all HS `.nl` problems
    (ThreadPool, 8 workers) via `run_uno`, aggregating `reliability`/`cum_cpu_time`/`n_rewritten`
    + per-problem rows. **Config-hash cache** at `results/quickRun/cache/*.json` (keyed by
    `sha1(options+time_limit)[:12]` + `_r<rep>`) so evolution/enumeration/variance share evals.
    Reads the test set from the repo-root `problems/HS_model/`; pins the bundled UNO build.
  - `classify.py` — turns one `UnoResult` into `solved`/`unsolved`/`timeout`/`invalid`/`crash`
    (keying off the printed status, not the exit code) and flags silently-rewritten configs from
    the composed-method banner.
- **`optiuno/evolve/`** — the **openEvolve search space + entry points** (moved from
  `quickRun/evolve/`): `initial_program.py` (the six-key `UNO_CONFIG` in the `EVOLVE-BLOCK`, the
  only thing mutated), `evaluator.py` (validates against `ALLOWED`, calls `evaluate_config`,
  returns `combined_score = reliability + 0.1·max(0, 1 − cum_cpu_time/60)` + artifacts, appends
  to `results/quickRun/openevolve_run/evolution_history.csv`), and `config.yaml` /
  `config-claude-code.yaml` (LLM + search-algorithm settings only — no paths, no search space).
  openEvolve loads `evaluator.py`/`initial_program.py` **by file path**, so `evaluator.py` puts
  the repo root on `sys.path` and imports `optiuno.harness.benchmark` absolutely.
- **`optiuno/uno_config_options.json`** / **`optiuno/uno_search_space.json`** — machine-readable
  option catalogues (all 89 options; the six searchable ingredients → legal values, matching
  `optiuno/evolve/evaluator.py:ALLOWED`).

## Tooling (`scripts/`) — standalone CLIs, run from the repo root

- `scrape_cute.py` — the corpus scraper (polite + resumable).
- `problem_parser.py` — the CUTE `.mod`→`.nl` converter via `amplpy` (`--presolve` flag).
- `ga_search.py` — NSGA-II (pymoo) bi-objective search over the six ingredients, scoring configs
  with `optiuno.objective`. Objectives: reliability (max) vs. cumulative UNO time (min). Evaluates
  all four UNO presets as baselines; every results CSV leads with a `preset` column; streams one
  line per population member; writes timestamped artifacts to
  `results/ga_<...>/<timestamp>/`. Needs pymoo + numpy + matplotlib (dev: conda env
  `sequential_OED`). `--uno-bin` / `--option KEY=VALUE` for HSL builds.
- **openEvolve pipeline** (moved from `quickRun/scripts/`):
  - `run_evolution.py` — drives `openevolve-run` over `optiuno/evolve/` (two LLM backends: the
    Claude Code CLI subscription by default, `--api` for the Anthropic API). Evaluates the preset
    baselines first; writes an effective config + all outputs under
    `results/quickRun/openevolve_run/`.
  - `plot_pareto.py` — Pareto-front figures + `front_configs.json` from the evolution history.
  - `validate_presets.py` — harness sanity-check vs. the published paper tables (reads
    `References/arxiv-2406.13454/sections/statistics_table.tex`, user-provided).
  - `variance_runs.py` — repeated sweeps to estimate CPU-time noise.
  - `translate_models.py` — one-time Vanderbei `.mod`→`.nl` (`problems/HS_model/mod/` →
    `problems/HS_model/`).

## Environment / conventions

- **Python environment:** no venv is committed. Scripts run under whatever Python you invoke them
  with; the dev environment is the conda env `sequential_OED` (holds `openevolve`, `amplpy`,
  `numpy`, `matplotlib`, `pyyaml`, `pymoo`, `requests`, `bs4`, `pandas`). Other users create their
  own env — detailed install instructions are future work.
- `amplpy` 0.17.0 + AMPL `base` engine, licensed with **AMPL for Academics** (allows `write`).
  Do NOT switch to AMPL **Community Edition** — it blocks `write`.
- **UNO binary selection** (`optiuno/utils.py:select_uno_bin`): **system-first** — `explicit`/
  `--uno-bin` → `$UNO_AMPL_BIN` → `uno_ampl` on PATH → the **bundled** build as a fallback.
- **Bundled UNO v2.8.0** at `external/uno/bin/uno_ampl` (self-contained, ~99 MB). Used as the
  fallback and pinned by `optiuno/harness/benchmark.py` + `optiuno.objective.evaluate` for
  reproducibility. `run_uno` auto-wires `LD_LIBRARY_PATH` from the binary's `lib/`+`deps/`.
- **Linear solvers / HSL:** the bundled build advertises only **MUMPS, SSIDS** (its `libhsl.so`
  is a stub). The user's build at **`/home/sdinh/sandbox/Uno/build/uno_ampl`** has real HSL
  (MA57, MA27, MUMPS, SSIDS). Select it with `--uno-bin` / `$UNO_AMPL_BIN` + `linear_solver=MA27`.
- **Threading:** UNO multithreads via OpenMP + OpenBLAS, defaulting to all cores; CPU time ≫ wall
  time on threaded solves. `ga_search`'s `--time-source wall` measures honest elapsed time.
- UNO strategy blocks / option values: `uno_ampl --strategies`; all options: `uno_ampl
  --dump-options`. (Or read the JSON catalogues in `optiuno/`.)

## Next steps

- **Search driver over the black box.** GA (`ga_search.py`) and openEvolve (`run_evolution.py`)
  both run; remaining work is comparing them against complete enumeration (~240-point space) and
  settling the bi-objective handling (scalarize / Pareto / constrained).
- **openEvolve known open issue:** openEvolve reported "No valid diffs found in response" on some
  smoke iterations (LLM/diff-format layer needs a follow-up).
- **Optional refactor:** have `optiuno/harness/benchmark.py:evaluate_config` delegate to
  `optiuno.objective` so there is a single evaluation core (deferred; not required).

## Knowledge base (`.crucible/`)

- Query with `crucible search "..."` / `crucible concept openevolve` (always `cd
  /home/sdinh/sandbox/OptiUNO` first). Covers openevolve, alphaevolve, and UNO strategy topics.

## Git

- The `quickRun/` subproject was dissolved into the existing dirs (code → `optiuno/harness`,
  `optiuno/evolve`, `scripts/`; data → `results/quickRun/{cache,openevolve_run}/`); paths/imports
  repointed; `.gitignore` cleaned (the ~2049 stale `quickRun/` entries removed, replaced with
  three rules for the new live-write locations). The moves are **staged, not committed** — commit
  manually (project rule: only the user commits).
- The old broken `quickRun/.venv/` was removed in a prior commit; `.venv/`/`__pycache__/`/`*.pyc`
  stay ignored.
- Still to decide: git tracking for the large `.nl` corpus (regenerates from `.mod`).
