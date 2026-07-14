# Preset validation against arXiv:2406.13454 (Uno paper)

Paper benchmark: Uno **2.2.0**; this harness: Uno **2.8.0** (release binaries). Agreement is judged on solved/failed status; objective-evaluation counts are reported for reference and may legitimately differ across versions.

**Caveat on model provenance:** the paper used the Neumaier/COCONUT AMPL translations of CUTE (see footnote in its Sec. 7), while this project uses Vanderbei's translations. Formulation or starting-point differences between the two translations can explain residual per-problem discrepancies beyond the solver-version gap.

- Problems in our HS test set: **123**
- Of those found in the paper's CUTE tables: **123**

## Preset `filtersqp`

- Our run: **120/123 solved**, cumulative CPU 1.29s
- Status agreement with the paper: **120/123** (97.6%)
- Of the co-solved problems, identical objective-evaluation count: 50

| Problem | Paper (2.2.0) | Ours (2.8.0) | Paper #evals | Our #evals | Our exit |
|---|---|---|---|---|---|
| hs061 | solved | failed | 1 | 2 | Infeasible stationary point |
| hs085 | failed | solved | -- | 8 | Feasible KKT point |
| hs093 | solved | failed | 3 | 4 | Infeasible stationary point |

## Preset `ipopt`

- Our run: **121/123 solved**, cumulative CPU 2.35s
- Status agreement with the paper: **120/123** (97.6%)
- Of the co-solved problems, identical objective-evaluation count: 48

| Problem | Paper (2.2.0) | Ours (2.8.0) | Paper #evals | Our #evals | Our exit |
|---|---|---|---|---|---|
| hs061 | solved | failed | 11 | 25 | Suboptimal point |
| hs085 | failed | solved | -- | 40 | Feasible KKT point |
| hs114 | failed | solved | -- | 20 | Feasible KKT point |

## Verdict

**PASS** — the harness reproduces the published preset behavior up to expected 2.2.0 -> 2.8.0 differences.
