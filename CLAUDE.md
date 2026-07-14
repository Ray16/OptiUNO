# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Rules

- **Never commit changes.** Do not run `git commit` or `git push`. Only the user runs git commit manually.
- **Never modify UNO source code** unless explicitly authorized by the user. UNO is treated as an external, read-only dependency — interact with it only through its `run-time-options`.
- **Never modify the user's environment.** Do not install, upgrade, or remove packages, or change environment/system configuration. You may only *check* whether packages/dependencies are installed; if something is missing, **suggest** a fix and let the user run it.
- **Stay within this project directory.** Only read, explore, or operate on this folder (`OptiUNO/`) and its subfolders. Do NOT explore, read, or traverse any parent or sibling folders on the user's computer.
- **Session logging.** At the **start** of every session, read `LOGBOOK.md` and `STATUS.md` to load context. At the **end** of every session, update both:
  - `LOGBOOK.md` — an append-only history. **Never overwrite or edit existing lines**; only add new dated entries describing the changes and actions taken.
  - `STATUS.md` — overwritten each time to reflect the current state of the project.

## What this project is

OptiUNO searches for optimal configurations of **UNO (Unified Nonlinear Optimizer)**. UNO is a single solver whose behavior is composed at runtime from interchangeable strategy building blocks (constraint reformulation, step computation, globalization mechanism — line-search vs. trust-region — and globalization strategy). There are at least 186 valid combinations; only a handful (shipped as UNO `presets`) have been explored. The goal is to discover configurations that outperform the presets, potentially specialized per problem class.

The core experiment maps directly onto an optimization problem:
- **Optimization variables** = UNO's `run-time-options` (the strategy combination).
- **Objective / performance metric** = e.g. total CPU-time, time variance, or iteration count (metric choice is an open design question; may be multi-objective).
- **Optimizer** = an evolutionary search driver (openEvolve or AlphaEvolve), with complete enumeration as a fallback if the evolutionary approach underperforms.
- **Test set** = a benchmark problem suite, e.g. the Hock-Schittkowski problems from Vanderbei's AMPL nonlinear models.

Note: **not every combination of `run-time-options` is valid** — some fail outright. Any experiment harness must detect and gracefully skip failing configurations rather than treating them as valid data points.

## Repository layout

Python, no build system and no dependency manifest (deps are installed into ad-hoc
venvs/conda envs and documented in `STATUS.md` + `quickRun/CLAUDE.md`, not pinned in a
file). There is no automated test suite; correctness is checked by sanity scripts (below).

- `optiuno/` — the **shared library** (stdlib-only), imported by everything else:
  - `uno_runner.py` — `run_uno(nl, options=..., preset=..., time_limit=...)` drives one
    `uno_ampl` subprocess and returns a typed `UnoResult`. Also a CLI (`python -m
    optiuno.uno_runner`). This is the single merged UNO driver.
  - `utils.py` — `select_uno_bin()` / `bundled_uno_bin()`, the **one authority** for where
    the UNO binary lives.
- `scripts/` — the **CUTE corpus pipeline** (uses `requests`/`bs4`/`amplpy`):
  `scrape_cute.py` downloads the COCONUT Library2 CUTE set; `problem_parser.py` converts
  `.mod`→`.nl` via AMPL.
- `problems/` — the two benchmark corpora (see `STATUS.md` for exact counts):
  `CUTE/` (full 727-problem COCONUT set, one folder per problem) and `HS_model/` (the
  Hock–Schittkowski `.nl` subset the `quickRun` search runs on).
- `quickRun/` — the **evolutionary-search subproject** (openEvolve over UNO's six
  "ingredient" options). **It has its own detailed `quickRun/CLAUDE.md` — read that before
  working there.**
- `external/uno/` — a bundled self-contained UNO v2.8.0 build (binary + `lib/` + `deps/`),
  used repo-wide as the fallback binary and pinned by the `quickRun` benchmark for
  reproducibility.
- `results/quickRun/` — checked-in **finished outputs** from prior runs (RESULTS.md,
  pareto plots, preset validation). Read these for prior findings.
- `References/` — the source PDFs. `plan/` — design docs.

## Architecture (how the pieces fit)

Everything funnels through **one function, `optiuno.run_uno`**, and one binary-resolution
helper. Key facts that are non-obvious from any single file:

- **UNO is invoked only as a subprocess**, never linked or modified. A "configuration" is a
  preset name and/or a dict of `key=value` run-time-options; custom options are placed after
  `preset=` on the command line so they override the preset (UNO's own parse order).
- **`uno_ampl` exits 0 even when a solve fails.** Outcome is therefore classified from the
  printed `Optimization status:` line, *not* the exit code — in `optiuno.uno_runner.classify`
  (solved/budget/error/failed/timeout) and, for the search, in `quickRun/harness/classify.py`.
  Never treat return code as success.
- **Binary selection is system-first**: explicit `uno_bin=`/`--uno-bin` → `$UNO_AMPL_BIN` →
  `uno_ampl` on `PATH` → bundled `external/uno/`. When the resolved binary is a self-contained
  release layout, `run_uno` auto-wires `LD_LIBRARY_PATH` from its `lib/`+`deps/`. A system UNO
  build can be selected with `export UNO_AMPL_BIN=/path/to/uno_ampl`.
- **Invalid/silently-rewritten configs** are a first-class concern: UNO echoes the actually
  composed method as a banner (captured in `UnoResult.banner`), so callers can detect when a
  run tested a *different* config than requested. The `quickRun` harness surfaces this as
  `n_rewritten`.
- **The search pipeline's inputs live in code, not the openEvolve YAML.** `run_evolution.py`
  hands `openevolve-run` two files: `evolve/initial_program.py` (the six-key `UNO_CONFIG` in
  the `EVOLVE-BLOCK` — the *only* thing mutated, i.e. the search space) and `evolve/evaluator.py`
  (legal values in `ALLOWED` + the `combined_score` scoring). The `.nl` **test set** is the
  hard-coded `NL_DIR` in `harness/benchmark.py` (`problems/HS_model/`). `evolve/config.yaml` /
  `config-claude-code.yaml` hold **only** LLM + search-algorithm settings — they do *not* select
  the test set or the search space. The layered evaluation core is
  `run_uno` (one solve) → `benchmark.evaluate_config` (one config over the whole set, cached) →
  `evaluator.evaluate` (validate + score for openEvolve). See `quickRun/CLAUDE.md` for details.

## External dependencies (installed outside this repo)

The README specifies these are installed in the workspace, *not* committed here:
- **UNO** — https://github.com/cvanaret/Uno (the solver being tuned)
- **openEvolve** — https://github.com/algorithmicsuperintelligence/openevolve, and/or **Google AlphaEvolve** (the search drivers)

## Commands

Run from the repo root. `optiuno` and `scripts/` are stdlib/`amplpy`; `quickRun` needs its
own venv (see `quickRun/CLAUDE.md`).

```bash
# Solve one problem with a config (CLI). --json for machine-readable UnoResult.
python -m optiuno.uno_runner problems/HS_model/hs071.nl --preset ipopt
python -m optiuno.uno_runner <nl> --option globalization_mechanism=LS --option hessian_model=exact --json

# Same thing as a library call
python -c "from optiuno import run_uno; print(run_uno('problems/HS_model/hs071.nl', preset='ipopt'))"

# Discover valid strategy blocks / all run-time-options (from UNO itself)
uno_ampl --strategies      # the "wheel" ingredient values
uno_ampl --dump-options    # every option

# Rebuild the CUTE corpus (needs requests/bs4 + amplpy with a license permitting `write`)
python scripts/scrape_cute.py
python scripts/problem_parser.py --only hs071 [--presolve] [--force]

# Evolutionary search + preset sanity-check — see quickRun/CLAUDE.md for the full pipeline,
# run from quickRun/ with its venv, e.g.:
#   .venv/bin/python scripts/validate_presets.py     # sanity-check harness vs. published paper
#   .venv/bin/python scripts/run_evolution.py [--smoke]
```

## Key references

- `References/Vanaret and Leyffer_2026_Implementing a unified solver for nonlinearly constrained optimization.pdf` — the UNO paper (Vanaret & Leyffer, MPC 2026), the authoritative description of the strategy building blocks (see §5.3.5 on silent rewrites).
- `References/Novikov et al._AlphaEvolve A coding agent for scientific and algorithmic discovery.pdf` — the AlphaEvolve paper (one candidate search driver).
- UNO docs: https://unosolver.readthedocs.io/en/latest/

<!-- crucible-project -->
## Crucible Knowledge Base

This project has a Crucible knowledge base in `.crucible/`.
Use the `crucible` CLI to ingest sources, search, and maintain the wiki.

Layout: `.crucible/sources/` (primary sources), `.crucible/wiki/` (distilled articles),
`.crucible/crucible.db` (graph database).

Conventions: org-mode with scimax, org-ref citations, narrative prose.
The LLM maintains the wiki; manual edits are the exception.
Run `crucible help all` for the full CLI reference.
<!-- crucible-project -->

<!-- crucible-knowledge-base -->
## Crucible Knowledge Base

A curated knowledge base is available at `/home/sdinh/sandbox/OptiUNO`.
Before answering domain-specific questions, check if the knowledge base
covers the topic by reading the manifest:
`/home/sdinh/sandbox/OptiUNO/.crucible/wiki/MANIFEST.md`

If relevant, use `crucible search "query"` and `crucible concept <name>`
to find articles. Run `crucible help all` for the full CLI reference.
Always `cd /home/sdinh/sandbox/OptiUNO` before running crucible commands.
<!-- crucible-knowledge-base -->
