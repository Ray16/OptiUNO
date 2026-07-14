# Status

_Last updated: 2026-07-13_

## Current state

Planning phase — design agreed, **no code yet**. The initial pipeline plan is
written and saved for further planning before implementation.

- `README.md` — project goals (find optimal UNO strategy configs via evolutionary search / enumeration).
- `RelevantFiles/` — UNO reference paper (Vanaret & Leyffer, MPC 2026).
- `CLAUDE.md` — guidance + 5 project rules.
- `plan/optiuno-initial-plan.md` — the agreed initial pipeline plan (not approved for implementation yet).

## Key design decisions (confirmed)

- **Toolchain**: `unopy` (pip, Python 3.10+) — problems defined via Python callbacks; options via `set_option`/`set_preset` then `optimize`.
- **Test set**: start with a hand-coded Hock-Schittkowski subset; CUTEst→callbacks bridge later.
- **Two drivers**: enumeration + openEvolve, sharing one core runner (`run_case` = one problem × one config); enumeration validates openEvolve.
- **Metric**: robustness then speed (lexicographic — # solved, then CPU time).
- **Feasibility**: two layers — a priori predicate rules (preset-validated) + persisted empirical `results/infeasible.json` ledger (conservative 100%-fail exclusion).

## Next steps

- Continue planning / refine `plan/optiuno-initial-plan.md` before writing code.
- When ready to implement: check `unopy` / `openevolve` are installed (suggest installs only, per rules).
- Port `hs015` as the first callback problem and stand up `run_case` with a smoke test (`objective ≈ 306.5`).
