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

## Project status

This repository currently contains **only planning material** — a `README.md` describing the project goals and a reference paper in `RelevantFiles/`. There is no source code, build system, or tests yet. Expect to scaffold these from scratch. Update this file once the structure (language, dependency manager, harness for running experiments) is chosen.

## What this project is

OptiUNO searches for optimal configurations of **UNO (Unified Nonlinear Optimizer)**. UNO is a single solver whose behavior is composed at runtime from interchangeable strategy building blocks (constraint reformulation, step computation, globalization mechanism — line-search vs. trust-region — and globalization strategy). There are at least 186 valid combinations; only a handful (shipped as UNO `presets`) have been explored. The goal is to discover configurations that outperform the presets, potentially specialized per problem class.

The core experiment maps directly onto an optimization problem:
- **Optimization variables** = UNO's `run-time-options` (the strategy combination).
- **Objective / performance metric** = e.g. total CPU-time, time variance, or iteration count (metric choice is an open design question; may be multi-objective).
- **Optimizer** = an evolutionary search driver (openEvolve or AlphaEvolve), with complete enumeration as a fallback if the evolutionary approach underperforms.
- **Test set** = a benchmark problem suite, e.g. the Hock-Schittkowski problems from Vanderbei's AMPL nonlinear models.

Note: **not every combination of `run-time-options` is valid** — some fail outright. Any experiment harness must detect and gracefully skip failing configurations rather than treating them as valid data points.

## External dependencies (installed outside this repo)

The README specifies these are installed in the workspace, *not* committed here:
- **UNO** — https://github.com/cvanaret/Uno (the solver being tuned)
- **openEvolve** — https://github.com/algorithmicsuperintelligence/openevolve, and/or **Google AlphaEvolve** (the search drivers)

## Key references

- `RelevantFiles/Implementing a unified solver for nonlinearly constrained optimization.pdf` — the UNO paper (Vanaret & Leyffer, MPC 2026), the authoritative description of the strategy building blocks.
- UNO docs: https://unosolver.readthedocs.io/en/latest/
