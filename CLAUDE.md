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
venvs/conda envs and documented in `STATUS.md`, not pinned in a file). There is no
automated test suite; correctness is checked by sanity scripts (below).

- `optiuno/` — the **shared library**, imported by everything else:
  - `uno_runner.py` — `run_uno(nl, options=..., preset=..., time_limit=...)` drives one
    `uno_ampl` subprocess and returns a typed `UnoResult`. Also a CLI (`python -m
    optiuno.uno_runner`). This is the single merged UNO driver. (stdlib-only)
  - `utils.py` — `select_uno_bin()` / `bundled_uno_bin()`, the **one authority** for where
    the UNO binary lives. (stdlib-only)
  - `objective.py` — the search-driver-agnostic black-box objective
    `evaluate(config, problem_set) -> (reliability, cum_cpu_time)`. (stdlib-only)
  - `harness/` — the **openEvolve evaluation core**: `benchmark.evaluate_config(options)`
    sweeps one config over the whole HS `.nl` set (ThreadPool) and aggregates
    `reliability`/`cum_cpu_time`/`n_rewritten` with a config-hash cache; `classify.py` turns
    one `UnoResult` into solved/unsolved/timeout/invalid/crash and detects silent rewrites.
  - `evolve/` — the **openEvolve search space + entry points**: `initial_program.py` (the
    six-key `UNO_CONFIG` that is the *only* thing mutated), `evaluator.py` (validate + score),
    and `config.yaml` / `config-claude-code.yaml` (LLM + search-algorithm settings only).
- `scripts/` — standalone CLI tooling (run from the repo root):
  - **CUTE corpus pipeline** (`requests`/`bs4`/`amplpy`): `scrape_cute.py` downloads the
    COCONUT Library2 CUTE set; `problem_parser.py` converts `.mod`→`.nl` via AMPL.
  - **searches over the objective**: `ga_search.py` (NSGA-II via pymoo) and the openEvolve
    driver `run_evolution.py`, plus `plot_pareto.py`, `validate_presets.py`, `variance_runs.py`,
    and the one-time `translate_models.py`.
- `problems/` — the two benchmark corpora (see `STATUS.md` for exact counts):
  `CUTE/` (full 727-problem COCONUT set, one folder per problem) and `HS_model/` (the
  Hock–Schittkowski `.nl` subset the openEvolve/GA search runs on).
- `external/uno/` — a bundled self-contained UNO v2.8.0 build (binary + `lib/` + `deps/`),
  used repo-wide as the fallback binary and pinned by the openEvolve benchmark
  (`optiuno/harness/benchmark.py`) for reproducibility.
- `results/quickRun/` — the openEvolve search outputs: checked-in **finished outputs**
  (RESULTS.md, pareto plots, preset validation) at the top level, plus `cache/` (the
  config-hash eval cache, makes re-runs free) and `openevolve_run/` (the live-write target
  for fresh runs — evaluations/history CSVs, `best/`, a checkpoint, per-problem logs). Other
  GA-search outputs live in sibling `results/ga_*` dirs. Read these for prior findings.
- `References/` — the source PDFs. `plan/` — design docs.

## Architecture (how the pieces fit)

Everything funnels through **one function, `optiuno.run_uno`**, and one binary-resolution
helper. Key facts that are non-obvious from any single file:

- **UNO is invoked only as a subprocess**, never linked or modified. A "configuration" is a
  preset name and/or a dict of `key=value` run-time-options; custom options are placed after
  `preset=` on the command line so they override the preset (UNO's own parse order).
- **`uno_ampl` exits 0 even when a solve fails.** Outcome is therefore classified from the
  printed `Optimization status:` line, *not* the exit code — in `optiuno.uno_runner.classify`
  (solved/budget/error/failed/timeout) and, for the search, in `optiuno/harness/classify.py`.
  Never treat return code as success.
- **Binary selection is system-first**: explicit `uno_bin=`/`--uno-bin` → `$UNO_AMPL_BIN` →
  `uno_ampl` on `PATH` → bundled `external/uno/`. When the resolved binary is a self-contained
  release layout, `run_uno` auto-wires `LD_LIBRARY_PATH` from its `lib/`+`deps/`. A system UNO
  build can be selected with `export UNO_AMPL_BIN=/path/to/uno_ampl`.
- **Invalid/silently-rewritten configs** are a first-class concern: UNO echoes the actually
  composed method as a banner (captured in `UnoResult.banner`), so callers can detect when a
  run tested a *different* config than requested. The openEvolve harness surfaces this as
  `n_rewritten` (see the paper's §5.3.5): requesting a filter/funnel strategy on the ~11
  unconstrained/bound-only HS problems is silently rewritten to `LS merit_function`, so
  strategy comparisons are effectively over the ~112 constrained problems.
- **The search pipeline's inputs live in code, not the openEvolve YAML.** `scripts/run_evolution.py`
  hands `openevolve-run` two files: `optiuno/evolve/initial_program.py` (the six-key `UNO_CONFIG`
  in the `EVOLVE-BLOCK` — the *only* thing mutated, i.e. the search space) and
  `optiuno/evolve/evaluator.py` (legal values in `ALLOWED` + the `combined_score` scoring,
  `= reliability + 0.1·max(0, 1 − cum_cpu_time/60)`: reliability dominates, CPU time breaks
  ties). The `.nl` **test set** is the hard-coded `NL_DIR` in `optiuno/harness/benchmark.py`
  (`problems/HS_model/`). `optiuno/evolve/config.yaml` / `config-claude-code.yaml` hold **only**
  LLM + search-algorithm settings — they do *not* select the test set or the search space. The
  layered evaluation core is `run_uno` (one solve) → `harness.benchmark.evaluate_config` (one
  config over the whole set, cached by config hash under `results/quickRun/cache/`) →
  `evolve.evaluator.evaluate` (validate + score for openEvolve).
- **Gotchas from prior runs** (see `results/quickRun/` + `LOGBOOK.md`): UNO 2.8.0 accepts all
  240 nominal ingredient combinations (the 2.2.0 paper prohibited `interior_point`+`TR`), so
  invalid/rewritten/failed configs are caught by the harness, not by refusing to run. The
  `inertia_correction_strategy=primal_dual × inequality_constrained` region fails fast
  ("Algorithmic error") on nearly every problem. The six-ingredient search is a **lower bound**:
  the `ipopt` *preset* (0.984 reliability) beats its bare ingredients (0.927) because ~30
  non-ingredient options carry it, and those are outside the search space. CPU-time noise is
  5–15% relative sd; reliability is noise-free.

## External dependencies (installed outside this repo)

The README specifies these are installed in the workspace, *not* committed here:
- **UNO** — https://github.com/cvanaret/Uno (the solver being tuned)
- **openEvolve** — https://github.com/algorithmicsuperintelligence/openevolve, and/or **Google AlphaEvolve** (the search drivers)

## Commands

Run from the repo root. The UNO driver + corpus pipeline are stdlib/`amplpy`; the openEvolve
and GA searches run under your Python environment (dev: conda env `sequential_OED`, which has
`openevolve`, `amplpy`, `numpy`, `matplotlib`, `pyyaml`, `pymoo`).

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

# Evolutionary / GA search + preset sanity-check — run from the repo root under the conda
# env sequential_OED, e.g.:
#   conda run -n sequential_OED python scripts/validate_presets.py       # sanity-check harness vs. published paper
#   conda run -n sequential_OED python scripts/run_evolution.py [--smoke]  # openEvolve search
#   conda run -n sequential_OED python scripts/ga_search.py [--generations N]  # NSGA-II search
# Run one config directly through the harness:
#   conda run -n sequential_OED python -c "from optiuno.harness.benchmark import evaluate_config; print(evaluate_config({'preset':'ipopt'}))"
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
