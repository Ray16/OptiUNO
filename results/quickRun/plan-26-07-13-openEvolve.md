# OptiUNO — Multi-objective search over UNO's six ingredient options

## Context

OptiUNO's core experiment: treat UNO's six *ingredient* run-time options as optimization variables and search for configurations that beat the shipped presets (`filtersqp`, `ipopt`). This plan builds the first end-to-end experiment: a testing environment driven by **openEvolve** that optimizes **two competing objectives** over the **full Hock–Schittkowski set (~115 problems)** from Vanderbei's AMPL collection:

1. **Reliability** — fraction of test problems solved (maximize)
2. **Cumulative CPU time** — summed over all problems (minimize)

plus, for reference, the **empirical variance of cumulative CPU time** (from repeated runs of the final Pareto-front configurations and presets — not an objective).

**Deliverables:** (1) an openEvolve testing environment searching the six ingredient options; (2) the HS benchmark set as `.nl` files; (3) run outputs — UNO logs and Pareto-front images over evolution iterations.

## Decisions already made (with the user)

| Decision | Choice |
|---|---|
| Search driver | **openEvolve** (pip; AlphaEvolve not used) |
| LLM backend | **Anthropic API key**, via Anthropic's OpenAI-compatible endpoint. **Model is a configurable setting; default `claude-sonnet-5`** (changeable in `evolve/config.yaml` / env var, e.g. to `claude-haiku-4-5` for cheaper runs) |
| Setup rights | **Project-local only**: I may create `OptiUNO/.venv` and download into `OptiUNO/external/`. Nothing outside this folder is touched; both git-ignored |
| Test set | **Full HS set (~115 problems)** from Vanderbei's CUTE collection |

## Key findings from research (answers the user asked for)

- **Python vs C++ interface:** `unopy` defines problems **via Python callbacks only — it cannot read `.nl` files**. The native **`uno_ampl`** executable reads `.nl` directly, takes options as `option=value` command-line pairs (`uno_ampl model.nl -AMPL preset=filtersqp globalization_mechanism=LS ...`). → **Use `uno_ampl`.** Bonus: CPU timing is uncontaminated by Python callback overhead.
- **System `uno_ampl` (`/usr/local/bin`) is broken** — missing `libhighs.so.1`. → Use the **self-contained UNO v2.8.0 release tarball** (`Uno_binaries.v2.8.0.x86_64-linux-gnu-cxx11.tar.gz`, published 2026-07-10) unpacked into `external/uno/`, invoked with `LD_LIBRARY_PATH` pointing at its bundled libs.
- **Vanderbei ships `.mod`, not `.nl`** — one-time translation via the pip-installable AMPL demo module (`amplpy` + `ampl-module-base`, demo license caps at 500 vars/cons; every HS problem is far below). Models that fail to translate are logged and skipped.
- **Search space:** six ingredients → 240 nominal combos, 180 legal after removing the prohibited `interior_point`+`TR` (from `uno-options.json`, built last session). Complete enumeration would be feasible as ground truth but is **deliberately deferred to a later session** (user decision); this session validates the harness against the published paper results instead.

## Directory layout (all new, all inside OptiUNO/)

```
OptiUNO/
├── .gitignore            # .venv/ external/ models/ results/ __pycache__/
├── setup.sh              # reproducible setup script (venv, pip, UNO tarball, model download)
├── external/uno/         # UNO v2.8.0 binaries + shared libs (downloaded)
├── .venv/                # openevolve, amplpy+ampl-module-base, numpy, matplotlib, pyyaml
├── models/
│   ├── mod/hs*.mod       # downloaded from vanderbei.princeton.edu/ampl/nlmodels/cute/
│   └── nl/hs*.nl         # translated once via amplpy demo module
├── harness/
│   ├── uno_runner.py     # one (config, .nl) run → status, iterations, CPU time, log path
│   ├── classify.py       # parse UNO output → solved / failed / invalid / silently-rewritten
│   ├── benchmark.py      # sweep config over all .nl in parallel; caching; metrics
│   └── cache/            # per-config results keyed by config hash (JSON)
├── evolve/
│   ├── initial_program.py  # EVOLVE-BLOCK: dict of the six ingredient options (start = filtersqp values)
│   ├── evaluator.py        # runs benchmark.py sweep → metrics for openEvolve
│   └── config.yaml         # openEvolve config: Anthropic endpoint, model (default claude-sonnet-5), MAP-Elites features
├── scripts/
│   ├── run_evolution.py    # launch openEvolve, snapshot Pareto front each checkpoint
│   ├── validate_presets.py # presets on HS set vs. published paper results (arXiv 2406.13454)
│   └── plot_pareto.py      # front-over-iterations figure + final front vs. presets
├── references/arxiv-2406.13454/   # downloaded tex source of the paper (validation data)
├── results/
│   ├── logs/<config-hash>/<problem>.log   # raw UNO logs (deliverable 3)
│   ├── evaluations.csv                    # every (config, metrics) evaluated
│   ├── pareto_evolution.png, pareto_final.png
│   └── RESULTS.md                         # findings write-up
└── STATUS.md             # created at last (required by CLAUDE.md, still missing)
```

## Implementation steps

### Phase 0 — Setup (`setup.sh`, then run it)
1. `python3 -m venv .venv`; pip install `openevolve amplpy ampl-module-base numpy matplotlib pyyaml` into it.
2. Download + unpack UNO v2.8.0 Linux x86_64 tarball into `external/uno/`; smoke-test `LD_LIBRARY_PATH=external/uno/lib external/uno/bin/uno_ampl --strategies` and record which QP/LP/linear solvers the binary actually supports (resolves last session's open question; cross-check against `uno-options.json`).
3. Verify `ANTHROPIC_API_KEY` is set (check only, never print). If unset, stop and ask the user to export it.
4. Write `.gitignore`. **Nothing is ever committed** (hard rule).

### Phase 1 — Benchmark set
1. Download all `hs*.mod` from Vanderbei's CUTE index (~115 files) into `models/mod/`.
2. Translate each to `.nl` with the amplpy demo module (`ampl.read(mod); ampl.eval('write gmodels/nl/hsNNN;')` equivalent). **Models that fail to translate (e.g. those needing `funcadd.c` or exceeding the demo license) are removed from the test set and reported, with the failure reason, in a separate file `models/untranslatable.md`.**
3. Sanity sweep: run every `.nl` once with `preset=auto`; problems that no preset solves are kept but flagged (they penalize every config equally).

### Phase 2 — Harness
- `uno_runner.py`: build the command `uno_ampl <nl> -AMPL <opt>=<val>...`, run via `subprocess` with a **watchdog timeout** (default 30 s) *and* UNO's own `time_limit`; measure the child's CPU time with `os.wait4`/`resource` (user+sys). Store the full UNO log.
- `classify.py`: parse termination status. **"Solved" = converged to a feasible KKT point within the limit**; feasible FJ point, infeasible stationary, small-TR exit, loose-tolerance fallback, timeout, crash are recorded as distinct outcomes (UNO.pdf §5.3.7). Detect UNO's *silent-override warnings* in the log and tag the run `rewritten` (the dangerous third failure mode from the LOGBOOK). Reject `interior_point`+`TR` up front as `invalid` without running.
- `benchmark.py`: given a six-ingredient config → run all problems in parallel (`multiprocessing`, ~cpu_count workers) → metrics: `reliability` (fraction solved), `cum_cpu_time` (sum of measured CPU seconds; unsolved runs contribute their actual consumed time, capped at the limit — the reliability axis handles the fast-failure pathology). **Cache by config hash**: only 180 distinct configs exist, so evolution + enumeration share results and re-evaluations are free.

### Phase 3 — openEvolve integration
- `initial_program.py`: an EVOLVE-BLOCK containing only the six-option dict, initialized to the `filtersqp` preset values; comments in the block list the legal values per option (from `uno-options.json`) so the LLM mutates within the catalogue.
- `evaluator.py`: import the dict, call the cached benchmark sweep, return `EvaluationResult(metrics={reliability, neg_log_cum_time, combined_score}, artifacts={uno_status_counts, sample_log_tail})` — artifacts feed failure info back to the LLM.
- `config.yaml`: Anthropic OpenAI-compatible endpoint (`api_base: https://api.anthropic.com/v1`), **`model: claude-sonnet-5` as the default, read from an overridable setting** (yaml key + `OPTIUNO_EVOLVE_MODEL` env override); MAP-Elites `feature_dimensions: [reliability, cum_cpu_time]` — the archive itself then maintains the Pareto-diverse population; ~150–200 iterations; checkpoint every 10.
- `run_evolution.py`: drives openEvolve; after every checkpoint dumps the current non-dominated set to `results/front_iter_NNN.json` for the evolution plot.
- Baselines first: evaluate `filtersqp` and `ipopt` preset-equivalent ingredient configs before evolution starts; they anchor the plots.

### Phase 4 — Validation against published results + variance
- **No enumeration this session** — the comparison to complete enumeration is deferred to a later session.
- Download the paper's tex source from **arXiv 2406.13454** (`arxiv.org/e-print/2406.13454`) into `references/arxiv-2406.13454/` and extract: (a) the list of `hsNNN` problems included in the 429-problem CUTE benchmark, and (b) the reported results for the `filtersqp` and `ipopt` presets relevant to those problems.
- `validate_presets.py`: run both presets through our harness on the HS test set and compare against the paper's numbers. If the tex only contains aggregate tables (shifted geometric means over all 429 problems), fall back to the authors' public per-problem logs at `github.com/cvanaret/nonlinear_optimization_solver_benchmark` for HS-level solved/unsolved and evaluation counts. Any discrepancy (problem solved by the paper's runs but not ours, or vice versa) is listed in `results/preset_validation.md` — this is the acceptance gate for the python↔UNO connection before evolution runs.
- Variance: re-run each final-front config + both presets **R = 10 times**; report mean, empirical variance, and std of `cum_cpu_time` in `RESULTS.md`.

### Phase 5 — Outputs & bookkeeping
- `plot_pareto.py`: (a) `pareto_evolution.png` — fronts at successive checkpoints, color-graded by iteration, presets marked; (b) `pareto_final.png` — final evolved front vs. exact enumerated front vs. presets, with variance error bars on time.
- `results/RESULTS.md`: metric definitions, solved-status table per config class, front analysis, preset-validation summary. (Enumeration comparison deferred.)
- End of session per CLAUDE.md: **append** LOGBOOK entry; **create/overwrite `STATUS.md`** (finally resolves the missing-file issue).

## Constraints honored
- No `git commit`/`push` ever; all generated dirs git-ignored.
- UNO used strictly through run-time options; source never touched.
- All installs confined to `OptiUNO/.venv` and `OptiUNO/external/` (explicitly authorized); no system changes.
- No file access outside `OptiUNO/`.

## Verification
1. `uno_ampl --strategies` runs from the tarball (self-contained check).
2. Single-problem smoke test: `hs015.nl` with `preset=filtersqp` solves; parsed status/iterations/CPU time match the raw log.
3. Baseline sanity: `ipopt`/`filtersqp` presets achieve high reliability on HS (paper says they should).
4. Invalid-combo check: `interior_point`+`TR` is classified `invalid`, never executed.
5. **Preset validation (acceptance gate):** harness results for `filtersqp`/`ipopt` on the HS set agree with the published results extracted from the arXiv 2406.13454 tex (per-problem logs repo as fallback); disagreements documented in `results/preset_validation.md` before evolution starts.
6. 5-iteration mini-evolution run end-to-end (LLM reachable, evaluator returns metrics, checkpoint front files written) before the full run.

## Open risks (flagged, not blockers)
- Some `.mod` files may not translate under the demo license or need `funcadd.c` → **removed from the test set and reported per-problem in `models/untranslatable.md`**; test-set size may land slightly under 115.
- The arXiv preprint may differ from the published MPC version (problem set, tables); if the tex lacks HS-level detail, the authors' public benchmark-logs repo is the per-problem source of truth for validation.
- CPU-time noise on tiny HS problems is real — exactly why the variance measurement is in scope; timing uses process CPU time (not wall clock) to reduce it.
- Which QP/LP/linear solvers the release binary contains is unknown until Phase 0's `--strategies` probe; solver options stay at binary defaults (only the six ingredients are searched).
