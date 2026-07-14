# Status

_Last updated: 2026-07-14_

## Current state

The CUTE benchmark is fully prepared (scraped + converted to `.nl` in two variants), and a **Python driver for
UNO** now exists. The remaining milestone is the batch/search harness that sweeps configurations.

- `problems/CUTE/` — **727** COCONUT Library2 CUTE problems, one folder per problem. Each folder has: `.mod`
  (always), `.gms`/`.dag`/`.res` (when available), a `metadata.json`, and **two generated `.nl` files**:
  - **`<name>.nl`** — AMPL presolve **OFF**: the faithful, unsimplified problem. **Primary file for benchmarking.**
  - **`<name>_presolve.nl`** — AMPL presolve **ON**: the reduced problem. (Faithful vs. presolved differ for 65
    problems; identical for 662.)
  - `in_uno_429_subset` flags the 425 problems in UNO's small subset; `feasible`: 510 true / 8 false / 209 unknown.
- `problems/CUTE/summary.csv` — per-problem metadata + feasibility + subset flag + per-file availability, incl.
  `nl_file_available`, `nl_presolve_file_available`, and the two `nl_*_conversion_status` columns.
- `problems/CUTE/nl_conversion_report.csv` — last conversion run's per-problem result.
- `problems/HS_model/` — the **121-problem HS test set** used by the `quickRun/`
  openEvolve experiment (`.nl` files; moved here from `quickRun/models/nl/`). The
  `quickRun` harness reads it via `ROOT.parent / "problems" / "HS_model"`; the current
  set was populated from the `hs*` `.nl` files under `problems/CUTE/`.

## Tooling (`scripts/`)

- `scrape_cute.py` — the corpus scraper (polite + resumable).
- `problem_parser.py` — the `.mod`→`.nl` converter via `amplpy`. `--presolve` flag (default OFF) selects the
  faithful vs. reduced variant. Updates `metadata.json` + `summary.csv`. Flags:
  `--only/--limit/--subset-only/--force/--no-summary/--report`.
- **UNO driver — now `optiuno/uno_runner.py`** (moved out of `scripts/`; the old
  `scripts/uno_runner.py` and `quickRun/harness/uno_runner.py` were merged into this one
  file). Runs `uno_ampl` via subprocess with a **preset and/or custom run-time-options**
  (custom overrides preset) and returns a structured `UnoResult` (outcome, statuses,
  objective, residuals, cpu_time, iterations, evaluation counts, solution_file, plus
  `banner`/`problem`/`wall_time`). Stdlib-only. Adds `time_limit=`/watchdog and `log_path`
  (folded in from the quickRun harness runner) and auto-wires `LD_LIBRARY_PATH` for the
  bundled `external/uno` build.
  - Library: `from optiuno import run_uno; run_uno(nl, preset="ipopt", options={...})`.
  - CLI: `python -m optiuno.uno_runner <nl> --preset ipopt --option k=v ... [--time-limit S] [--write-solution] [--json]`.
  - Outcomes: `solved` / `budget` (iter/time limit) / `error` (evaluation/algorithmic) / `failed` (invalid config,
    can't run) / `timeout`. NOTE: `uno_ampl` exit code is 0 even on failed solves — the driver classifies on the
    printed `Optimization status:`, which is the robust signal.

## Environment / conventions

- `amplpy` 0.17.0 + AMPL `base` engine, licensed with **AMPL for Academics** (full license; allows `write`, no size
  cap). Do NOT switch to AMPL **Community Edition** — it blocks `write`.
- **UNO binary selection** (`optiuno/utils.py:select_uno_bin`, the single UNO-location authority): **system-first**
  — `explicit`/`--uno-bin` → `$UNO_AMPL_BIN` → `uno_ampl` on PATH → the **bundled** build as a fallback. A locally
  built binary lives at `/home/sdinh/sandbox/Uno/build/uno_ampl` — e.g.
  `export UNO_AMPL_BIN=/home/sdinh/sandbox/Uno/build/uno_ampl`. No machine-specific paths are baked into scripts;
  `uno_runner.resolve_uno_bin()` is a thin wrapper over `select_uno_bin`.
- **Bundled UNO v2.8.0** (self-contained binary + `lib/` + `deps/`, ~99 MB): now at the **repo root**,
  `external/uno/bin/uno_ampl` (moved from `quickRun/external/`), shared project-wide. Used automatically as the
  fallback by `select_uno_bin`, and pinned explicitly by `quickRun/harness/benchmark.py` (via
  `optiuno.utils.bundled_uno_bin()`) for reproducible benchmark results. `run_uno` auto-wires `LD_LIBRARY_PATH`
  from the binary's own `lib/`+`deps/` when it detects this release layout.
- UNO strategy building blocks / valid option values: `uno_ampl --strategies`; all options: `uno_ampl --dump-options`.

## Next steps

- **Batch/sweep harness**: layer over `run_uno` to solve a set of problems (e.g. the 429 subset) under a set of
  configs, compare the objective to `Fbest` from `metadata.json` (mind the 8 infeasible / 209 unknown cases),
  aggregate metrics (CPU time, iterations, success rate), and write a results table. `run_uno` already returns
  everything needed and classifies invalid/failing configs gracefully.
- **Search design**: choose the performance metric(s)/objective and the search driver over the strategy-combination
  space from `--strategies`, with complete enumeration as a fallback. Driver options:
  - **openEvolve** — self-hosted (`pip install openevolve`, Py3.10+); needs an OpenAI-compatible LLM endpoint (or
    local model / Claude Code CLI). Three inputs: initial program w/ `# EVOLVE-BLOCK`, `evaluator.py`, `config.yaml`.
  - **AlphaEvolve** — **now GA (2026-07-09)** as a hosted Google Cloud API (Gemini Enterprise Agent Platform); a
    client-side loop supplies a seed program + local evaluator, queries the API for candidates, scores them locally.
    Caveat: GCP org policy on this project blocks some Vertex features (e.g. web_search) — verify API access first.
  - For a ~186-combo categorical space, both may be overkill vs. enumeration or a classical configurator (SMAC/irace);
    the reusable core is a shared `evaluate(config)→metric` over `run_uno` plus a results cache. See the crucible wiki
    (`openevolve`, `alphaevolve`, `openevolve-empirical-findings`) for the full comparison and tuning lessons.

## Knowledge base (`.crucible/`)

- Expanded this session: **22 articles / 21 concepts / 6 sources / 130 cross-links** (was 17/17/2/93). Added
  OpenEvolve coverage from its GitHub README + 3 Hugging Face blogs: concepts `openevolve` and
  `openevolve-empirical-findings`, three source summaries, and a cross-link from `alphaevolve`. Query with
  `crucible search "..."` / `crucible concept openevolve` (always `cd /home/sdinh/sandbox/OptiUNO` first).

## Git

- Generated `.nl` (faithful, untracked) and `<name>_presolve.nl` (staged renames); `problem_parser.py` /
  `uno_runner.py` / `metadata.json` / `summary.csv` edits are working-tree changes. Nothing committed (per rule).
  Decide git tracking for the ~210 MB × 2 `.nl` corpus (track vs. `.gitignore`, since both regenerate from `.mod`).
