# Status

_Last updated: 2026-07-15 (all four UNO presets as GA baselines + `preset` column in every results CSV; CUTE sets; GA tic-toc timing + overhead; live per-member output; selectable HSL/MA27 binary)_

## Current state

The CUTE benchmark is fully prepared (scraped + converted to `.nl` in two variants), the **UNO
Python driver** exists, and a **reusable, search-driver-agnostic black-box evaluator** now exists
too: `optiuno.objective.evaluate(config, problem_set) -> (reliability, cum_cpu_time)`. This is the
core building block the batch/search harness needs — the remaining milestone is choosing and
wiring a search driver (Bayesian optimization / GA / enumeration) on top of it.

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
- `problems/HS_model/` — the **121-problem HS test set** (`.nl` files) used by the `quickRun`
  experiment and by the new evaluator's example set.
- `problems/sets/` — **problem-set JSON files** (the input format the black-box evaluator reads):
  - `hs_model_all.json` — all 121 HS stems (`base_dir: problems/HS_model`, flat layout).
  - `cute_uno_subset.json` — **NEW.** UNO's benchmark subset present in CUTE: **425** problems
    (the 429 `small_instances` minus 4 absent from Library2). Full nested `.nl` paths.
  - `cute_all.json` — **NEW.** All **727** CUTE problems. Full nested `.nl` paths.
  - CUTE sets use full `problems/CUTE/<name>/<name>.nl` paths (no `base_dir`) because the CUTE
    corpus is one-folder-per-problem, not the flat layout `base_dir`+stem assumes.

## `optiuno/` package (the shared, stdlib-only library)

Imported by everything; depends on nothing in `quickRun/` (the dependency arrow is one-way,
`quickRun → optiuno`).

- `optiuno/uno_runner.py` — `run_uno(nl, options=, preset=, uno_bin=, time_limit=) -> UnoResult`.
  One `uno_ampl` subprocess call; regex-parses status/objective/CPU/iterations + the composed
  banner; never raises on a solver failure. Also a CLI (`python -m optiuno.uno_runner`).
- `optiuno/utils.py` — `select_uno_bin` (system-first: explicit → `$UNO_AMPL_BIN` → PATH →
  bundled), `bundled_uno_bin` (pins `external/uno/bin/uno_ampl`), and `REPO_ROOT`.
- **`optiuno/objective.py`** — the black-box objective for external optimizers:
  - `evaluate(config, problem_set, *, time_limit=20, workers=8, uno_bin=None, validate=True,
    time_source="cpu")` → `(reliability, cum_cpu_time)`. **reliability** = fraction in [0,1]
    solved (strict: `Optimization status: Success` **and** `Solution status: Feasible KKT
    point`). **cum_cpu_time** = sum of per-problem times; a timeout charges the full
    `time_limit`. **`time_source`** picks the time metric: `"cpu"` (UNO-reported CPU seconds,
    default — parallelism-invariant) or `"wall"` (real tic-toc `perf_counter` around each
    solve; keep `workers=1` so the sum reflects serial elapsed time). Binary defaults to the
    bundled build for reproducibility.
  - `evaluate_detailed()` (rich dict; also returns `cum_wall_time` = raw tic-toc sum,
    `time_source`, and per-problem `wall_time`), `load_problem_set()` (JSON path / list /
    `{base_dir, problems}` object; fail-fast on missing files), `is_solved()`, and
    `make_objective(problem_set, *, time_source=...) -> (config -> (rel, time))`.
  - **`extra_options`** kwarg (all of `evaluate`/`evaluate_detailed`/`make_objective`; CLI
    `--extra-option KEY=VALUE`): fixed UNO options merged into every solve, **outside the
    search space and unvalidated** (UNO checks them) — e.g. `linear_solver=MA27`. Combine
    with `uno_bin=`/`--uno-bin` to run an HSL-enabled UNO build.
  - Config is validated against `uno_search_space.json` (unknown key / illegal value → ValueError);
    bad *combinations* of legal values are NOT rejected — they run and show as low reliability.
  - CLI: `python -m optiuno.objective --problems SET.json --option k=v ... [--time-source wall] [--json]`.
- **`optiuno/uno_config_options.json`** / **`optiuno/uno_search_space.json`** — **NEW.**
  Machine-readable option catalogues built by probing the bundled binary. The first documents all
  89 options (types, defaults, solvers, presets, invalid-combo caveats); the second is just the
  six searchable ingredients → legal values (matches `quickRun/evolve/evaluator.py:ALLOWED`).
  Note: `--strategies` misprints the Hessian model as `LFBGS`; the parser accepts `LBFGS` (the
  catalogues use the accepted spelling).

## Tooling (`scripts/`)

- `scrape_cute.py` — the corpus scraper (polite + resumable).
- `problem_parser.py` — the `.mod`→`.nl` converter via `amplpy`. `--presolve` flag (default OFF)
  selects the faithful vs. reduced variant. Updates `metadata.json` + `summary.csv`.
- `ga_search.py` — NSGA-II (pymoo) bi-objective search over the six ingredients, scoring configs
  with `optiuno.objective`. Objectives: reliability (max) vs. cumulative UNO time (min). Time is
  the real **tic-toc wall clock** by default (`--time-source wall`; `cpu` for UNO-reported CPU),
  and solves run **serially by default** (`--workers 1`, no parallel pool) so the run can report
  **GA overhead = run wall clock − time spent inside UNO** (written to `timing.json` + a RESULTS
  section; only meaningful at `workers=1`). **Baselines:** evaluates **all four** UNO built-in
  presets — `filtersqp`, `ipopt`, `funnelsqp`, `filterslp` (as six-ingredient configs;
  `PRESET_INGREDIENTS` mirrors `Uno/uno/options/Presets.cpp`) — so every plot / RESULTS table has
  the full preset reference set. **`preset` column:** every results CSV (`evaluations.csv`,
  `ga_history.csv`, `pareto_front.csv`) now leads with a `preset` column via `match_preset()` —
  the built-in preset whose six ingredients the config matches, or `custom` (so a GA-*discovered*
  config equal to a preset bundle is labelled with that preset's name). **Streams one line per
  population member live** as each config finishes (reliability, time, `solved=n/N`, per-config
  `eval_wall`, config; cache hits tagged `(cached)`), with a summary line at each generation's
  end; `--no-population` = summary only, `--quiet` = silent (all off by default). Writes
  timestamped artifacts
  (evaluations/history CSVs, Pareto front, plots, `timing.json`, `RESULTS.md`) to
  `results/ga_pop_<pop_size>_gen_<generations>_<set>/<timestamp>/` (override with `--out`). Needs
  an interpreter with pymoo + numpy + matplotlib (dev: conda env `sequential_OED`). **Binary:** `--uno-bin` (default system-first
  via `select_uno_bin`: `$UNO_AMPL_BIN` → PATH → bundled); **fixed options:** `--option
  KEY=VALUE` (repeatable, e.g. `--option linear_solver=MA27`), with a preflight that fails fast
  if the requested `linear_solver` isn't advertised by the chosen binary.
- The UNO driver lives in `optiuno/uno_runner.py` (see above), not in `scripts/`.

## Environment / conventions

- **Python environment:** no venv is committed (the old broken `quickRun/.venv/` was removed).
  Scripts run under whatever Python you invoke them with; the dev environment is the conda env
  `sequential_OED` (holds `openevolve`, `amplpy`, `numpy`, `matplotlib`, `pyyaml`, `pymoo`,
  `requests`, `bs4`, `pandas`). Other users create their own env with the packages each script
  needs — detailed install instructions are future work.
- `amplpy` 0.17.0 + AMPL `base` engine, licensed with **AMPL for Academics** (allows `write`, no
  size cap). Do NOT switch to AMPL **Community Edition** — it blocks `write`.
- **UNO binary selection** (`optiuno/utils.py:select_uno_bin`): **system-first** — `explicit`/
  `--uno-bin` → `$UNO_AMPL_BIN` → `uno_ampl` on PATH → the **bundled** build as a fallback. A
  locally built binary can be selected with `export UNO_AMPL_BIN=/path/to/uno_ampl`.
- **Bundled UNO v2.8.0** at the repo root, `external/uno/bin/uno_ampl` (self-contained binary +
  `lib/` + `deps/`, ~99 MB). Used automatically as the fallback and pinned by
  `quickRun/harness/benchmark.py` and `optiuno.objective.evaluate` for reproducibility.
  `run_uno` auto-wires `LD_LIBRARY_PATH` from the binary's own `lib/`+`deps/`.
- **Linear solvers / HSL:** the bundled build advertises only **MUMPS, SSIDS** — its
  `deps/libhsl.so` is a non-functional 18 KB Julia HSL_jll **stub**, so `linear_solver=MA27`
  fails ("unknown"). The user's own build at **`/home/sdinh/sandbox/Uno/build/uno_ampl`** is
  compiled with real HSL (`.../Uno/dependencies/lib/libcoinhsl.so`) and advertises
  **MA57, MA27, MUMPS, SSIDS**. Select it with `--uno-bin` / `$UNO_AMPL_BIN` and pass
  `--option linear_solver=MA27` (ga_search) or `--extra-option linear_solver=MA27` (objective).
- **Threading:** UNO has no thread option; it multithreads via OpenMP (libgomp) + OpenBLAS,
  defaulting to **all cores** unless `OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS` are set
  (OpenMP is the dominant lever). So UNO-reported **CPU time ≫ wall time** on threaded solves;
  the GA's `--time-source wall` measures honest elapsed time.
- UNO strategy building blocks / valid option values: `uno_ampl --strategies`; all options:
  `uno_ampl --dump-options`. (Or read the JSON catalogues in `optiuno/`.)

## Next steps

- **Search driver over the black box.** `optiuno.objective.make_objective(problem_set)` gives a
  clean `config -> (reliability, cum_cpu_time)` callable. Remaining work: pick the search method
  (Bayesian optimization / GA / random search, with complete enumeration over the ~240-point
  ingredient space as the ground-truth fallback) and how to handle the bi-objective (scalarize,
  Pareto, or constrained). An optional evaluation cache would make enumeration/duplicate-heavy
  search cheap (the openEvolve harness already caches by config hash under
  `quickRun/harness/cache/`).
- **openEvolve path** (`quickRun/`) remains available; see `quickRun/CLAUDE.md`. Known open issue:
  openEvolve reported "No valid diffs found in response" on smoke iterations (LLM/diff-format
  layer needs a follow-up).
- **Optional refactor:** have `quickRun/harness/benchmark.py:evaluate_config` delegate to
  `optiuno.objective` so there is a single evaluation core (deferred; not required).

## Knowledge base (`.crucible/`)

- Query with `crucible search "..."` / `crucible concept openevolve` (always `cd
  /home/sdinh/sandbox/OptiUNO` first). Covers openevolve, alphaevolve, and UNO strategy topics.

## Git

- The old broken `quickRun/.venv/` (4111 tracked `.pyc`, ~70 MB, no interpreter) was removed
  from git and disk; the tracked `.gitignore` now ignores `.venv/`, `__pycache__/`, `*.pyc` so a
  local env is never re-tracked. That removal is **staged, not committed** — commit it manually
  (project rule: only the user commits).
- Still to decide: git tracking for the large `.nl` corpus (regenerates from `.mod`).
