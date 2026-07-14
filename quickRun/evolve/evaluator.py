"""openEvolve evaluator for OptiUNO.

Loads UNO_CONFIG from the evolved program, sweeps it over the HS test set via
the cached harness, and returns the two objectives plus a scalar fitness:

  reliability     fraction of the 123 problems solved (maximize)
  cum_cpu_time    cumulative CPU seconds over the test set (minimize)
  combined_score  reliability-dominated scalar with CPU time as tiebreak

Every evaluation (cached or not) is appended to results/evolution_history.csv
so the Pareto front can be reconstructed per evolution step.
"""
import csv
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from openevolve.evaluation_result import EvaluationResult  # noqa: E402

from harness.benchmark import evaluate_config  # noqa: E402

HISTORY = ROOT / "results" / "evolution_history.csv"

ALLOWED = {
    "constraint_relaxation_strategy": ["feasibility_restoration"],
    "inequality_handling_method": ["inequality_constrained", "interior_point"],
    "hessian_model": ["exact", "LBFGS", "LSR1", "identity", "zero"],
    "inertia_correction_strategy": ["primal", "primal_dual", "none"],
    "globalization_mechanism": ["TR", "LS"],
    "globalization_strategy": ["merit_function", "fletcher_filter_method",
                               "waechter_filter_method", "funnel_method"],
}

# CPU-time normalization scale (s): presets land at 1-3 s cumulative.
TIME_SCALE = 60.0


def _load_config(program_path: str) -> dict:
    spec = importlib.util.spec_from_file_location("evolved", program_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return dict(mod.UNO_CONFIG)


def _validation_errors(cfg: dict) -> list[str]:
    errs = [f"missing option {k!r}" for k in ALLOWED if k not in cfg]
    errs += [f"unknown option {k!r}" for k in cfg if k not in ALLOWED]
    errs += [
        f"invalid value {cfg[k]!r} for {k!r}; allowed: {ALLOWED[k]}"
        for k in ALLOWED if k in cfg and cfg[k] not in ALLOWED[k]
    ]
    return errs


def _append_history(row: dict) -> None:
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    new = not HISTORY.exists()
    with open(HISTORY, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["timestamp", "config_json", "valid", "reliability",
                        "cum_cpu_time", "combined_score", "n_solved",
                        "status_counts_json"])
        w.writerow([f"{row['timestamp']:.3f}", row["config_json"],
                    row["valid"], f"{row['reliability']:.6f}",
                    f"{row['cum_cpu_time']:.4f}",
                    f"{row['combined_score']:.6f}", row["n_solved"],
                    row["status_counts_json"]])


def combined_score(reliability: float, cum_cpu_time: float) -> float:
    """Reliability dominates; faster cumulative CPU time breaks ties."""
    return reliability + 0.1 * max(0.0, 1.0 - cum_cpu_time / TIME_SCALE)


def evaluate(program_path: str) -> EvaluationResult:
    try:
        cfg = _load_config(program_path)
    except Exception as exc:  # noqa: BLE001 - malformed program proposed by LLM
        return EvaluationResult(
            metrics={"combined_score": 0.0, "reliability": 0.0,
                     "cum_cpu_time": TIME_SCALE},
            artifacts={"error": f"program failed to load: {exc}"},
        )

    errors = _validation_errors(cfg)
    if errors:
        _append_history({
            "timestamp": time.time(), "config_json": json.dumps(cfg, sort_keys=True),
            "valid": 0, "reliability": 0.0, "cum_cpu_time": TIME_SCALE,
            "combined_score": 0.0, "n_solved": 0, "status_counts_json": "{}",
        })
        return EvaluationResult(
            metrics={"combined_score": 0.0, "reliability": 0.0,
                     "cum_cpu_time": TIME_SCALE},
            artifacts={"validation_errors": "; ".join(errors)},
        )

    out = evaluate_config(cfg, label="evolve")
    score = combined_score(out["reliability"], out["cum_cpu_time"])

    _append_history({
        "timestamp": time.time(), "config_json": json.dumps(cfg, sort_keys=True),
        "valid": 1, "reliability": out["reliability"],
        "cum_cpu_time": out["cum_cpu_time"], "combined_score": score,
        "n_solved": out["n_solved"],
        "status_counts_json": json.dumps(out["status_counts"]),
    })

    unsolved = [f"{r['problem']}({r['detail']})" for r in out["per_problem"]
                if r["category"] != "solved"][:15]
    return EvaluationResult(
        metrics={
            "combined_score": score,
            "reliability": out["reliability"],
            "cum_cpu_time": out["cum_cpu_time"],
        },
        artifacts={
            "status_counts": json.dumps(out["status_counts"]),
            "n_silently_rewritten": str(out["n_rewritten"]),
            "unsolved_problems": ", ".join(unsolved) or "none",
        },
    )
