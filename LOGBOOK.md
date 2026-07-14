# Logbook

Append-only history of changes and actions. Newest entries at the bottom. Never overwrite existing entries.

## 2026-07-13

- Ran `/init`; created `CLAUDE.md` documenting project intent (tuning UNO strategy configurations via evolutionary search), external dependencies, and key references.
- Created initial `LOGBOOK.md` and `STATUS.md`.
- Finalized the `CLAUDE.md` **Rules** section with the following (user-provided):
  1. Never commit — user runs `git commit`/`git push` manually.
  2. Never modify UNO source code unless explicitly authorized; treat UNO as a read-only dependency accessed via `run-time-options`.
  3. Never modify the user's environment; only check for installed packages and suggest fixes.
  4. Stay within the `OptiUNO/` directory and subfolders; do not explore parent/sibling folders.
  5. Session logging: read `LOGBOOK.md` + `STATUS.md` at start; update both at end (LOGBOOK append-only, STATUS overwritten).

### Session 2 — CUTE benchmark scrape

- Built `scripts/scrape_cute.py`: a polite, resumable scraper for the COCONUT Library2 CUTE collection (`https://arnold-neumaier.at/glopt/coconut/Benchmark/Library2_new_v1.html`). Uses already-installed `requests`/`bs4`/`lxml`/`pandas` (no installs). Flags: `--only`, `--limit`, `--force`, `--delay`, `--summary-only`.
- Scraped **all 727** problems into `problems/CUTE/<name>/`. Per problem: downloaded every available file (`.mod`, `.gms`, `.dag`) + reference solution `RES/<name>.res`, and wrote `metadata.json` with the table metadata (number, classification, N, M, Nnl, Mnl, Nz, Fbest), per-file `*_file_available` flags, `feasible` (from the parenthesized-Fbest convention), and an `in_uno_429_subset` tag.
- Tagged UNO's benchmark subset from `nonconvex_solver_comparison/CUTE/small_instances.txt`: **425 of 429** matched; 4 subset names are absent from Library2 (`hs067`, `methanb8`, `methanl8`, `nuffield_continuum`).
- Wrote `problems/CUTE/summary.csv` (727 rows) mirroring the web table plus all metadata keys.
- Findings: `.mod` present for all 727 (the format UNO needs); `.gms` 531, `.dag` 545, `.res` 531. Missing `.gms`/`.dag`/`.res` return HTTP 300 (Apache "Multiple Choices") = genuinely absent, recorded as `false`. Feasibility: 510 true, 8 false (infeasible best-known), 209 unknown (empty Fbest). Corpus ≈128 MB / 3077 files. Verified an infeasible example (`argauss`, `hs085`), spot-checked table rows against the site, and confirmed idempotent re-run (all 727 skipped).
- Fixed two bugs during testing: table hrefs are relative to the index page (not `Library2/`) — was producing doubled URLs; and the subset-missing check now compares against the full table.

### Session 3 — `.mod` → `.nl` converter

- Built `scripts/problem_parser.py`: converts each `problems/CUTE/<name>/<name>.mod` into `<name>.nl` (AMPL
  ASCII "g"-format) in the same folder, for the UNO solver (`uno_ampl` reads `.nl`, not `.mod`). Mirrors
  `scrape_cute.py` conventions (docstring, `pathlib`, section banners, `main(argv)`, `--only/--limit/--force`,
  atomic tmp→rename, `metadata.json` read/merge/write with `indent=2`, `raise SystemExit(main())`).
- Conversion approach: `preprocess_mod()` strips AMPL *command* statements (`solve`, `display`, `print`,
  `printf`, `expand`, `close`, `shell`, `exit`, `quit`, `reset`, `write`, `csvdisplay`) after removing comments,
  keeping all model/data statements (`param`, `var`, `minimize`, `subject to`, `data;` blocks, `let` starting
  points). The cleaned model is written to a temp `.mod`, `AMPL().read()`-run (so nothing solves), then
  `write "g<stub>"` emits the `.nl`; tmp files are renamed/cleaned atomically. A single `AMPL()` instance is
  reused with `reset()` per problem and recreated only if the engine dies.
- Outputs: updates each `metadata.json` (`nl_file_available`, `files["nl"]`, `nl_conversion` status/reason) and
  refreshes `problems/CUTE/summary.csv` with `nl_file_available` + `nl_conversion_status` columns (inserted after
  `res_file_available`). `--report` writes `nl_conversion_report.csv`; `--subset-only` restricts to the UNO 429.
- Dependency: **amplpy** (AMPL Python API + processor) — the only thing that parses AMPL `.mod`. Not installed;
  the script lazy-imports it and, if absent, prints exact install commands for the `sequential_OED` env and exits
  cleanly (code 2). Demo AMPL caps model size (~300 nonlinear vars); free AMPL CE license
  (`amplpy.modules activate <uuid>` from https://ampl.com/ce) lifts it. Oversized problems fail gracefully and are
  reported (grouped as "size-limit" vs "other"; exit code non-zero only for non-size-limit failures).
- Verified without amplpy: byte-compiles, `--help` OK, import guard prints instructions + exits 2, and
  `preprocess_mod` on `hs071.mod` (keeps `let` starting point) and `rosenbr.mod` (keeps `data;` block) strips all
  solve/display/printf while preserving model+data. Full end-to-end verification (`.nl` generation +
  `uno_ampl hs071.nl preset=ipopt` → obj ≈ 17.014) is pending the amplpy install.

### Session 3 (cont.) — amplpy install, AMPL licensing, full conversion

- User installed `amplpy` 0.17.0 (Python API) via pip, then the `base` AMPL engine module
  (`python -m amplpy.modules install base`). Note: `pip install amplpy` gives only the API; the `ampl` processor
  is a separate `amplpy.modules` install (fixed the `cannot execute /x-ampl` error). Updated the script's
  INSTALL_HINT to say `install base`.
- **AMPL licensing gotcha (important):** the bundled **demo** license allows the `write` command (how we emit
  `.nl`) but caps model size (~300 nonlinear vars) — hs071 & rosenbr converted + solved in UNO under it.
  **Community Edition (CE)** removes the size cap **but blocks `write` entirely** ("AMPL CE does not allow write
  commands except during trials") — even hs071 failed after CE activation. The fix is a **full license**: user
  obtained a free **AMPL for Academics (A4A)** license (portal.ampl.com/account/ampl, academic email, no time
  limit, full functionality) and activated it via `amplpy.modules activate <uuid>` (overwrites the CE `ampl.lic`).
- With A4A active, verified `write` unblocked and cap gone: hs071 (724 B), minc44 (N=311 → 33 KB),
  mccormck (N=50000 → 3.0 MB) all converted.
- **Ran the full batch** (`problem_parser.py --report`): **727/727 converted, 0 failed** (723 new + 4 already
  present). Each problem folder now has `<name>.nl`; `summary.csv` shows `nl_file_available=True` for all 727;
  `nl_conversion_report.csv` written; no stray temp files.
- End-to-end spot-checks in UNO (`preset=ipopt`) matched Fbest: hs071→17.014, rosenbr→~0, avion2→9.468013e7,
  bqp1var→~0, denschna→~0 (all "Success").
- Generated `.nl` corpus is **209.5 MB** across 727 files (largest: `sensors.nl` 44.4 MB, `scurly30.nl` 7.8 MB).
  These are regenerable artifacts (from `.mod` via the script); left untracked pending the user's git decision
  (track vs. `.gitignore`). [Superseded below: these were the presolve-ON files, since renamed to `_presolve.nl`.]

### Session 3 (cont.) — AMPL presolve discovery + dual-variant `.nl`

- Genericized `scripts/problem_parser.py`: removed all machine-specific paths/env names
  (`/home/sdinh/anaconda3/envs/sequential_OED/bin/python`, `sequential_OED`) from the docstring and INSTALL_HINT;
  commands now use plain `python -m ...`. Also corrected the INSTALL_HINT license guidance (CE blocks `write`; use
  a full/academic license). `git add`ed the 727 `.nl` (staging only; no commit).
- **Found that AMPL presolve was silently active.** `write` runs AMPL's presolver by default
  (`option presolve 10`), which rewrites the model (fixes/eliminates vars, drops constraints). Proven on
  `aircrftb`: presolve-on → 5 vars/0 cons vs presolve-off → 8 vars/3 cons. Across the corpus, **65 of 727** models
  actually differ between the two. For a faithful UNO benchmark we want the unsimplified model.
- Renamed the existing (presolve-on) files `<name>.nl` → `<name>_presolve.nl` for all 727 via `git mv` (staged).
- Added a **`--presolve` flag** (default OFF) to `problem_parser.py`. A `variant_spec()` maps the flag to the
  AMPL `option presolve` value (0 off / 10 on), the output filename (`<name>.nl` / `<name>_presolve.nl`), and the
  metadata/summary keys. `convert_one` now emits `option presolve N;` before `write`. `update_metadata` derives
  **both** availability flags + `files[]` entries from disk (self-healing) and records per-variant conversion
  status (`nl_conversion` / `nl_presolve_conversion`). `summary.csv` gained four nl columns
  (`nl_file_available`, `nl_presolve_file_available`, `nl_conversion_status`, `nl_presolve_conversion_status`)
  after `res_file_available`; the report gained a `presolve` column.
- **Regenerated the faithful presolve-OFF `<name>.nl` for all 727** (`--force --report`): 727 converted, 0 failed.
  Now every folder has both `<name>.nl` (faithful) and `<name>_presolve.nl` (reduced). summary.csv shows
  nl_file_available=727 and nl_presolve_file_available=727; no stray temp files; re-run without `--force` skips.
- End-to-end in UNO on faithful files: hs071→17.014, aircrftb (8-var full)→Success, allinit (4/3 full)→16.706.

### Session 3 (cont.) — UNO Python driver module

- Built `scripts/uno_runner.py`: a stdlib-only Python driver that runs `uno_ampl` via `subprocess` and returns a
  structured `UnoResult`. Supports a **preset and/or custom run-time-options** together (custom options are placed
  after `preset=` so they override it, matching UNO's parse order). Mirrors the existing scripts' conventions.
- API: `run_uno(nl_path, *, preset=None, options=None, uno_bin=None, timeout=None, write_solution=False,
  capture_stdout=False, extra_args=None) -> UnoResult`. `UnoResult` carries optimization/solution status,
  objective, residuals, cpu_time, iterations, all evaluation counts, returncode, solution_file, the options used,
  and `.ok`/`.to_dict()`. Plus a CLI: `uno_runner.py <nl> --preset P --option k=v ... [--options k=v,..]
  [--uno-bin] [--timeout] [--write-solution] [--print-stdout] [--json]`.
- Binary resolution avoids machine-specific paths: `uno_bin` arg → `$UNO_AMPL_BIN` → `shutil.which("uno_ampl")`
  → clear FileNotFoundError.
- Classifier derived from UNO source (via Explore): `uno_ampl` returns exit code 0 even on failed solves and 1
  only on setup/parse errors (printing `uno_ampl failed with the following error:` to stdout), so outcome is keyed
  on the printed `Optimization status:`. Five outcomes: **solved** (Success), **budget** (Iteration/Time limit,
  User termination), **error** (Evaluation/Algorithmic error, Unknown), **failed** (exit≠0 or no summary), and
  **timeout**. Parser tolerates the box-drawing prefixes on the residual lines and the duplicated
  `Primal feasibility:` line.
- Verified all 9 cases: compile/help; preset solve (hs071→solved, 17.014); preset+custom override; custom-only
  building blocks (→budget without preset tuning); invalid value (→error, rc 0); nonexistent model (→failed);
  malformed .nl (→failed, rc 1, captured `jacdim` error); `--write-solution` (.sol written, path recorded);
  timeout on 50k-var mccormck (→timeout); and programmatic `from uno_runner import run_uno`.
