# UNO run-time options

Complete list of UNO's run-time options, transcribed from the [UNO manual](https://unosolver.readthedocs.io/en/latest/options/) (retrieved 2026-07-13). The machine-readable companion is [`uno-options.json`](uno-options.json) — keep the two in sync.

**90 options in total**, of which **17 have a finite value set** (categorical or small integer enum). Those 17 define the discrete search space for OptiUNO; the remaining 73 are continuous, integer, boolean, or string hyperparameters.

Legend: a `—` in the *Values* column means the option is not categorical (any value of the given type is accepted).

---

## 1. Ingredients — the algorithmic building blocks

These are the primary **optimization variables** for OptiUNO. The manual lists no defaults for them: they are set by the `preset` option (default `auto`), or must be given explicitly.

| Option | Values | Default | Description |
|---|---|---|---|
| `constraint_relaxation_strategy` | `feasibility_restoration` | *(from preset)* | How the subproblem constraints are relaxed to guarantee a well-defined, feasible subproblem |
| `inequality_handling_method` | `inequality_constrained`, `interior_point` | *(from preset)* | How the combinatorics induced by inequality constraints are handled |
| `hessian_model` | `exact`, `LBFGS`, `LSR1`, `identity`, `zero` | *(from preset)* | Approximation of the Lagrangian Hessian |
| `inertia_correction_strategy` | `primal`, `primal_dual`, `none` | *(from preset)* | How the inertia of the Lagrangian Hessian / KKT matrix is corrected |
| `globalization_mechanism` | `TR`, `LS` | *(from preset)* | Trust region or line search: controls step length and the recourse action when a trial iterate is rejected |
| `globalization_strategy` | `merit_function`, `fletcher_filter_method`, `waechter_filter_method`, `funnel_method` | *(from preset)* | Decides whether a trial iterate makes sufficient progress, and accepts or rejects it |

> **Discrepancy with the paper.** UNO.pdf (§4.2) describes **two** constraint relaxation strategies — ℓ1 relaxation and feasibility restoration — but the current manual exposes only `feasibility_restoration` as a value. Either ℓ1 relaxation is not user-selectable, or the docs are behind the code. Worth confirming against the binary before assuming the search space includes it.

## 2. Subproblem solver

Availability is **build-dependent** — probe the actual binary rather than assuming.

| Option | Values | Default | Description |
|---|---|---|---|
| `QP_solver` | `BQPD`, `HiGHS` *(if available)* | auto | Quadratic programming subproblem solver |
| `LP_solver` | `BQPD`, `HiGHS` *(if available)* | auto | Linear programming subproblem solver |
| `linear_solver` | `MA57`, `MA27`, `MA86`, `MUMPS`, `SSIDS` *(if available)* | auto | Direct solver for sparse symmetric indefinite linear systems |
| `libhsl_path` | — *(string)* | `""` | Name/path of the HSL shared library to `dlopen` for MA27/MA57/MA86. Only used when UNO is built with `-DHSL_RUNTIME_LOADING=ON`. An empty value resolves at runtime to the platform default `libhsl.{so,dylib,dll}` |

*"If not provided, the solver is chosen automatically from the available solvers (if any)."*

## 3. Main options

| Option | Values | Default | Description |
|---|---|---|---|
| `preset` | `filtersqp`, `ipopt`, `auto` | `auto` | UNO preset (see §14) |
| `logger` | `SILENT`, `DISCRETE`, `WARNING`, `INFO`, `DEBUG`, `DEBUG2`, `DEBUG3` | `INFO` | Verbosity level of the logger |
| `progress_norm` | `L1`, `L2`, `INF` | `L1` | Norm used for the progress measures |
| `residual_norm` | `L1`, `L2`, `INF` | `INF` | Norm used for the residuals |
| `residual_scaling_threshold` | — *(double)* | `100.0` | Scaling factor in stationarity and complementarity residuals |
| `protect_actual_reduction_against_roundoff` | `true`, `false` | `false` | Whether actual reduction accounts for roundoff |
| `protected_actual_reduction_macheps_coefficient` | — *(double)* | `10` | Coefficient of the machine epsilon in protected actual reduction |
| `print_subproblem` | `true`, `false` | `false` | Whether the subproblem prints in DEBUG mode |
| `write_solution_to_file` | `true`, `false` | `false` | Whether the solution is printed to a file (used by AMPL and CUTEst) |

## 4. Termination

| Option | Values | Default | Description |
|---|---|---|---|
| `primal_tolerance` | — *(double)* | `1e-8` | Tolerance on constraint violation |
| `dual_tolerance` | — *(double)* | `1e-8` | Tolerance on stationarity and complementarity |
| `loose_primal_tolerance` | — *(double)* | `1e-6` | Loose tolerance on constraint violation |
| `loose_dual_tolerance` | — *(double)* | `1e-6` | Loose tolerance on stationarity and complementarity |
| `loose_tolerance_iteration_threshold` | — *(integer)* | `15` | Number of iterations for the loose tolerance to apply |
| `max_iterations` | — *(integer)* | `2000` | Maximum number of outer iterations |
| `time_limit` | — *(double)* | `infinity` | Time limit |
| `print_solution` | `true`, `false` | `false` | Whether the primal-dual solution is printed |
| `unbounded_objective_threshold` | — *(double)* | `-1e20` | Objective threshold under which the problem is declared unbounded |

## 5. Globalization strategy (Armijo condition)

| Option | Values | Default | Description |
|---|---|---|---|
| `armijo_decrease_fraction` | — *(double)* | `1e-4` | Fraction of predicted reduction in the Armijo condition |
| `armijo_tolerance` | — *(double)* | `1e-9` | Minimum value of predicted reduction in the Armijo condition, 0 otherwise |

## 6. Switching method

| Option | Values | Default | Description |
|---|---|---|---|
| `switching_delta` | — *(double)* | `0.999` | Fraction of constraint violation in the switching condition |
| `switching_infeasibility_exponent` | — *(double)* | `2` | Exponent of constraint violation in the switching condition |

## 7. Merit function

Applies when `globalization_strategy = merit_function`.

| Option | Values | Default | Description |
|---|---|---|---|
| `sufficient_infeasibility_decrease_ratio` | — *(double)* | `0.9` | Sufficient infeasibility decrease ratio |

## 8. Filter method

Applies when `globalization_strategy = fletcher_filter_method` or `waechter_filter_method`.

| Option | Values | Default | Description |
|---|---|---|---|
| `filter_type` | `standard` | `standard` | Type of the filter data structure |
| `filter_beta` | — *(double)* | `0.999` | Fraction in the infeasibility sufficient reduction condition |
| `filter_gamma` | — *(double)* | `0.001` | Slope in the objective sufficient reduction condition |
| `filter_ubd` | — *(double)* | `1e2` | Minimum value for the initial upper bound on infeasibility |
| `filter_fact` | — *(double)* | `1.25` | Multiple of initial infeasibility for the upper bound on infeasibility |
| `filter_capacity` | — *(integer)* | `50` | Maximum number of filter entries |
| `filter_sufficient_infeasibility_decrease_factor` | — *(double)* | `0.9` | Infeasibility decrease factor in the sufficient decrease condition |

## 9. Funnel

Applies when `globalization_strategy = funnel_method`.

| Option | Values | Default | Description |
|---|---|---|---|
| `funnel_kappa` | — *(double)* | `0.5` | Convex combination coefficient in the funnel update rule |
| `funnel_beta` | — *(double)* | `0.9999` | Fraction in the infeasibility sufficient reduction condition |
| `funnel_gamma` | — *(double)* | `0.001` | Slope in the objective sufficient reduction condition |
| `funnel_ubd` | — *(double)* | `1.0` | Minimum value for the initial upper bound on infeasibility |
| `funnel_fact` | — *(double)* | `1.5` | Multiple of initial infeasibility for the upper bound on infeasibility |
| `funnel_update_strategy` | `1`, `2`, `3` | `1` | Rule for the funnel update |
| `funnel_require_acceptance_wrt_current_iterate` | `true`, `false` | `false` | Whether the trial iterate should improve upon the current iterate |

## 10. Line search

Applies when `globalization_mechanism = LS`.

| Option | Values | Default | Description |
|---|---|---|---|
| `LS_backtracking_ratio` | — *(double)* | `0.5` | Decrease ratio of the step length for the backtracking line search |
| `LS_min_step_length` | — *(double)* | `1e-12` | Minimum acceptable step length before failure is reported |
| `LS_scale_duals_with_step_length` | `true`, `false` | `true` | Whether the Lagrange multipliers are scaled with the step length |

## 11. Trust region

Applies when `globalization_mechanism = TR`.

| Option | Values | Default | Description |
|---|---|---|---|
| `TR_radius` | — *(double)* | `10.0` | Initial value of the radius |
| `TR_increase_factor` | — *(double)* | `2` | Increase factor of the radius for successful iterations |
| `TR_decrease_factor` | — *(double)* | `2` | Decrease factor of the radius for unsuccessful iterations |
| `TR_aggressive_decrease_factor` | — *(double)* | `4` | Decrease factor of the radius when errors occur |
| `TR_activity_tolerance` | — *(double)* | `1e-6` | Tolerance with which the trust-region constraint is considered active |
| `TR_min_radius` | — *(double)* | `1e-12` | Minimum radius acceptable before failure is reported |
| `TR_radius_reset_threshold` | — *(double)* | `1e-4` | Smallest value to which the radius is reset at the beginning of an iteration |

## 12. Inertia correction

| Option | Values | Default | Description |
|---|---|---|---|
| `regularization_failure_threshold` | — *(double)* | `1e20` | Threshold for the primal inertia correction coefficient above which failure occurs |
| `primal_regularization_initial_factor` | — *(double)* | `1e-4` | Initial value of the primal inertia correction coefficient |
| `regularization_increase_factor` | — *(double)* | `2` | Increase factor for the primal inertia correction coefficient |
| `dual_regularization_fraction` | — *(double)* | `1e-8` | Fraction of the dual inertia correction parameter |
| `primal_regularization_lb` | — *(double)* | `1e-20` | Minimum value of the primal inertia correction coefficient upon decrease |
| `primal_regularization_decrease_factor` | — *(double)* | `3.0` | Decrease factor for the primal inertia correction coefficient |
| `primal_regularization_fast_increase_factor` | — *(double)* | `100.0` | Fast increase factor for the primal inertia correction coefficient |
| `primal_regularization_slow_increase_factor` | — *(double)* | `8.0` | Slow increase factor for the primal inertia correction coefficient |
| `threshold_unsuccessful_attempts` | — *(integer)* | `8` | Number of unsuccessful attempts until inertia correction becomes aggressive |

## 13. Quasi-Newton

Applies when `hessian_model = LBFGS` or `LSR1`.

| Option | Values | Default | Description |
|---|---|---|---|
| `quasi_newton_memory_size` | — *(integer)* | `6` | Size of the quasi-Newton limited memory |
| `quasi_newton_delta_lower_bound` | — *(double)* | `1e-8` | Lower bound on delta in quasi-Newton approximations |
| `quasi_newton_delta_upper_bound` | — *(double)* | `1e8` | Upper bound on delta in quasi-Newton approximations |
| `LBFGS_max_skips_before_reset` | — *(integer)* | `2` | Number of consecutive skips before the limited memory is reset |
| `LSR1_pivot_max_magnitude` | — *(double)* | `1e-7` | Maximum magnitude of allowed pivots in L-SR1 |

## 14. Feasibility restoration

Applies when `constraint_relaxation_strategy = feasibility_restoration`.

| Option | Values | Default | Description |
|---|---|---|---|
| `switch_to_optimality_requires_linearized_feasibility` | `true`, `false` | `true` | Whether the switch to the optimality phase requires linearized constraint consistency |
| `l1_constraint_violation_coefficient` | — *(double)* | `1` | Coefficient of the constraint violation in the ℓ1-relaxed problem |

## 15. Barrier subproblem

Applies when `inequality_handling_method = interior_point`.

| Option | Values | Default | Description |
|---|---|---|---|
| `barrier_function` | `log` | `log` | Type of the barrier function |
| `barrier_initial_parameter` | — *(double)* | `0.1` | Initial value of the barrier parameter |
| `barrier_default_multiplier` | — *(double)* | `1` | Initial value of the bound multipliers |
| `barrier_tau_min` | — *(double)* | `0.99` | Coefficient of the fraction-to-boundary rule |
| `barrier_k_sigma` | — *(double)* | `1e10` | Safeguard parameter for rescaling the bound multipliers |
| `barrier_k_mu` | — *(double)* | `0.2` | Coefficient for the multiplicative update of the barrier parameter |
| `barrier_theta_mu` | — *(double)* | `1.5` | Coefficient for the geometric update of the barrier parameter |
| `barrier_k_epsilon` | — *(double)* | `10` | Scaling factor of the barrier parameter in the update rule |
| `barrier_update_fraction` | — *(double)* | `10` | Fraction in the barrier update rule |
| `barrier_regularization_exponent` | — *(double)* | `0.25` | Exponent of the barrier parameter in the dual inertia correction parameter |
| `barrier_small_direction_factor` | — *(double)* | `10.0` | Multiple of the machine epsilon in the small step condition |
| `barrier_push_variable_to_interior_k1` | — *(double)* | `1e-2` | Coefficient for the perturbation of the initial bounds |
| `barrier_push_variable_to_interior_k2` | — *(double)* | `1e-2` | Coefficient for the perturbation of the initial bounds |
| `barrier_damping_factor` | — *(double)* | `1e-5` | Damping coefficient for single bounds |
| `barrier_small_infeasibility_factor` | — *(double)* | `1e-4` | Factor in the small infeasibility test |
| `least_square_multiplier_max_norm` | — *(double)* | `1e3` | Maximum accepted norm of the least-square multipliers |

## 16. BQPD

| Option | Values | Default | Description |
|---|---|---|---|
| `BQPD_kmax_heuristic` | `filtersqp`, `minotaur` | `filtersqp` | Heuristic used to pick the upper bound on the nullspace size (`kmax`) |

---

## Presets — the baselines to beat

From the [presets page](https://unosolver.readthedocs.io/en/latest/presets/). The `auto` preset (the default) picks `ipopt` if *2000 ≤ n + m* **or** *50000 ≤ nnz(∇c) + nnz(∇²L)*; otherwise `filtersqp`.

| Option | `filtersqp` | `ipopt` |
|---|---|---|
| `constraint_relaxation_strategy` | `feasibility_restoration` | `feasibility_restoration` |
| `inequality_handling_method` | `inequality_constrained` | `interior_point` |
| `hessian_model` | `exact` | `exact` |
| `inertia_correction_strategy` | `none` | `primal_dual` |
| `globalization_mechanism` | `TR` | `LS` |
| `globalization_strategy` | `fletcher_filter_method` | `waechter_filter_method` |
| `filter_type` | `standard` | `standard` |
| `barrier_function` | — | `log` |
| `progress_norm` | `L1` | `L1` |
| `residual_norm` | `L2` | `INF` |
| `primal_tolerance` | `1e-6` | `1e-8` |
| `dual_tolerance` | `1e-6` | `1e-8` |
| `loose_primal_tolerance` | — | `1e-6` |
| `loose_dual_tolerance` | — | `1e-6` |
| `loose_tolerance_iteration_threshold` | — | `15` |
| `l1_constraint_violation_coefficient` | `1` | `1000` |
| `switch_to_optimality_requires_linearized_feasibility` | `true` | `false` |
| `protect_actual_reduction_against_roundoff` | `false` | `true` |
| `TR_radius` | `10` | — |
| `filter_beta` | — | `0.99999` |
| `filter_gamma` | — | `1e-8` |
| `filter_ubd` | — | `1e4` |
| `filter_fact` | — | `1e4` |
| `switching_delta` | — | `1` |
| `filter_switching_infeasibility_exponent` | — | `1.1` |
| `armijo_decrease_fraction` | — | `1e-8` |
| `LS_backtracking_ratio` | — | `0.5` |
| `LS_min_step_length` | — | `5e-7` |
| `LS_scale_duals_with_step_length` | — | `true` |
| `barrier_tau_min` | — | `0.99` |
| `barrier_damping_factor` | — | `1e-5` |

> **Naming inconsistency.** The presets page sets `filter_switching_infeasibility_exponent`, but the options page calls this option `switching_infeasibility_exponent`. Verify which name the binary accepts before scripting either.

---

## Notes for the OptiUNO search

**Size of the ingredient space.** Taking the Cartesian product of the six ingredient options as documented gives
1 × 2 × 5 × 3 × 2 × 4 = **240** combinations. UNO prohibits `interior_point` + `TR` (UNO.pdf §5.2), which removes 1 × 1 × 5 × 3 × 1 × 4 = 60, leaving **180** nominally-legal combinations — in the same ballpark as the "at least 186" quoted in the README. *This is a derived count, not a figure from the manual; treat it as a sanity check, not ground truth.* Multiplying by the solver choices (`QP_solver`, `LP_solver`, `linear_solver`) and the norms (`progress_norm`, `residual_norm`) inflates it substantially.

**Three failure modes, not two.** A harness must distinguish:
1. **Invalid** — rejected outright (e.g. `interior_point` + `TR`).
2. **Silently rewritten** — UNO overrides your choice and runs something else (UNO.pdf §5.3.5): the subproblem solver is swapped for an LP solver when the subproblem has no curvature; an unconstrained reformulation forces `NoRelaxation` + `l1MeritFunction` + `BoxLPSolver`; and `hessian_model = exact` degrades to `zero` (with a warning) when the modeler supplies no Hessian. **This is the dangerous case** — the run succeeds and looks like a valid data point for a configuration that was never actually tested.
3. **Genuinely failed** — a legal configuration that does not converge on the instance.

**Termination is not binary.** UNO.pdf §5.3.7 defines several distinct exits (feasible KKT point, feasible FJ point, infeasible stationary point, trust-region radius near machine epsilon, loose-tolerance fallback after ~15 iterations). Record the exit status, not just success/failure — the choice of which exits count as "solved" materially changes the objective.
