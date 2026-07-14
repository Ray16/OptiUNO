# Status

_Last updated: 2026-07-14_

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
- `problems/sets/hs_model_all.json` — **NEW.** Example/default **problem-set JSON** (all 121 HS
  stems, `base_dir: problems/HS_model`) — the input format the black-box evaluator reads.

## `optiuno/` package (the shared, stdlib-only library)

Imported by everything; depends on nothing in `quickRun/` (the dependency arrow is one-way,
`quickRun → optiuno`).

- `optiuno/uno_runner.py` — `run_uno(nl, options=, preset=, uno_bin=, time_limit=) -> UnoResult`.
  One `uno_ampl` subprocess call; regex-parses status/objective/CPU/iterations + the composed
  banner; never raises on a solver failure. Also a CLI (`python -m optiuno.uno_runner`).
- `optiuno/utils.py` — `select_uno_bin` (system-first: explicit → `$UNO_AMPL_BIN` → PATH →
  bundled), `bundled_uno_bin` (pins `external/uno/bin/uno_ampl`), and `REPO_ROOT`.
- **`optiuno/objective.py`** — **NEW.** The black-box objective for external optimizers:
  - `evaluate(config, problem_set, *, time_limit=20, workers=8, uno_bin=None, validate=True)`
    → `(reliability, cum_cpu_time)`. **reliability** = fraction in [0,1] solved (strict:
    `Optimization status: Success` **and** `Solution status: Feasible KKT point`).
    **cum_cpu_time** = sum of UNO-reported CPU seconds; a timeout charges the full `time_limit`.
    Solves in a ThreadPool (parallelism does not affect the CPU-sum metric). Binary defaults to
    the bundled build for reproducibility.
  - `evaluate_detailed()` (rich dict incl. `status_counts` + per-problem rows),
    `load_problem_set()` (JSON path / list / `{base_dir, problems}` object; fail-fast on missing
    files), `is_solved()`, and `make_objective(problem_set) -> (config -> (rel, cpu))` for
    optimizer loops.
  - Config is validated against `uno_search_space.json` (unknown key / illegal value → ValueError);
    bad *combinations* of legal values are NOT rejected — they run and show as low reliability.
  - CLI: `python -m optiuno.objective --problems SET.json --option k=v ... [--json]`.
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
- The UNO driver lives in `optiuno/uno_runner.py` (see above), not in `scripts/`.

## Environment / conventions

- `amplpy` 0.17.0 + AMPL `base` engine, licensed with **AMPL for Academics** (allows `write`, no
  size cap). Do NOT switch to AMPL **Community Edition** — it blocks `write`.
- **UNO binary selection** (`optiuno/utils.py:select_uno_bin`): **system-first** — `explicit`/
  `--uno-bin` → `$UNO_AMPL_BIN` → `uno_ampl` on PATH → the **bundled** build as a fallback. A
  locally built binary can be selected with `export UNO_AMPL_BIN=/path/to/uno_ampl`.
- **Bundled UNO v2.8.0** at the repo root, `external/uno/bin/uno_ampl` (self-contained binary +
  `lib/` + `deps/`, ~99 MB). Used automatically as the fallback and pinned by
  `quickRun/harness/benchmark.py` and `optiuno.objective.evaluate` for reproducibility.
  `run_uno` auto-wires `LD_LIBRARY_PATH` from the binary's own `lib/`+`deps/`.
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

- Nothing committed (per rule). Working-tree additions this session: `optiuno/objective.py`,
  `optiuno/uno_config_options.json`, `optiuno/uno_search_space.json`,
  `problems/sets/hs_model_all.json`, edits to `optiuno/__init__.py`, `CLAUDE.md`, `LOGBOOK.md`,
  `STATUS.md`. Still to decide: git tracking for the ~210 MB × 2 `.nl` corpus (regenerates from
  `.mod`).
