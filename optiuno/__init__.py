"""OptiUNO — search for optimal run-time configurations of the UNO solver.

Re-exports are lazy (PEP 562) so that `python -m optiuno.uno_runner` does not
import the submodule twice (which would emit a runpy RuntimeWarning), while
`from optiuno import run_uno` still works.
"""

# Map each lazily re-exported name to the submodule that defines it.
_LAZY = {
    "run_uno": "uno_runner",
    "UnoResult": "uno_runner",
    "DEFAULT_TIME_LIMIT": "uno_runner",
    "select_uno_bin": "utils",
    "bundled_uno_bin": "utils",
    "evaluate": "objective",
    "evaluate_detailed": "objective",
    "load_problem_set": "objective",
    "make_objective": "objective",
}

__all__ = list(_LAZY)


def __getattr__(name):
    module = _LAZY.get(name)
    if module is not None:
        import importlib
        return getattr(importlib.import_module(f".{module}", __name__), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
