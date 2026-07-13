# Status

_Last updated: 2026-07-13_

## Current state

Planning phase. Repository contains only planning material — no source code, build system, or tests yet.

- `README.md` — project goals (find optimal UNO strategy configurations via evolutionary search / enumeration).
- `RelevantFiles/` — UNO reference paper (Vanaret & Leyffer, MPC 2026).
- `CLAUDE.md` — guidance and rules for Claude Code.

## Next steps

- Install external dependencies in the workspace (not in this repo): UNO, and openEvolve and/or AlphaEvolve.
- Select a benchmark test set (e.g. Hock-Schittkowski problems).
- Decide on the performance metric(s) / objective.
- Scaffold an experiment harness that runs UNO with a given `run-time-options` config and detects invalid/failing combinations.
