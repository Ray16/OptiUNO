"""Classify a uno_runner result: solved / unsolved / invalid / crashed / timeout,
plus detection of silently-rewritten configurations.

UNO prints the *actually composed* method as a banner, e.g.
  "TR Fletcher-filter restoration inequality-constrained SQP method
   with exact Hessian and no inertia correction"
Comparing that banner against the requested ingredients catches the dangerous
case where a run succeeds but tested a different configuration (LOGBOOK
2026-07-13: invalid / silently-rewritten / genuinely-failed are three cases).
"""
from __future__ import annotations

SOLVED = "solved"
UNSOLVED = "unsolved"          # ran fine, terminated at a non-KKT exit
TIMEOUT = "timeout"
INVALID = "invalid"            # UNO rejected the option combination
CRASH = "crash"                # process died without a parseable result


def _banner_ingredients(banner: str) -> dict:
    """Parse UNO's composed-method banner back into ingredient values."""
    b = banner or ""
    out = {}
    if b.startswith("TR "):
        out["globalization_mechanism"] = "TR"
    elif b.startswith("LS "):
        out["globalization_mechanism"] = "LS"

    if "Fletcher-filter" in b:
        out["globalization_strategy"] = "fletcher_filter_method"
    elif "Waechter-filter" in b:
        out["globalization_strategy"] = "waechter_filter_method"
    elif "funnel" in b.lower():
        out["globalization_strategy"] = "funnel_method"
    elif "merit" in b.lower():
        out["globalization_strategy"] = "merit_function"

    if "interior-point" in b:
        out["inequality_handling_method"] = "interior_point"
    elif "inequality-constrained" in b:
        out["inequality_handling_method"] = "inequality_constrained"

    if "exact Hessian" in b:
        out["hessian_model"] = "exact"
    elif "L-BFGS" in b or "LBFGS" in b:
        out["hessian_model"] = "LBFGS"
    elif "SR1" in b:
        out["hessian_model"] = "LSR1"
    elif "identity Hessian" in b:
        out["hessian_model"] = "identity"
    elif "zero Hessian" in b:
        out["hessian_model"] = "zero"

    if "no inertia correction" in b:
        out["inertia_correction_strategy"] = "none"
    elif "primal-dual inertia" in b:
        out["inertia_correction_strategy"] = "primal_dual"
    elif "primal inertia" in b:
        out["inertia_correction_strategy"] = "primal"

    if "restoration" in b:
        out["constraint_relaxation_strategy"] = "feasibility_restoration"
    return out


def rewritten_ingredients(requested: dict, banner: str) -> list[str]:
    """Ingredient names whose banner value differs from what was requested."""
    actual = _banner_ingredients(banner or "")
    return sorted(
        k for k, v in requested.items()
        if k in actual and str(actual[k]) != str(v)
    )


def classify(result: dict) -> dict:
    """Return {category, rewritten, detail} for one uno_runner result."""
    banner = result.get("banner") or ""
    opt_status = result.get("optimization_status") or ""
    sol_status = result.get("solution_status") or ""

    if banner == "strategy combination not initialized":
        category = INVALID
    elif result.get("timed_out"):
        category = TIMEOUT
    elif opt_status == "" and sol_status == "":
        category = CRASH
    elif "time limit" in opt_status.lower():
        category = TIMEOUT
    elif opt_status == "Success" and sol_status == "Feasible KKT point":
        category = SOLVED
    else:
        category = UNSOLVED

    rewritten = []
    if category in (SOLVED, UNSOLVED, TIMEOUT) and banner:
        rewritten = rewritten_ingredients(result.get("options", {}), banner)

    return {
        "category": category,
        "rewritten": rewritten,
        "detail": sol_status or opt_status or ("timeout" if category == TIMEOUT else "no output"),
    }
