#!/usr/bin/env python3
"""Validate the python<->UNO harness: run both presets on the HS test set and
compare per-problem outcomes against the published results of
arXiv:2406.13454 (Vanaret & Leyffer), Tables `statistics_table.tex`.

The paper benchmarked Uno 2.2.0; we run the v2.8.0 binaries, so evaluation
counts may differ — the acceptance gate is solved/failed agreement, with every
discrepancy listed in results/preset_validation.md.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from harness.benchmark import evaluate_config, test_problems  # noqa: E402

TEX = ROOT / "references" / "arxiv-2406.13454" / "sections" / "statistics_table.tex"
OUT = ROOT / "results" / "preset_validation.md"

ROW_RE = re.compile(r"^\s*([A-Za-z0-9_\-]+)\s*&(.+)\\\\\s*$")


def parse_paper_tables() -> dict:
    """problem -> {'filtersqp': evals|None, 'ipopt': evals|None} (None = failure)."""
    rows = {}
    for line in TEX.read_text().splitlines():
        m = ROW_RE.match(line)
        if not m or m.group(1) in ("Problem",):
            continue
        cells = [c.strip() for c in m.group(2).split("&")]
        if len(cells) < 2:
            continue

        def val(cell: str):
            cell = cell.replace("\\textbf{", "").replace("}", "").strip()
            if cell in ("--", "-", ""):
                return None
            try:
                return int(cell)
            except ValueError:
                return None

        rows[m.group(1)] = {"filtersqp": val(cells[0]), "ipopt": val(cells[1])}
    return rows


def main() -> None:
    paper = parse_paper_tables()
    ours_problems = [p.stem for p in test_problems()]
    common = [p for p in ours_problems if p in paper]
    print(f"paper table rows: {len(paper)} | our test set: {len(ours_problems)} "
          f"| overlap: {len(common)}")

    lines = [
        "# Preset validation against arXiv:2406.13454 (Uno paper)",
        "",
        "Paper benchmark: Uno **2.2.0**; this harness: Uno **2.8.0** "
        "(release binaries). Agreement is judged on solved/failed status; "
        "objective-evaluation counts are reported for reference and may "
        "legitimately differ across versions.",
        "",
        "**Caveat on model provenance:** the paper used the Neumaier/COCONUT "
        "AMPL translations of CUTE (see footnote in its Sec. 7), while this "
        "project uses Vanderbei's translations. Formulation or starting-point "
        "differences between the two translations can explain residual "
        "per-problem discrepancies beyond the solver-version gap.",
        "",
        f"- Problems in our HS test set: **{len(ours_problems)}**",
        f"- Of those found in the paper's CUTE tables: **{len(common)}**",
        "",
    ]

    overall_ok = True
    for preset in ("filtersqp", "ipopt"):
        res = evaluate_config({"preset": preset}, label=f"preset-{preset}")
        by_problem = {r["problem"]: r for r in res["per_problem"]}

        agree, disagree, eval_match = 0, [], 0
        for prob in common:
            p_solved = paper[prob][preset] is not None
            o = by_problem[prob]
            o_solved = o["category"] == "solved"
            if p_solved == o_solved:
                agree += 1
                if p_solved and o["objective_evaluations"] == paper[prob][preset]:
                    eval_match += 1
            else:
                disagree.append((prob, p_solved, o_solved, paper[prob][preset],
                                 o["objective_evaluations"], o["detail"]))

        lines += [
            f"## Preset `{preset}`",
            "",
            f"- Our run: **{res['n_solved']}/{res['n_problems']} solved**, "
            f"cumulative CPU {res['cum_cpu_time']:.2f}s",
            f"- Status agreement with the paper: **{agree}/{len(common)}** "
            f"({100 * agree / len(common):.1f}%)",
            f"- Of the co-solved problems, identical objective-evaluation "
            f"count: {eval_match}",
            "",
        ]
        if disagree:
            lines += [
                "| Problem | Paper (2.2.0) | Ours (2.8.0) | Paper #evals | "
                "Our #evals | Our exit |",
                "|---|---|---|---|---|---|",
            ]
            for prob, ps, os_, pe, oe, detail in disagree:
                lines.append(
                    f"| {prob} | {'solved' if ps else 'failed'} | "
                    f"{'solved' if os_ else 'failed'} | {pe if pe is not None else '--'} | "
                    f"{oe if oe is not None else '--'} | {detail} |")
            lines.append("")
        if len(disagree) > 5:
            overall_ok = False

    verdict = ("**PASS** — the harness reproduces the published preset behavior "
               "up to expected 2.2.0 -> 2.8.0 differences."
               if overall_ok else
               "**FAIL** — too many status disagreements; investigate before "
               "trusting search results.")
    lines += ["## Verdict", "", verdict, ""]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
