#!/usr/bin/env python3
"""Drive the openEvolve search over UNO's six ingredient options.

Usage (from the project root, inside the venv or via ./.venv/bin/python):
    scripts/run_evolution.py [--model NAME] [--iterations N] [--smoke]
                             [--claude-code]

Model precedence: --model > $OPTIUNO_EVOLVE_MODEL > default.
Two LLM backends:
  * default        Anthropic API (requires ANTHROPIC_API_KEY);
                   default model claude-sonnet-5
  * --claude-code  the Claude Code CLI's OAuth session (subscription, no
                   API key); default model "sonnet". A set-but-invalid
                   ANTHROPIC_API_KEY is stripped from the child environment,
                   since the CLI would give it precedence over the login.

Baselines (both presets, expressed as explicit ingredient configs) are
evaluated before evolution starts so every plot has its reference points.
"""
import argparse
import os
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("OPTIUNO_EVOLVE_MODEL"))
    ap.add_argument("--iterations", type=int, default=None,
                    help="override max_iterations from the evolve config")
    ap.add_argument("--smoke", action="store_true",
                    help="5-iteration end-to-end smoke test")
    ap.add_argument("--claude-code", action="store_true",
                    help="use the Claude Code CLI (subscription) instead of "
                         "the Anthropic API")
    args = ap.parse_args()

    env = dict(os.environ)
    if args.claude_code:
        config_file = ROOT / "evolve" / "config-claude-code.yaml"
        model = args.model or "sonnet"
        # the CLI prefers ANTHROPIC_API_KEY over the OAuth login; drop it so
        # the subscription session is used
        env.pop("ANTHROPIC_API_KEY", None)
    else:
        config_file = ROOT / "evolve" / "config.yaml"
        model = args.model or DEFAULT_MODEL
        if not env.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY is not set - export it (or use "
                     "--claude-code to run on the CLI subscription).")

    print(f"LLM backend: {'claude-code CLI (subscription)' if args.claude_code else 'Anthropic API'}"
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
        str(ROOT / ".venv" / "bin" / "openevolve-run"),
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
