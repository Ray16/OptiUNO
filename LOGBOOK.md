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

## 2026-07-14

### Session 4 — Crucible: ingest OpenEvolve sources + AlphaEvolve GA note

- Answered conceptual questions on AlphaEvolve vs. Bayesian optimization vs. genetic algorithms,
  and on the AlphaEvolve/OpenEvolve setup requirements, grounded in the existing crucible wiki.
  Correction learned this session: **AlphaEvolve went generally available on 2026-07-09** as a
  hosted API on Google Cloud's Gemini Enterprise Agent Platform (client-side loop: query API for
  mutated candidates → score with your local evaluator → submit scores back). Supersedes the prior
  "not publicly available" understanding (was true as of the Jan 2026 knowledge cutoff).
- **Ingested 4 OpenEvolve web sources** into crucible (`crucible ingest`, stored under
  `.crucible/sources/external/web/`): the GitHub README (`sharma2026`), and three Hugging Face
  blog posts — the intro/announcement (`sharma2025`), GPU-kernel discovery (`sharma2025`), and the
  AlgoTune study "Towards Open Evolutionary Agents" (`andthattoo2025`). Fetched via `curl`
  (web_search is blocked by GCP org policy on this project; `pandoc` not installed, so blog HTML was
  converted to text with the already-present `bs4`). No packages installed.
- **Cite-key limitation found:** crucible *derives* cite keys as firstauthor+year and does not store
  or disambiguate them, so both Sharma-2025 blogs collide on `citep:sharma2025` (one bib entry). The
  `--bibtex` flag does not override the derived key. Article→source linking is unaffected because it
  uses `SOURCE_KEYS` filename tokens (`oe_readme`/`oe_blog_intro`/`oe_blog_gpu`/`oe_blog_agents`),
  which were verified per-article with `crucible sources`. Cosmetic bibliography collision only.
- **Distilled 5 new wiki articles + 1 update:** concepts `openevolve.org` (anchor: architecture,
  config, LLM options, setup, OptiUNO mapping) and `openevolve-empirical-findings.org` (parallelism
  essential, diff-vs-rewrite by model strength, temp ≈0.4, artifacts +17%, more iterations help,
  ensembles underperform, cascade eval saves ~70%); summaries `sharma-2025-openevolve.org`,
  `sharma-2025-openevolve-gpu-kernels.org`, `andthattoo-2025-open-evolutionary-agents.org`; and a
  cross-link section added to existing `alphaevolve.org`.
- **Maintenance:** `crucible sync` + `manifest` + `index` + `lint`. Wiki grew 17→22 articles,
  17→21 concepts, 2→6 sources, 93→130 links; new topics `openevolve`, `benchmarking`, `algotune`,
  `gpu-optimization`. Lint clean of citation/link errors (remaining items are the auto-generated
  `index.org` frontmatter warnings and two optional "no dedicated article" info hints); no orphans.
  Fixed a mid-editing snag where a delete/re-ingest cycle left the GPU blog as an orphan file with no
  DB row (re-ingested cleanly). Per rules: nothing committed.

---

## 2026-07-14 — Merged the two `uno_runner.py` into `optiuno/uno_runner.py`

The repo had two divergent UNO drivers: `scripts/uno_runner.py` (typed `UnoResult`, binary
resolution, full field/residual parsing, CLI — but never imported by any code) and
`quickRun/harness/uno_runner.py` (plain-dict return, hard-wired bundled binary +
`LD_LIBRARY_PATH`, banner parsing, `DEFAULT_TIME_LIMIT`/watchdog, `log_path` — imported only
by `quickRun/harness/benchmark.py`). Merged them into a single **`optiuno/uno_runner.py`**
(built on the richer `scripts/` version) and deleted both originals.

- Folded the quickRun-only features into the `UnoResult` design: added `banner` (composed-method
  string), `problem`, `wall_time`; added `DEFAULT_TIME_LIMIT = 20.0`, a `time_limit=` option
  (also drives the default `time_limit+10` watchdog), a `log_path` writer, and automatic
  `LD_LIBRARY_PATH` wiring when the resolved binary is a self-contained release (detected by a
  `deps/` sibling of `lib/`, so it never mis-fires for system installs — no path baked into
  `optiuno`). Signature made backward-compatible with both old call styles:
  `run_uno(nl_path, options=None, *, preset=None, uno_bin=None, time_limit=None, timeout=None, ...)`.
- Callers: `quickRun/harness/benchmark.py` now imports `from optiuno.uno_runner import ...`
  (adds the repo root to `sys.path`), passes `uno_bin=external/uno/bin/uno_ampl`, and reads the
  `UnoResult` by attribute (kept the emitted per-problem key `objective_evaluations` so the
  cache/CSV schema and existing `harness/cache/*.json` stay valid). `quickRun/harness/classify.py`
  switched from dict `.get()` to `UnoResult` attributes. The four scripts that import
  `harness.benchmark` (evaluator, run_evolution, validate_presets, variance_runs) needed no
  changes. `optiuno/__init__.py` re-exports `run_uno`/`UnoResult`/`DEFAULT_TIME_LIMIT` lazily
  (PEP 562) so `python -m optiuno.uno_runner` runs without a runpy double-import warning.
- CLI moved from `python scripts/uno_runner.py ...` to `python -m optiuno.uno_runner ...`
  (also runnable as `python optiuno/uno_runner.py ...`).
- Verified: py_compile of all changed files; `from optiuno import run_uno, UnoResult,
  DEFAULT_TIME_LIMIT`; the `harness.benchmark`/`harness.classify` import chain resolves
  `optiuno`; a live solve of `hs110`/`rosenbr` against the bundled binary returns
  `outcome=solved` with `banner`/`wall_time`/`problem` populated and `classify()` →
  `solved / Feasible KKT point`; and the CLI (`-m`, script-path, `--json`, `--time-limit`)
  works with correct exit codes. (The full `benchmark`/`validate_presets` sweep still needs the
  uncommitted HS `.nl` set under `quickRun/models/`.)

---

## 2026-07-14 — Moved bundled UNO to the repo root + system-first UNO selector

Promoted the self-contained UNO v2.8.0 build from a `quickRun/`-only resource to a
project-wide one, and centralized "which uno_ampl do we run?" in a single helper.

- **Moved `quickRun/external/` → `external/`** at the repo root via `git mv` (579 files,
  ~99 MB; staged as renames so history is preserved — **not committed**, per rule). New
  bundled binary path: `external/uno/bin/uno_ampl` (with sibling `lib/` + `deps/`). No
  `.gitignore` rule shadows the new location; `quickRun/external` is fully gone from the
  index.
- **New module `optiuno/utils.py`** — the single UNO-location authority (stdlib-only):
  - `select_uno_bin(explicit=None)` — **system-first** selection: `explicit` → `$UNO_AMPL_BIN`
    → `uno_ampl` on `PATH` → bundled `external/uno/bin/uno_ampl` fallback. Returns an
    absolute path; raises `FileNotFoundError` (with guidance) only if even the bundled build
    is missing. Usability check matches the old resolver (`is_file()` + `os.access(X_OK)`).
  - `bundled_uno_bin()` / `BUNDLED_UNO_BIN` — the one place the bundled path is written
    (computed from the package location: `Path(__file__).resolve().parents[1]/external/uno/...`).
- **`optiuno/uno_runner.py`** now routes through the helper: `resolve_uno_bin()` is a thin
  wrapper over `select_uno_bin()` (keeps the public name/signature; `run_uno` and the
  `--uno-bin` CLI gain the bundled fallback for free). Dropped the now-unused `shutil` import
  and `DEFAULT_BIN_NAME` constant; `_bundled_env()` (LD_LIBRARY_PATH wiring) is unchanged —
  it derives paths from the binary's own layout, so it works at the new location. Docstrings
  and CLI help updated to state the new precedence.
- **`quickRun/harness/benchmark.py`** keeps its **bundled pin** for reproducibility (user's
  choice), but now sources it from the helper: `UNO_BIN = bundled_uno_bin()` instead of the
  hard-coded `ROOT/"external"/...`. The `run_uno(..., uno_bin=UNO_BIN)` call is unchanged, so
  cache keying is preserved.
- **`optiuno/__init__.py`** lazily re-exports `select_uno_bin`/`bundled_uno_bin` (routed to the
  right submodule via a name→module map) alongside the existing `run_uno`/`UnoResult`/
  `DEFAULT_TIME_LIMIT`; still no eager import (no runpy warning under `python -m`).
  `quickRun/CLAUDE.md` updated to note the repo-root bundle + `select_uno_bin`/`bundled_uno_bin`.
- **Verified:** py_compile of all four Python files; bundled fallback (env unset, empty PATH →
  `select_uno_bin()` returns the root bundle); system-first precedence (a fake `$UNO_AMPL_BIN`
  binary wins over bundled); a live solve of `problems/HS_model/hs071.nl --preset ipopt`
  against the bundled binary → `outcome=solved`, obj 17.01402, `cmd[0]` = root bundle (proves
  LD_LIBRARY_PATH wiring at the new location); `harness.benchmark.UNO_BIN` resolves to the root
  bundle; `grep` finds no stale `quickRun/external` refs; all lazy re-exports import and
  `python -m optiuno.uno_runner --help` runs with no RuntimeWarning. Nothing committed.

---

## 2026-07-14 — Provisioned the HS test set and moved it to `problems/HS_model/`

Context: the `quickRun/` openEvolve run failed because (a) `run_evolution.py` hard-coded
`.venv/bin/openevolve-run` but openEvolve is installed in the `sequential_OED` conda env, and
(b) `quickRun/models/nl/` was empty (the Vanderbei `.mod` sources were never committed, so
`translate_models.py` couldn't regenerate them).

- **`run_evolution.py`:** made the Claude Code CLI (subscription) the **default** backend and
  added `--api` to opt into the Anthropic API (kept `--claude-code` as a deprecated no-op).
  Replaced the hard-coded `.venv/bin/openevolve-run` with `_find_openevolve_run()`, which
  prefers the `openevolve-run` next to the running interpreter (so
  `conda run -n sequential_OED python scripts/run_evolution.py` works), then a project `.venv`,
  then PATH.
- **Test set:** populated the set by copying the 121 faithful `hs*` `.nl` files from
  `problems/CUTE/` (a COCONUT/Neumaier translation — a different provenance than the original
  Vanderbei set, so not directly comparable to the archived `results/quickRun/` numbers). Moved
  the 75 stale Vanderbei-based cache files to `quickRun/harness/cache/_vanderbei_backup/`
  (preserved, not deleted).
- **Verified the pipeline end-to-end:** baselines evaluate on the 121-problem set
  (filtersqp 0.967 / 4.14 s, ipopt 0.917 / 11.11 s) and `run_evolution.py --smoke` runs to
  completion via the Claude Code backend (exit 0). Known issue: openEvolve reported
  "No valid diffs found in response" on every smoke iteration, so no mutation occurred — the
  plumbing works but the diff-format/LLM layer needs a follow-up.

### Relocated the test set: `quickRun/models/nl/` → `problems/HS_model/`

Moved the 121-problem HS `.nl` set up to the repo root (alongside `problems/CUTE/`) and removed
the now-empty `quickRun/models/`. Because quickRun scripts set `ROOT = quickRun/` but the target
is one level up, the two live path assignments were repointed to
`ROOT.parent / "problems" / "HS_model"` (not a string swap, which would give
`quickRun/problems/...`):

- `quickRun/harness/benchmark.py` — `NL_DIR` (the sole consumer; `test_problems()` and the
  no-`.nl` RuntimeError follow via the variable). The four scripts that import
  `harness.benchmark` (evaluator, run_evolution, validate_presets, variance_runs) inherit the
  new path — no edits.
- `quickRun/scripts/translate_models.py` — `NL_DIR` and `REPORT` (`untranslatable.md`, now
  inside the test-set dir); `MANIFEST.csv` already writes inside `NL_DIR` so it travels
  automatically. Left `MOD_DIR` (`quickRun/models/mod`, the `.mod` source) unchanged — input
  and output are no longer siblings; noted in the docstring.
- Docs updated: `quickRun/CLAUDE.md` (path-convention + commands), `STATUS.md` (new
  `problems/HS_model/` entry). Config-hash cache is unaffected (keyed by options, not paths).
- Verified: `NL_DIR` resolves to `problems/HS_model` and finds 121 problems; a full preset sweep
  reproduces filtersqp 117/121 (0.967); both edited files byte-compile.

## 2026-07-14 — UNO option catalogues + decoupled black-box evaluator (`optiuno.objective`)

Added two machine-readable option catalogues and a reusable, search-driver-agnostic objective
function so optimizers other than openEvolve (Bayesian optimization, GA, enumeration) can score
UNO configs.

### Option catalogues (`optiuno/*.json`)
- `optiuno/uno_config_options.json` — full catalogue of **all 89 options** (6 preset-only
  ingredients + 85 from `--dump-options`), built by probing the bundled `external/uno` binary
  (`--strategies` + `--dump-options`), cross-checked vs `results/quickRun/uno-options.md`.
  Groups: ingredients, search_space (incl. `known_invalid_combinations` / `silent_rewrites`),
  solvers (this build: QP/LP BQPD+HiGHS, linear MUMPS+SSIDS — no HSL), presets,
  categorical/boolean/numeric options. Coverage + defaults verified against the binary.
- `optiuno/uno_search_space.json` — just the six searchable ingredients → legal values (flat
  dict; byte-identical to `quickRun/evolve/evaluator.py:ALLOWED`).
- **Finding:** `uno_ampl --strategies` prints the Hessian model as `LFBGS`, but that is a
  display typo — the parser accepts `LBFGS` (banner "with L-BFGS Hessian") and rejects `LFBGS`
  ("Hessian model LFBGS does not exist"). Catalogues use the accepted spelling `LBFGS`; the
  repo's existing `ALLOWED`/`initial_program.py` were already correct.

### Black-box evaluator (`optiuno/objective.py`)
- `evaluate(config, problem_set) -> (reliability, cum_cpu_time)` — solves one UNO config over a
  problem set and returns the two OptiUNO objectives. **reliability** = fraction in [0,1] that
  reached optimum (strict `Success` + `Feasible KKT point`, matching
  `quickRun/harness/classify.py` but reimplemented so `optiuno` keeps its one-way dependency —
  it does **not** import `quickRun`). **cum_cpu_time** = sum of per-problem UNO CPU seconds;
  a timeout charges the full `time_limit` (mirrors `benchmark.py:70-74`). Runs problems in a
  ThreadPool (default 8 workers); parallelism does not affect the CPU-sum metric.
- Also: `evaluate_detailed()` (rich dict), `load_problem_set()` (JSON path / list / object with
  `base_dir`+`problems`, fail-fast on missing files), `is_solved()`, `make_objective()` factory
  (resolves the set once, returns `config -> (rel, cpu)` for an optimizer loop), and a CLI
  (`python -m optiuno.objective --problems SET.json --option k=v ...`).
- Config is validated against `uno_search_space.json` (unknown key / illegal value → ValueError);
  bad *combinations* of legal values (interior_point+TR, the primal_dual×inequality_constrained
  dead region) are NOT rejected — they run and surface as low reliability, which the optimizer
  should see.
- **Naming gotcha:** first drafted as `optiuno/evaluate.py`, but a submodule whose name equals a
  re-exported function name breaks the lazy `__init__` re-export (`from optiuno import evaluate`
  returned the module). Renamed the module to `optiuno/objective.py`; the function stays
  `evaluate`. Added `evaluate`/`evaluate_detailed`/`load_problem_set`/`make_objective` to
  `optiuno/__init__.py` `_LAZY`.
- New data file `problems/sets/hs_model_all.json` (all 121 HS stems) as the example/default set.

### Verification
- CLI over the 121-set with filtersqp ingredients → **reliability 0.9669 (117/121)**, exact
  match to the recorded baseline; `cum_cpu_time` ≈ 2–3.5 s (run-to-run CPU noise).
- Cross-checked vs `quickRun.harness.benchmark.evaluate_config` on the same set (fresh, no
  cache): **reliability identical**, `cum_cpu_time` within noise (3.25 vs 3.45 s).
- Fail-fast paths (missing file, unknown key, illegal value, stem without base_dir) all raise;
  dead-region config runs to `(0.0, …)` without raising; `make_objective` returns a callable.
- `CLAUDE.md` (root) was also refreshed this session to document the current architecture
  (shared `optiuno` library, the two corpora, the search-pipeline input layering).

## 2026-07-14 — CUTE problem-set JSONs + GA output-path scheme

### Added CUTE problem-set JSONs
Created two more problem-set JSONs under `problems/sets/`, in the same format read by
`optiuno.objective.load_problem_set`, generated from `problems/CUTE/summary.csv`:

- `cute_uno_subset.json` — the **"400s" UNO test set**: UNO's nonconvex-solver-comparison
  benchmark subset (`in_uno_429_subset`), **425** of the original 429 `small_instances`
  (4 absent from Library2: `hs067`, `methanb8`, `methanl8`, `nuffield_continuum`).
- `cute_all.json` — **all 727** CUTE problems.

Both list **full nested `.nl` paths** (`problems/CUTE/<name>/<name>.nl`) with **no `base_dir`**,
because CUTE is one-folder-per-problem — the flat `base_dir`+stem convention `hs_model_all.json`
uses (`base_dir/<stem>.nl`) does not fit. `_resolve_entry` treats any entry ending in `.nl` as a
path (resolved against the repo root), so this loads unchanged. Faithful presolve-OFF `.nl`
variant only. Entries sorted alphabetically.

- Verified: the generator confirmed every referenced `.nl` exists on disk (0 missing for both
  sets); `load_problem_set` resolves all three sets — cute_all → 727, cute_uno_subset → 425,
  hs_model_all → 121 — with every path present.

### GA output-path scheme
- Changed `scripts/ga_search.py` default output folder from
  `results/ga_<set>/<timestamp>/` to
  `results/ga_pop_<pop_size>_gen_<generations>_<set>/<timestamp>/`, so the population and
  generation count are visible in the group folder name; the run timestamp stays as the
  subfolder (existing convention). Only the default path changed — an explicit `--out` still
  overrides. Updated the module docstring and `--out` help text to match.
- Verified: `py_compile` OK; path construction previews e.g.
  `results/ga_pop_24_gen_15_hs_model_all/<timestamp>/` and
  `results/ga_pop_40_gen_30_cute_uno_subset/<timestamp>/`. The prior
  `results/ga_hs_model_all/20260714_163339/` run folder is left untouched.

Nothing committed (per rule).

## 2026-07-14 — GA timing: tic-toc UNO time, serial default, GA-overhead metric

Reworked how `scripts/ga_search.py` accounts time so it can report **GA overhead =
real run wall clock − time spent inside UNO**, with UNO time measured by tic-toc.

**Clarified first (user question):** the time the GA minimizes was UNO's *self-reported
CPU seconds* (parsed from the `CPU time:` line UNO prints — `optiuno/uno_runner.py`),
NOT a tic-toc around the call. `run_uno` also records `UnoResult.wall_time` (a
`time.perf_counter()` measured around the `subprocess.run`), previously used only as a
crash fallback.

**`optiuno/objective.py` (shared library, backward-compatible):**
- Renamed `_charged_cpu` → `_charged_time(res, time_limit, time_source)`. New
  `time_source="wall"` charges the real tic-toc `res.wall_time` (no cap; it is the
  time genuinely spent); `time_source="cpu"` (default) keeps the old UNO-CPU logic.
- `evaluate_detailed` / `evaluate` / `make_objective` gained a `time_source="cpu"`
  kwarg (default preserves all existing behavior/numbers). Per-problem rows now always
  carry raw `wall_time`; the result dict gained `cum_wall_time` (always the tic-toc
  sum) and `time_source`. Invalid `time_source` → ValueError.
- CLI: added `--time-source {cpu,wall}`; prints `cum_time` (labelled with its source)
  and `cum_wall_time`.

**`scripts/ga_search.py`:**
- **Default `--workers` 8 → 1** (serial, no parallel pool) so the summed UNO tic-toc
  time is comparable to the run wall clock. New `--time-source {wall,cpu}` (default
  **wall**) — the GA now optimizes real wall-clock UNO time by default.
- `Evaluator` accumulates `total_uno_time` (sum of `cum_wall_time`) and `n_uno_calls`
  over cache **misses only** (a cache hit runs no UNO), and passes `time_source`
  through.
- `main` times the whole run with `perf_counter` and writes a new **`timing.json`**
  (`run_wall_s`, `uno_wall_s`, `ga_overhead_s`, `ga_overhead_fraction`, `uno_calls`,
  `n_evaluations`, `n_distinct_configs`). A Timing section was added to `RESULTS.md`
  and a timing block to the console summary. If `workers != 1`, both warn that the
  overhead is not directly meaningful (overlapping wall clocks). `n_evaluations` is
  read from `result.algorithm.evaluator` (pymoo runs on an internal copy, so the local
  `algorithm` has n_eval=0). Plot axis labels / prose changed "CPU time" → "UNO time".
- Note: `uno_wall_s` always uses the real tic-toc `cum_wall_time` even under
  `--time-source cpu`, so the overhead subtraction stays honest regardless of the
  objective's time metric.

- Verified (`python3`, pymoo 0.6.2): `py_compile` of both files; `evaluate_detailed`
  on 3 HS problems shows `cpu` vs `wall` differ and `wall` makes `cpu_time==wall_time`;
  bad `time_source` raises. End-to-end GA smoke (pop 4 × gen 2, serial, 4-problem temp
  set) wrote `timing.json` with run 2.84s − UNO 2.31s = overhead 0.53s (18.8%),
  `n_evaluations=8`. A `--workers 2 --time-source cpu` run correctly showed negative
  overhead + the overlap warning. All smoke artifacts (temp set + run folders) removed;
  pre-existing `results/ga_hs_model_all/` untouched. Nothing committed (per rule).

### Per-generation, per-population console output
Extended `scripts/ga_search.py` so each generation prints one line **per population
member**, not just a one-line summary. In `FrontSnapshot.notify` (fires at the end of
each generation, so the generation number from `algorithm.n_gen` is exact), it iterates
the surviving population `algorithm.pop` and prints, per member: reliability, the time
objective, `solved=n/N`, `eval_wall` (measured wall to evaluate that config), and the
full config (via `_fmt_config` + a `SHORT_KEYS` abbreviation map). A `-> gen N summary`
line follows (evals / distinct / front size / best). `Evaluator.evaluate` now records
`eval_wall` and `cum_wall_time` on each cache-miss rec so the callback can show per-member
wall time (cache hits reuse the original config's recorded `eval_wall`).
- New flag `--no-population` (summary line only); `--quiet` still suppresses everything.
- Verified: smoke run prints the per-member block for both generations with correct
  values; `--no-population` shows only the two summary lines; `--quiet` emits no
  per-generation output. Smoke artifacts removed. Nothing committed (per rule).

### Switched per-population output to LIVE streaming
Follow-up (user: quiet is off by default — confirmed it already was; the real ask was to
see members as they finish, not batched at the generation boundary). Moved the per-member
printing out of `FrontSnapshot.notify` (which fires only at a generation's end) into
`Evaluator._print_member`, called from `Evaluator.evaluate` right after each GA config is
scored — so on a long serial run the lines appear one at a time instead of after the whole
generation. Details:
- Generation numbering: while a generation is being evaluated, `Evaluator.gen` (bumped by
  the callback at each generation's *end*) lags by one, so the gen currently being evaluated
  is `self.gen + 1` (initial population → gen 1). `_print_member` prints a `generation N:`
  header when that value changes and resets the per-gen `pop` index. Verified correct on a
  pop 4 × gen 3 smoke run (headers 1/2/3, indices 0..3).
- Only GA members stream (label == "ga"); baselines are still printed by `main()`. Cache
  hits are tagged `(cached)` (the config's original `eval_wall` is shown). `FrontSnapshot`
  now only records the front + prints the end-of-generation summary line.
- `Evaluator` gained `verbose`/`per_individual` flags (from `--quiet` / `--no-population`);
  `FrontSnapshot` lost its `per_individual` param. All flags default to full live output.
- Verified: live per-member streaming with correct gen numbers and n_eval (4/8/12);
  `--no-population` → summary lines only; `--quiet` → no per-generation output. Smoke
  artifacts removed; real run dirs untouched. Nothing committed (per rule).

## 2026-07-14 — UNO threading finding + selectable HSL/MA27 binary in the GA

### Threading (answering "how many threads does UNO use?")
- The bundled `external/uno/bin/uno_ampl` links **libgomp (OpenMP)** and pulls in
  **MUMPS + OpenBLAS** from `external/uno/deps`. UNO exposes **no** thread run-time-option;
  threading is governed entirely by the libraries' defaults, which use **all available
  cores** when `OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS` are unset (28 cores here).
- Measured on `problems/CUTE/broydn7d` (`preset=ipopt`) with `/usr/bin/time -v`:
  default → **~1900–2600% CPU** (≈19–26 threads), wall ≈0.09s but **user CPU ≈2.5–3.5s**;
  `OMP_NUM_THREADS=1` → 97% CPU, user 0.07s; `OPENBLAS_NUM_THREADS=1` → 100% CPU. So the
  parallelism is **OpenMP-driven** (OMP is the lever; OpenBLAS alone made little difference
  here). Notably, pinning to 1 thread was *faster in wall clock* for this small problem
  (0.06–0.08s vs 0.18s) — the parallel overhead exceeds the benefit at small sizes.
- Implication for our timing work: `time_source="cpu"` (UNO-reported CPU) sums across
  threads, so it runs ~1 order of magnitude above wall on threaded regions; the tic-toc
  `wall` source is the honest per-solve elapsed time. Even at GA `--workers 1`, each UNO
  solve still uses many cores internally.

### Bundled UNO has only a STUB HSL (no real MA27)
- `external/uno/deps/libhsl.so` exists and the binary is linked to it, and the binary even
  has MA27/MA57 wrapper code compiled in — BUT the bundled libhsl is an **18 KB Julia
  HSL_jll stub** (each `ma27ad_`/`ma57ad_` is a 1-byte no-op; `LIBHSL_isfunctional` returns
  false), so UNO advertises only **MUMPS, SSIDS** and `linear_solver=MA27` → "The linear
  solver MA27 is unknown". This build also lacks runtime HSL loading (no `libhsl_path`
  option; not built with `-DHSL_RUNTIME_LOADING=ON`).

### User's own UNO build has real MA27 — made it selectable from `ga_search.py`
- The user's checkout `/home/sdinh/sandbox/Uno/build/uno_ampl` is built with real HSL
  (`.../Uno/dependencies/lib/libcoinhsl.so`) and advertises **MA57, MA27, MUMPS, SSIDS**;
  verified it solves hs071 with `linear_solver=MA27` (obj 17.01402, Success), including
  through `optiuno.run_uno` (option passed as `preset=ipopt linear_solver=MA27`).
- **`optiuno/objective.py`:** added `extra_options` kwarg to `evaluate_detailed` / `evaluate`
  / `make_objective` — a dict of **fixed, non-searched, unvalidated** UNO options merged into
  every solve (`run_options = {**config, **extra_options}`). CLI gained `--extra-option
  KEY=VALUE` (repeatable). `uno_bin` was already supported. Defaults unchanged (bundled
  binary, no extra options) so existing behavior/numbers are preserved.
- **`scripts/ga_search.py`:** added `--uno-bin` (default **system-first** via
  `optiuno.uno_runner.resolve_uno_bin`: `$UNO_AMPL_BIN` → PATH → bundled) and `--option
  KEY=VALUE` (repeatable, the fixed extra options). `Evaluator` forwards both to
  `evaluate_detailed`. A **preflight** parses `<bin> --strategies` and, if a requested
  `linear_solver` isn't advertised, exits 2 with a clear message **before** creating any
  output dir (prevents silently scoring every problem unsolved on a non-HSL binary). The
  resolved binary + fixed options are printed at startup and recorded in `timing.json`
  (`uno_bin`, `extra_options`) and the RESULTS "Setup" section (which no longer hard-codes
  "bundled").
- Usage: `python scripts/ga_search.py --uno-bin /home/sdinh/sandbox/Uno/build/uno_ampl
  --option linear_solver=MA27 ...` (or `export UNO_AMPL_BIN=.../Uno/build/uno_ampl` and drop
  `--uno-bin`).
- Verified (`py_compile` both files): MA27 run on the user binary solves and streams
  per-member output with `uno binary`/`fixed options` echoed and provenance in `timing.json`;
  MA27 on the bundled binary is rejected (exit 2, no output dir left); the objective CLI
  `--extra-option linear_solver=MA27 --uno-bin <user>` → 4/4 solved. Smoke artifacts removed;
  real run dirs (`ga_hs_model_all`, `ga_pop_24_gen_15_hs_model_all`) untouched. Bundled UNO
  and the user's UNO were **not** modified (read-only). Nothing committed (per rule).

### Worker-count sweep (16/8/4/1) with the user's MA27 binary — 4 sequential GA runs
Ran `ga_search.py` four times, identical settings except `--workers` (16, 8, 4, 1), all with
`--uno-bin /home/sdinh/sandbox/Uno/build/uno_ampl --option linear_solver=MA27
--problems problems/sets/hs_model_all.json` (defaults: pop 24, gen 15, seed 1, time_source=wall,
time_limit 20s). Outputs in `results/ga_pop_24_gen_15_hs_model_all/{20260714_184528 (w16),
_190819 (w8), _193532 (w4), _202336 (w1)}`.

| workers | run_wall (s) | best reliability | best config | wall-obj of best (s) | distinct | evals |
|--------:|-------------:|:----------------:|-------------|---------------------:|---------:|------:|
| 16 | 1370.7 | 0.9669 (117/121) | fr·IP·exact·primal_dual·LS·funnel | 8.87 | 187 | 358 |
|  8 | 1632.1 | 0.9669 (117/121) | fr·IP·exact·primal_dual·LS·funnel | 4.91 | 189 | 358 |
|  4 | 2883.5 | 0.9669 (117/121) | fr·IP·exact·primal_dual·LS·funnel | 2.95 | 195 | 358 |
|  1 | 7252.2 | 0.9669 (117/121) | fr·IP·exact·primal_dual·LS·funnel | 1.48 | 193 | 358 |

**Finding: the optimization OUTCOME is invariant to worker count** — same best reliability
(0.9669 = 117/121) and the *same* winning config in all four; baselines identical too
(filtersqp 0.9669, ipopt 0.9256 everywhere); 358 evals each; distinct configs 187–195 (±2%,
minor trajectory jitter from the noisy time tiebreaker). **What changes is only the time
numbers, and that's a threading artifact:** each UNO solve already uses ~all cores (OpenMP), so
N concurrent workers oversubscribe the 28-core box and inflate per-solve wall. The wall-time
objective of the *same* config spanned ~6× (8.87→4.91→2.95→1.48s as workers 16→8→4→1); the
filtersqp baseline time spanned ~7.7× (24.6→19.2→10.6→3.2s). Total run wall grew ~5.3× as
workers dropped (16→1) because less parallelism. GA overhead is only meaningful at workers=1:
**61.8 s = 0.9%** of the 7252 s run (UNO dominates; pymoo/caching/plot/I/O negligible).
Conclusion: absolute `cum_time` is NOT comparable across worker counts — use **workers=1** for
trustworthy time values (slow, ~2 h), higher workers only for faster search where you care about
reliability/relative ranking. Scratch console logs removed; the 4 result dirs kept. Read-only;
nothing committed.

## 2026-07-15 — All four UNO presets as baselines + `preset` column in every results CSV

Discovered UNO defines **four** built-in presets in `Uno/uno/options/Presets.cpp`, not two:
`ipopt`, `filtersqp`, and additionally **`funnelsqp`** (= filtersqp but funnel_method
globalization) and **`filterslp`** (= filtersqp but hessian_model=zero → SLP). `auto` (default)
is availability-based selection, not a fixed bundle. All four presets' six ingredients are
present in `optiuno/uno_search_space.json`, so they validate as baselines *and* are reachable by
the GA.

Changes to `scripts/ga_search.py` (per user request "run all presets and add to the result;
add a first column 'preset' to all CSVs, matching config→preset, else 'custom'"):
- `PRESET_INGREDIENTS` extended from 2→4 presets (added `funnelsqp`, `filterslp`) with the
  six-ingredient bundles from Presets.cpp; `PRESET_STYLE` given markers/colors for the two new
  ones (plots + RESULTS.md baseline table now show all four).
- New module-level `match_preset(options)`: returns the preset whose six ingredients equal the
  config (compared over the six search-space keys), else `"custom"`.
- Added a **leading `preset` column** to all three results CSVs — `evaluations.csv`,
  `ga_history.csv`, `pareto_front.csv` — populated via `match_preset`. So a GA-*discovered*
  config that happens to equal a preset bundle is labelled with that preset's name (not custom).
  Note: presets are matched/evaluated as six-ingredient configs (UNO-default numerics), the
  existing framework convention — a GA config with the same six ingredients is genuinely the
  same run, which is what makes the label accurate.
- Docstring updated to document the `preset` column and the four baselines.

Verified with a fast smoke run (bundled binary, pop 6 × gen 1, 3-problem set): all four
baselines evaluated; CSVs lead with `preset`; baselines labelled correctly; a GA-found config
matching funnelsqp's bundle was correctly labelled `funnelsqp` on the Pareto front; other GA
configs `custom`. Temp smoke artifacts removed. Read-only re UNO; nothing committed.

## 2026-07-15 — Back-fill `preset` column into the existing worker-sweep CSVs

Migrated the 12 pre-existing CSVs under `results/ga_pop_24_gen_15_hs_model_all/{20260714_184528,
_190819, _193532, _202336}` to the new format: inserted a leading `preset` column populated by
the *same* `scripts/ga_search.py:match_preset` (imported, not re-implemented) so labels are
identical to freshly-generated files. `evaluations.csv` matches on `options_json`,
`ga_history.csv` on `config_json`, `pareto_front.csv` on its six ingredient columns. In-place
rewrite, idempotent (skips a file whose first column is already `preset`). Row counts unchanged
(evaluations 187/189/195/193; ga_history 360 each = 2 old baselines + 358 GA calls;
pareto_front 2/1/1/3). Spot-check: baselines labelled `filtersqp`/`ipopt`, the GA-discovered
funnelsqp bundle labelled `funnelsqp`, the ipopt bundle on a front labelled `ipopt`, everything
else `custom` — matching by ingredients, as designed. **Note:** these runs predate the
four-preset change, so their `RESULTS.md` baseline tables still show only `filtersqp`/`ipopt`
(only two baselines were actually run then); I did not fabricate funnelsqp/filterslp baseline
numbers for them — only the CSV format was updated. Nothing committed.

## 2026-07-16 — Funnel method: investigation, figures, and crucible ingest

Investigated the `funnel_method` globalization strategy (arising from the four-preset work).
Read UNO source (`Uno/uno/ingredients/globalization_strategies/switching_methods/funnel_methods/`):
funnel = a single scalar `width` = monotonically-decreasing upper bound on infeasibility;
`acceptable(h): h<=width`; f-type/h-type switching. Established the origin paper is **Gould &
Toint, "Nonlinear programming without a penalty function or a filter," Math. Program. 122(1):
155-196, 2010** (DOI 10.1007/s10107-008-0244-7), confirmed via Crossref. Key finding: the
**Vanaret & Leyffer 2026 UNO paper does NOT mention funnel** — verified by reading its §4.1
(only merit + filter classes; 0 "funnel" hits across a faithful pdftotext extraction).

- Created two explanatory figures under `figures/`: `funnel_vs_waechter_filter.png` (side-by-side
  acceptance regions in the (eta,f) plane) and `funnel_vs_filter_overlap.png` (the four
  agree/disagree regions — shows neither acceptance region contains the other; funnel is a hard
  eta-cap indifferent to objective, filter trades objective vs infeasibility).
- User uploaded the Gould & Toint PDF to `References/`; read it and confirmed 1:1 correspondence
  with UNO's `Funnel` class (theta_k^max = width; f/c-iterations = f-type/h-type; "memory via the
  decreasing {theta_k^max}" vs a stored filter set). Caveat: paper is trust-region +
  equality-constrained; UNO generalizes funnel to pair with LS too.
- **Ingested it into the Crucible wiki** (`crucible ingest`, source ID 8, cite key `gould2010`):
  wrote summary `.crucible/wiki/summaries/gould-toint-2010-trust-funnel.org`; added a **Funnel
  methods** section to `.crucible/wiki/concepts/globalization-strategy.org` (previously merit +
  filter only) with cross-links; fixed the auto-added `references.bib` entry (proper
  journal/vol/pages/DOI). Ran `crucible sync` + `index`; `lint` clean (0 errors; only
  pre-existing index.org notes). `funnel` now returns both articles in search.
- Saved memory `funnel-method-reference.md`. Read-only re UNO; nothing committed.

## 2026-07-22 — Removed the committed `quickRun/.venv/`; standardized on the `sequential_OED` conda env

Removed the broken, checked-in `quickRun/.venv/` (4111 tracked `.pyc` files, ~70 MB, no `bin/` or
interpreter — the `.venv/bin/python` used throughout the docs never resolved). Runs now use the
developer's conda env `sequential_OED`; other users create their own env, with per-user install
instructions left as future work.

- **Code:** `quickRun/scripts/run_evolution.py` — dropped the dead `ROOT/.venv/bin/openevolve-run`
  fallback in `_find_openevolve_run()` (kept the `sys.executable`-adjacent → PATH resolution, which
  already finds the env's `openevolve-run`); updated its usage/resolution docstrings.
  `scripts/ga_search.py` — replaced the `/home/sdinh/anaconda3/bin/python` example with
  `conda run -n sequential_OED python`.
- **Docs:** `quickRun/CLAUDE.md`, root `CLAUDE.md`, `STATUS.md` — swapped every `.venv/bin/python`
  for `conda run -n sequential_OED python`, rewrote the "`.venv/` not committed" bullet as a
  "Python environment" note (dev env = `sequential_OED`; future-user install = TODO), and refreshed
  STATUS.md's stale Git section.
- **Git/ignore:** `git rm -r quickRun/.venv` (untracked 4111 files + deleted the dir); added
  `.venv/`, `__pycache__/`, `*.pyc` to the tracked `.gitignore`. The removal is **staged, not
  committed** (project rule — the user commits).
- **Validation:** no `.venv` remains in live `.py` or living docs; `run_evolution.py` /
  `ga_search.py` / `optiuno.uno_runner` `--help` all exit 0 under `sequential_OED`; `openevolve-run`
  resolves next to the env python and on PATH (so the removed fallback was safe); the new ignore
  rules match venv/cache paths. Nothing committed.
