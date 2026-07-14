#!/usr/bin/env python3
"""Render a graph-like figure of the quickRun code structure.

Documentation helper only (not part of the experiment pipeline). Draws the
modules of quickRun/ as nodes grouped by role, with edges showing the data /
call flow. Output: quickRun/docs/architecture.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent / "architecture.png"

# ---- palette (color-blind-safe, consistent light look) ----------------------
C = {
    "input":   ("#e8eef7", "#2f5c9e"),   # (fill, edge/title)
    "prep":    ("#eef3e8", "#4c7a2f"),
    "core":    ("#fdf2e0", "#b5761f"),
    "dep":     ("#f0eef7", "#6a4fa0"),
    "driver":  ("#fce9ea", "#b23a48"),
    "output":  ("#e9f4f4", "#227a7a"),
}
GROUP_TITLE = {
    "input":  "INPUTS",
    "prep":   "PRE-PROCESSING (one-time)",
    "core":   "CORE HARNESS  (harness/)",
    "dep":    "EXTERNAL DEPENDENCY",
    "driver": "DRIVERS  (evolve/ + scripts/)",
    "output": "OUTPUTS  (results/)",
}

fig, ax = plt.subplots(figsize=(19, 11.5))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

nodes = {}   # id -> (cx, cy, w, h)


def box(nid, cx, cy, text, kind, w=17, h=7.5, fs=9.5, bold_first=True):
    fill, edge = C[kind]
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.25,rounding_size=0.9",
        linewidth=1.6, edgecolor=edge, facecolor=fill, zorder=2))
    lines = text.split("\n")
    if bold_first and len(lines) > 1:
        ax.text(cx, cy + h / 2 - 1.6, lines[0], ha="center", va="center",
                fontsize=fs, fontweight="bold", color=edge, zorder=3,
                family="monospace")
        ax.text(cx, cy - 0.6, "\n".join(lines[1:]), ha="center", va="center",
                fontsize=fs - 1.3, color="#333", zorder=3)
    else:
        ax.text(cx, cy, text, ha="center", va="center", fontsize=fs,
                color="#222", zorder=3)
    nodes[nid] = (cx, cy, w, h)


def group_bg(kind, x0, y0, x1, y1):
    fill, edge = C[kind]
    ax.add_patch(FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0,
        boxstyle="round,pad=0.2,rounding_size=1.2",
        linewidth=1.3, edgecolor=edge, facecolor="none",
        linestyle=(0, (4, 3)), alpha=0.55, zorder=1))
    ax.text(x0 + 0.8, y1 - 1.7, GROUP_TITLE[kind], ha="left", va="center",
            fontsize=10, fontweight="bold", color=edge, alpha=0.9, zorder=1)


def edge(a, b, color="#555", style="-", rad=0.0, lw=1.5, side_a=None, side_b=None):
    ax, ay, aw, ah = nodes[a]
    bx, by, bw, bh = nodes[b]

    def anchor(cx, cy, w, h, side, other):
        if side == "r":  return (cx + w / 2, cy)
        if side == "l":  return (cx - w / 2, cy)
        if side == "t":  return (cx, cy + h / 2)
        if side == "b":  return (cx, cy - h / 2)
        # auto: horizontal by default
        return (cx + w / 2, cy) if other[0] > cx else (cx - w / 2, cy)

    pa = anchor(ax, ay, aw, ah, side_a, (bx, by))
    pb = anchor(bx, by, bw, bh, side_b, (ax, ay))
    globals()["ax_"] = None
    arrow = FancyArrowPatch(
        pa, pb, connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>", mutation_scale=13, linewidth=lw,
        color=color, linestyle=style, zorder=2)
    plt.gca().add_patch(arrow)


ax = plt.gca()

# ---- group backgrounds ------------------------------------------------------
group_bg("input",  1,  62, 20, 92)
group_bg("prep",   1,  30, 20, 55)
group_bg("core",   26, 20, 52, 92)
group_bg("dep",    26, 2,  52, 16)
group_bg("driver", 57, 20, 77, 96)
group_bg("output", 81, 6,  99, 96)

# ---- INPUTS -----------------------------------------------------------------
box("mod", 10.5, 82, "models/mod/*.mod\n125 Vanderbei HS", "input", h=8)
box("paper", 10.5, 70, "references/…/\nstatistics_table.tex\n(paper results)", "input", h=9)

# ---- PRE-PROCESSING ---------------------------------------------------------
box("translate", 10.5, 47, "translate_models.py\n.mod → AMPL .nl", "prep", h=8)
box("nl", 10.5, 36, "models/nl/*.nl\n123 problems\n+ MANIFEST.csv", "prep", h=9)

# ---- CORE HARNESS -----------------------------------------------------------
box("runner", 39, 82, "uno_runner.py\nrun_uno(nl, opts)\n1 subprocess call", "core", h=10)
box("classify", 39, 66, "classify.py\nclassify(result)\nsolved/…/rewritten", "core", h=10)
box("bench", 39, 48, "benchmark.py\nevaluate_config()\nsweep + cache", "core", h=10)
box("cache", 39, 32, "harness/cache/\n*.json\n(per-config)", "core", h=8, fs=9)

# ---- EXTERNAL DEP -----------------------------------------------------------
box("uno", 39, 9, "external/uno/bin/uno_ampl\nUNO 2.8.0 (+ lib/ deps/)", "dep", h=7, fs=9)

# ---- DRIVERS ----------------------------------------------------------------
box("initprog", 67, 90, "evolve/initial_program.py\nUNO_CONFIG (6 opts)", "driver", h=7, fs=8.5)
box("evaluator", 67, 80, "evolve/evaluator.py\nvalidate → score", "driver", h=7, fs=8.5)
box("cfgyaml", 67, 70, "evolve/config.yaml\nopenEvolve + LLM", "driver", h=7, fs=8.5)
box("runevo", 67, 59, "scripts/run_evolution.py\nbaselines + openevolve-run", "driver", h=7, fs=8.5)
box("validate", 67, 47, "scripts/validate_presets.py", "driver", h=6, fs=8.5, bold_first=False)
box("variance", 67, 38, "scripts/variance_runs.py", "driver", h=6, fs=8.5, bold_first=False)
box("plot", 67, 29, "scripts/plot_pareto.py", "driver", h=6, fs=8.5, bold_first=False)

# ---- OUTPUTS ----------------------------------------------------------------
box("evalcsv", 90, 84, "evaluations.csv", "output", h=5.5, fs=9, bold_first=False)
box("evohist", 90, 74, "evolution_history.csv", "output", h=5.5, fs=9, bold_first=False)
box("evoout", 90, 64, "openevolve_output/", "output", h=5.5, fs=9, bold_first=False)
box("presetval", 90, 50, "preset_validation.md", "output", h=5.5, fs=9, bold_first=False)
box("varout", 90, 40, "variance.{md,json}", "output", h=5.5, fs=9, bold_first=False)
box("pareto", 90, 29, "pareto_*.png\nfront_configs.json", "output", h=7, fs=9)

# ---- EDGES ------------------------------------------------------------------
BLUE, ORANGE, RED, GREY = "#2f5c9e", "#b5761f", "#b23a48", "#888"

# preprocessing chain
edge("mod", "translate", color=BLUE, side_a="b", side_b="t")
edge("translate", "nl", color="#4c7a2f", side_a="b", side_b="t")

# harness internal + inputs
edge("nl", "runner", color=BLUE)                      # runner reads .nl
edge("uno", "runner", color="#6a4fa0", side_a="t", side_b="b", rad=-0.1)  # subprocess
edge("runner", "classify", color=ORANGE, side_a="b", side_b="t")
edge("bench", "runner", color=ORANGE, rad=0.28, side_a="t", side_b="l")   # bench calls run_uno
edge("bench", "classify", color=ORANGE, rad=0.15, side_a="t", side_b="b")
edge("bench", "cache", color=ORANGE, style="--", side_a="b", side_b="t")

# drivers -> harness
edge("evaluator", "bench", color=RED, rad=0.05, side_a="l", side_b="r")
edge("initprog", "evaluator", color=RED, side_a="b", side_b="t")
edge("cfgyaml", "runevo", color=RED, side_a="b", side_b="t")
edge("runevo", "evaluator", color=RED, rad=0.2, side_a="t", side_b="r")
edge("runevo", "bench", color=RED, rad=-0.25, side_a="l", side_b="r", style="--")
edge("validate", "bench", color=RED, rad=-0.1, side_a="l", side_b="r")
edge("variance", "bench", color=RED, rad=-0.18, side_a="l", side_b="r")
edge("paper", "validate", color=BLUE, rad=-0.3, side_a="r", side_b="l", style="--")

# drivers -> outputs
edge("bench", "evalcsv", color=GREY, style="--", rad=-0.15, side_a="r", side_b="l")
edge("evaluator", "evohist", color=GREY, style="--", rad=0.2, side_a="r", side_b="l")
edge("runevo", "evoout", color=GREY, style="--", rad=-0.1, side_a="r", side_b="l")
edge("validate", "presetval", color=GREY, style="--", side_a="r", side_b="l")
edge("variance", "varout", color=GREY, style="--", side_a="r", side_b="l")
edge("plot", "pareto", color=GREY, style="--", side_a="r", side_b="l")
edge("evohist", "plot", color=GREY, style="--", rad=0.35, side_a="b", side_b="t")
edge("varout", "plot", color=GREY, style="--", rad=-0.2, side_a="b", side_b="t")

# ---- title + legend ---------------------------------------------------------
ax.text(50, 98.5, "OptiUNO / quickRun — code structure & data flow",
        ha="center", va="center", fontsize=16, fontweight="bold", color="#222")

from matplotlib.lines import Line2D
legend = [
    Line2D([0], [0], color=BLUE,   lw=2, label="problem data"),
    Line2D([0], [0], color=ORANGE, lw=2, label="solve / classify call"),
    Line2D([0], [0], color=RED,    lw=2, label="driver → harness call"),
    Line2D([0], [0], color=GREY,   lw=2, ls="--", label="writes / reads file"),
]
ax.legend(handles=legend, loc="lower left", fontsize=9, frameon=True,
          ncol=1, bbox_to_anchor=(0.005, 0.005))

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"wrote {OUT}")
