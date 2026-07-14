#!/usr/bin/env python3
"""Drive the openEvolve search over UNO's six ingredient options.

Usage (from the project root, inside the venv or via ./.venv/bin/python):
    scripts/run_evolution.py [--model NAME] [--iterations N] [--smoke] [--api]

Model precedence: --model > $OPTIUNO_EVOLVE_MODEL > default.
Two LLM backends:
  * default   the Claude Code CLI's OAuth session (subscription, no API key);
              default model "claude-sonnet-4-5" (the bare "sonnet" alias now
              resolves to claude-sonnet-5, which many subscriptions cannot
              serve). A set-but-invalid ANTHROPIC_API_KEY is stripped from the
              child environment, since the CLI would give it precedence over
              the login.
  * --api     the Anthropic API (requires ANTHROPIC_API_KEY); default model
              claude-sonnet-5.

Baselines (both presets, expressed as explicit ingredient configs) are
evaluated before evolution starts so every plot has its reference points.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from harness.benchmark import evaluate_config  # noqa: E402

DEFAULT_MODEL = "claude-sonnet-5"

# The presets' six-ingredient equivalents (from uno-options.json / UNO banners)
PRESET_INGREDIENTS = {
    "filtersqp": {
        "constraint_relaxation_strategy": "feasibility_restoration",
        "inequality_handling_method": "inequality_constrained",
        "hessian_model": "exact",
        "inertia_correction_strategy": "none",
        "globalization_mechanism": "TR",
        "globalization_strategy": "fletcher_filter_method",
    },
    "ipopt": {
        "constraint_relaxation_strategy": "feasibility_restoration",
        "inequality_handling_method": "interior_point",
        "hessian_model": "exact",
        "inertia_correction_strategy": "primal_dual",
        "globalization_mechanism": "LS",
        "globalization_strategy": "waechter_filter_method",
    },
}


def _find_openevolve_run() -> str:
    """Locate the openevolve-run entry point.

    Prefer the one installed alongside the interpreter running this script (so
    `conda run -n <env> python scripts/run_evolution.py` uses that env's
    openEvolve), then a project-local .venv, then PATH.
    """
    candidates = [
        Path(sys.executable).parent / "openevolve-run",   # same env as this Python
        ROOT / ".venv" / "bin" / "openevolve-run",         # project-local venv
    ]
    for cand in candidates:
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    on_path = shutil.which("openevolve-run")
    if on_path:
        return on_path
    sys.exit(
        "Could not find 'openevolve-run'. Install openEvolve in the environment "
        "you run this script with (e.g. `pip install openevolve` in your conda "
        "env), then run:\n"
        "  conda run -n <env> python scripts/run_evolution.py ...")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("OPTIUNO_EVOLVE_MODEL"))
    ap.add_argument("--iterations", type=int, default=None,
                    help="override max_iterations from the evolve config")
    ap.add_argument("--smoke", action="store_true",
                    help="5-iteration end-to-end smoke test")
    ap.add_argument("--api", action="store_true",
                    help="use the Anthropic API (needs ANTHROPIC_API_KEY) "
                         "instead of the default Claude Code CLI subscription")
    ap.add_argument("--claude-code", action="store_true",
                    help="(deprecated no-op) the Claude Code CLI is now the "
                         "default backend")
    args = ap.parse_args()

    env = dict(os.environ)
    if args.api:
        config_file = ROOT / "evolve" / "config.yaml"
        model = args.model or DEFAULT_MODEL
        if not env.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY is not set - export it (or drop --api "
                     "to run on the Claude Code CLI subscription).")
    else:
        config_file = ROOT / "evolve" / "config-claude-code.yaml"
        model = args.model or "claude-sonnet-4-5"
        # the CLI prefers ANTHROPIC_API_KEY over the OAuth login; drop it so
        # the subscription session is used
        env.pop("ANTHROPIC_API_KEY", None)

    print(f"LLM backend: {'Anthropic API' if args.api else 'claude-code CLI (subscription)'}"
          f" | model: {model}")
    print("Evaluating baselines (presets as explicit ingredient configs) ...")
    for name, ingredients in PRESET_INGREDIENTS.items():
        out = evaluate_config(ingredients, label=f"baseline-{name}")
        print(f"  {name:10s} reliability={out['reliability']:.3f} "
              f"cumCPU={out['cum_cpu_time']:.2f}s")

    # Substitute the model into an effective config instead of using
    # --primary-model: the CLI override calls rebuild_models(), which drops
    # per-model fields (e.g. max_budget_usd -> None, which the claude CLI
    # rejects as a literal "None").
    import yaml
    cfg = yaml.safe_load(config_file.read_text())
    cfg["llm"]["models"][0]["name"] = model
    effective = ROOT / "results" / "openevolve_effective_config.yaml"
    effective.parent.mkdir(parents=True, exist_ok=True)
    effective.write_text(yaml.safe_dump(cfg, sort_keys=False))

    cmd = [
        _find_openevolve_run(),
        str(ROOT / "evolve" / "initial_program.py"),
        str(ROOT / "evolve" / "evaluator.py"),
        "--config", str(effective),
        "--output", str(ROOT / "results" / "openevolve_output"),
    ]
    iters = 5 if args.smoke else args.iterations
    if iters is not None:
        cmd += ["--iterations", str(iters)]

    print("$", " ".join(cmd))
    raise SystemExit(subprocess.run(cmd, cwd=ROOT, env=env).returncode)


if __name__ == "__main__":
    main()
