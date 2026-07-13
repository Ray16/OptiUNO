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
