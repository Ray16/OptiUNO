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
- Ran a planning session (`/plan`) to sketch the initial project pipeline.
- Researched the toolchain (read-only web/docs, no installs): confirmed `unopy` is a pip package that solves models via **Python callbacks** (`unopy.Model` + `UnoSolver.set_option`/`set_preset` → `optimize`); identified the strategy option keys/values that form the search space; and extracted how the presets (filtersqp, ipopt, funnelsqp, filterslp) map to consistent option combinations.
- Confirmed design decisions with the user: (a) start with a hand-coded Hock-Schittkowski subset (CUTEst bridge later), (b) two independent drivers — enumeration + openEvolve — sharing one core runner, with enumeration validating openEvolve, (c) metric = robustness then speed (lexicographic).
- Designed `run_case` as the atomic unit (one problem × one config) and a **two-layer feasibility tracking** scheme: a priori predicate rules (with reason strings, preset-validated) + a persisted empirical `results/infeasible.json` ledger (conservative 100%-fail exclusion).
- Saved the plan document to `plan/optiuno-initial-plan.md`. **No code implemented** — further planning to come before implementation.
