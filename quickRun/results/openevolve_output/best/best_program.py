"""OptiUNO evolution target: the six UNO ingredient options.

Only the dict below evolves. Every value must come from the listed
alternatives (from the UNO 2.8.0 manual / `uno-options.json`); anything else
is rejected by the evaluator. Initialized to the `filtersqp` preset ingredients.
"""

# EVOLVE-BLOCK-START
UNO_CONFIG = {
    # only value available in Uno 2.8.0:
    #   "feasibility_restoration"
    "constraint_relaxation_strategy": "feasibility_restoration",

    # one of: "inequality_constrained" | "interior_point"
    "inequality_handling_method": "inequality_constrained",

    # one of: "exact" | "LBFGS" | "LSR1" | "identity" | "zero"
    "hessian_model": "exact",

    # one of: "primal" | "primal_dual" | "none"
    "inertia_correction_strategy": "none",

    # one of: "TR" (trust region) | "LS" (line search)
    "globalization_mechanism": "TR",

    # one of: "merit_function" | "fletcher_filter_method"
    #       | "waechter_filter_method" | "funnel_method"
    "globalization_strategy": "fletcher_filter_method",
}
# EVOLVE-BLOCK-END
