# Status

_Last updated: 2026-07-13_

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

## Tooling (`scripts/`)

- `scrape_cute.py` — the corpus scraper (polite + resumable).
- `problem_parser.py` — the `.mod`→`.nl` converter via `amplpy`. `--presolve` flag (default OFF) selects the
  faithful vs. reduced variant. Updates `metadata.json` + `summary.csv`. Flags:
  `--only/--limit/--subset-only/--force/--no-summary/--report`.
- `uno_runner.py` — **the UNO driver.** Runs `uno_ampl` via subprocess with a **preset and/or custom
  run-time-options** (custom overrides preset) and returns a structured `UnoResult` (outcome, statuses, objective,
  residuals, cpu_time, iterations, evaluation counts, solution_file, ...). Stdlib-only.
  - Library: `from uno_runner import run_uno; run_uno(nl, preset="ipopt", options={...})`.
  - CLI: `python scripts/uno_runner.py <nl> --preset ipopt --option k=v ... [--write-solution] [--json]`.
  - Outcomes: `solved` / `budget` (iter/time limit) / `error` (evaluation/algorithmic) / `failed` (invalid config,
    can't run) / `timeout`. NOTE: `uno_ampl` exit code is 0 even on failed solves — the driver classifies on the
    printed `Optimization status:`, which is the robust signal.

## Environment / conventions

- `amplpy` 0.17.0 + AMPL `base` engine, licensed with **AMPL for Academics** (full license; allows `write`, no size
  cap). Do NOT switch to AMPL **Community Edition** — it blocks `write`.
- **UNO binary location**: `uno_runner.py` finds `uno_ampl` via the `UNO_AMPL_BIN` env var (or `--uno-bin`, or
  PATH). The built binary is at `/home/sdinh/sandbox/Uno/build/uno_ampl` — e.g.
  `export UNO_AMPL_BIN=/home/sdinh/sandbox/Uno/build/uno_ampl`. No machine-specific paths are baked into scripts.
- UNO strategy building blocks / valid option values: `uno_ampl --strategies`; all options: `uno_ampl --dump-options`.

## Next steps

- **Batch/sweep harness**: layer over `run_uno` to solve a set of problems (e.g. the 429 subset) under a set of
  configs, compare the objective to `Fbest` from `metadata.json` (mind the 8 infeasible / 209 unknown cases),
  aggregate metrics (CPU time, iterations, success rate), and write a results table. `run_uno` already returns
  everything needed and classifies invalid/failing configs gracefully.
- **Search design**: choose the performance metric(s)/objective and the search driver (openEvolve / AlphaEvolve,
  with complete enumeration as a fallback) over the strategy-combination space from `--strategies`.

## Git

- Generated `.nl` (faithful, untracked) and `<name>_presolve.nl` (staged renames); `problem_parser.py` /
  `uno_runner.py` / `metadata.json` / `summary.csv` edits are working-tree changes. Nothing committed (per rule).
  Decide git tracking for the ~210 MB × 2 `.nl` corpus (track vs. `.gitignore`, since both regenerate from `.mod`).
