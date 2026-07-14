# Status

_Last updated: 2026-07-13_

## Current state

The CUTE benchmark is fully prepared: all 727 problems are scraped **and** converted to UNO-ready `.nl` files.
No solver/experiment harness yet — that's the next milestone.

- `problems/CUTE/` — **727** COCONUT Library2 CUTE problems, one folder per problem, each with its available
  `.mod`/`.gms`/`.dag`, the `.res` reference solution (when one exists), a generated **`<name>.nl`**, and a
  `metadata.json`.
  - File availability: `.mod` 727/727, **`.nl` 727/727**, `.gms` 531, `.dag` 545, `.res` 531.
  - `in_uno_429_subset` flags the **425** problems (of UNO's 429 small-problem list) present in Library2
    (4 subset names absent from the page: `hs067`, `methanb8`, `methanl8`, `nuffield_continuum`).
  - `feasible`: 510 true, 8 false (infeasible best-known), 209 unknown (no Fbest in the table).
- `problems/CUTE/summary.csv` — one row per problem; web-table metadata + feasibility + subset flag + per-file
  availability (incl. `nl_file_available`, `nl_conversion_status`) + detail-page URL.
- `problems/CUTE/nl_conversion_report.csv` — per-problem conversion result (723 converted, 4 skipped, 0 failed).
- Generated `.nl` corpus is **~210 MB** (largest `sensors.nl` 44 MB). These are regenerable from `.mod`; **not yet
  git-tracked — user decision pending** (track vs. add `*.nl` to `.gitignore`).

## Tooling

- `scripts/scrape_cute.py` — the scraper (polite + resumable; `--only/--limit/--force/--summary-only`).
- `scripts/problem_parser.py` — the **`.mod`→`.nl` converter** via `amplpy`. Strips AMPL `solve`/`display`/`printf`,
  keeps model + `data;`/`let` (starting points), writes `<name>.nl` per folder, updates `metadata.json` +
  `summary.csv`. Flags: `--only/--limit/--subset-only/--force/--no-summary/--report`. Resumable (skips existing
  non-empty `.nl`). Run with the `sequential_OED` env python.
- **Environment** (`sequential_OED`, Python 3.12): `amplpy` 0.17.0 + AMPL `base` engine module installed.
  Licensed with a free **AMPL for Academics** license (activated via `amplpy.modules activate <uuid>`), which
  allows the `write` command with no size cap. NOTE: the AMPL **Community Edition** license does *not* allow
  `write` — do not switch to it; the demo license allows `write` but caps size at ~300 vars.
- UNO built at `/home/sdinh/sandbox/Uno/build/uno_ampl`; verified reading generated `.nl`, e.g.
  `uno_ampl problems/CUTE/hs071/hs071.nl preset=ipopt` → obj 17.014 (matches Fbest).

## Next steps

- **Decide git tracking for `.nl`** (~210 MB): commit them for convenience, or `.gitignore` them since
  `problem_parser.py` regenerates them from the `.mod` files.
- **Experiment harness**: run `uno_ampl` on a problem with a given `run-time-options`/preset config, capture
  objective/status/iterations/CPU-time, compare against the reference solution/Fbest, and detect invalid/failing
  configurations gracefully. The corpus (`.nl` + `metadata.json` with Fbest/feasibility) is ready to drive this.
- **Search design**: decide the performance metric(s)/objective and the search driver (openEvolve / AlphaEvolve,
  with complete enumeration as a fallback).
