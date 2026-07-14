#!/usr/bin/env python3
"""Convert CUTE AMPL .mod models into UNO-ready .nl files.

For every problem folder problems/CUTE/<name>/ that has a <name>.mod, this
script writes an AMPL "g"-format / ASCII .nl into the SAME folder, using the
AMPL processor via amplpy.

Two variants, selected by --presolve (AMPL's presolver rewrites the model:
fixes/eliminates variables, drops redundant constraints, tightens bounds):
  * default (presolve OFF, `option presolve 0`) -> <name>.nl -- the faithful,
    unsimplified problem exactly as written in the .mod. This is the primary
    file for benchmarking UNO.
  * --presolve (presolve ON, `option presolve 10`) -> <name>_presolve.nl -- the
    AMPL-presolved (reduced) problem.

It then:
  * updates that problem's metadata.json (nl_file_available /
    nl_presolve_file_available flags, files["nl"] / files["nl_presolve"]
    entries, nl_conversion / nl_presolve_conversion status/reason), and
  * refreshes problems/CUTE/summary.csv with the nl_* columns.

The .mod files ship as full AMPL scripts (they end in `solve;` and carry
`display`/`printf` lines). Those *command* statements are stripped before the
model is handed to AMPL so nothing is actually solved; model/data statements
(`param`, `var`, `minimize`, `subject to`, `data`, `let`, ...) are kept so the
emitted .nl carries the problem and its starting point.

This script is resumable (an existing non-empty target .nl is skipped unless
--force) and installs nothing. It requires `amplpy`; if that import fails it
prints install instructions and exits without a traceback.

Run it with the Python that has amplpy installed, e.g.:
    python scripts/problem_parser.py --only hs071            # faithful <name>.nl
    python scripts/problem_parser.py --only hs071 --presolve # <name>_presolve.nl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
# AMPL *command* statements to drop from a .mod before conversion. Everything
# else (model + data + `let` starting points) is kept. Matched on the leading
# keyword of each ';'-terminated statement, case-insensitively.
COMMAND_KEYWORDS = frozenset({
    "solve", "display", "print", "printf", "expand", "close", "shell",
    "exit", "quit", "reset", "write", "csvdisplay",
})
# Suffix (no dots) for the throwaway stub/model AMPL writes, renamed on success.
TMP_SUFFIX = "__optiuno_tmp"
# summary.csv column order produced by scrape_cute.py; the nl columns are
# inserted right after res_file_available.
BASE_SUMMARY_COLUMNS = [
    "number", "name", "classification", "N", "M", "Nnl", "Mnl", "Nz",
    "Fbest_raw", "Fbest", "feasible", "in_uno_429_subset",
    "mod_file_available", "gms_file_available", "dag_file_available",
    "res_file_available", "other_files", "detail_page",
]
NL_COLUMNS = [
    "nl_file_available", "nl_presolve_file_available",
    "nl_conversion_status", "nl_presolve_conversion_status",
]


# --------------------------------------------------------------------------- #
# Presolve variants
# --------------------------------------------------------------------------- #
def variant_spec(presolve: bool) -> dict:
    """Filenames + metadata/summary keys for the presolve-off / -on variant.

    off (default): faithful model  -> <name>.nl
    on (--presolve): AMPL-presolved -> <name>_presolve.nl
    """
    if presolve:
        return {
            "presolve_passes": 10,          # AMPL's default number of passes
            "suffix": "_presolve",          # <name>_presolve.nl
            "avail_key": "nl_presolve_file_available",
            "files_key": "nl_presolve",
            "conv_key": "nl_presolve_conversion",
            "label": "on ",
        }
    return {
        "presolve_passes": 0,               # fully disable AMPL presolve
        "suffix": "",                       # <name>.nl
        "avail_key": "nl_file_available",
        "files_key": "nl",
        "conv_key": "nl_conversion",
        "label": "off",
    }

INSTALL_HINT = """\
amplpy is not available in this Python environment.

problem_parser.py needs amplpy (the AMPL Python API + the AMPL processor) to
translate AMPL .mod models into .nl files -- no other tool parses AMPL .mod
syntax.

Install it into the Python environment you run this script with (you run these;
the script won't). `pip install amplpy` gives only the Python API; the AMPL
engine comes from the `base` module:

    python -m pip install amplpy --upgrade
    python -m amplpy.modules install base

Writing .nl needs the `base` AMPL engine only -- no solver module is required.

License note: the bundled demo license allows `write` but caps model size (~300
nonlinear vars/constraints); AMPL Community Edition removes the cap but BLOCKS
`write` (the command this script uses to emit .nl). To convert the larger
problems, use a full AMPL license -- e.g. the free "AMPL for Academics" license
(https://portal.ampl.com/account/ampl) -- and activate it with:

    python -m amplpy.modules activate <license-uuid>

Then re-run this script with that same Python.
"""


# --------------------------------------------------------------------------- #
# amplpy loader
# --------------------------------------------------------------------------- #
def require_ampl():
    """Return the amplpy.AMPL class, or print install help and exit(2)."""
    try:
        from amplpy import AMPL
    except ImportError:
        print(INSTALL_HINT, file=sys.stderr)
        raise SystemExit(2)
    return AMPL


def _fresh_ampl(ampl, AMPL):
    """Reset `ampl` to a clean state; recreate it if the process is broken.

    reset() clears the model/data, so a healthy instance is reusable across all
    problems. If reset() itself throws (dead engine), replace the instance.
    """
    try:
        ampl.reset()
        return ampl
    except Exception:
        try:
            ampl.close()
        except Exception:
            pass
        new = AMPL()
        new.reset()
        return new


# --------------------------------------------------------------------------- #
# .mod preprocessing
# --------------------------------------------------------------------------- #
def _strip_comments(text: str) -> str:
    """Remove AMPL comments (`/* ... */` blocks and `# ... EOL`)."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"#.*", "", text)
    return text


def preprocess_mod(text: str) -> str:
    """Return a solve-free model: drop command statements, keep model+data.

    Splits on ';' after stripping comments and drops any statement whose leading
    keyword is in COMMAND_KEYWORDS (solve/display/printf/...). Model and data
    statements -- including `data;` mode switches and `let` starting points --
    are preserved in their original order.
    """
    kept = []
    for stmt in _strip_comments(text).split(";"):
        s = stmt.strip()
        if not s:
            continue
        m = re.match(r"[A-Za-z_][A-Za-z_0-9.]*", s)
        keyword = m.group(0).lower() if m else ""
        if keyword in COMMAND_KEYWORDS:
            continue
        kept.append(s)
    if not kept:
        return ""
    return ";\n".join(kept) + ";\n"


# --------------------------------------------------------------------------- #
# Conversion
# --------------------------------------------------------------------------- #
def _first_line(msg: str) -> str:
    lines = (msg or "").strip().splitlines()
    return lines[0][:200] if lines else ""


def convert_one(ampl, name: str, mod_path: Path, nl_path: Path, presolve: int):
    """Convert mod_path -> nl_path with the given AMPL presolve level.

    Returns (status, reason, nbytes). status: "converted" | "failed". Assumes
    `ampl` was just reset (fresh). The caller handles the skip-if-exists case.
    `presolve` is the AMPL `option presolve` value (0 = off, 10 = default on).
    AMPL errors (parse errors, size-limit, ...) are caught and reported as
    ("failed", <message>, 0).
    """
    pdir = nl_path.parent
    tmp_mod = pdir / f"{name}{TMP_SUFFIX}.mod"     # cleaned model AMPL will read
    tmp_stub = f"{name}{TMP_SUFFIX}"               # AMPL writes <stub>.nl
    tmp_nl = pdir / f"{tmp_stub}.nl"

    cleaned = preprocess_mod(mod_path.read_text(errors="replace"))
    if not cleaned:
        return "failed", "empty model after preprocessing", 0

    try:
        tmp_mod.write_text(cleaned)
        ampl.cd(str(pdir))
        ampl.eval(f"option presolve {presolve};")  # control model simplification
        ampl.read(str(tmp_mod))                    # run model+data, no solve
        ampl.eval(f'write "g{tmp_stub}";')         # emit ASCII nl
    except Exception as exc:                        # amplpy raises varied types
        return "failed", _first_line(str(exc)), 0
    finally:
        try:
            tmp_mod.unlink()
        except OSError:
            pass

    if not tmp_nl.exists() or tmp_nl.stat().st_size == 0:
        # AMPL declined to write (e.g. demo size-limit) without raising.
        try:
            tmp_nl.unlink()
        except OSError:
            pass
        return "failed", "no .nl produced (demo size-limit or empty model?)", 0

    tmp_nl.replace(nl_path)                         # atomic within the folder
    return "converted", "", nl_path.stat().st_size


# --------------------------------------------------------------------------- #
# metadata / summary
# --------------------------------------------------------------------------- #
def update_metadata(pdir: Path, name: str, conv_key: str, status: str, reason: str):
    """Merge nl_* fields into the problem's metadata.json (if present).

    Both availability flags and both files[] entries are derived from what is
    actually on disk (self-healing), so a single run keeps the other variant's
    flags correct too. Only `conv_key` (the variant just run) gets this run's
    status/reason; the other variant's conversion dict is set to "present" if
    its file exists and it has none yet.
    """
    meta_path = pdir / "metadata.json"
    if not meta_path.exists():
        return
    try:
        meta = json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        return

    files = meta.get("files") or {}
    # variant -> (filename, availability key, files key, conversion key)
    variants = [
        (f"{name}.nl", "nl_file_available", "nl", "nl_conversion"),
        (f"{name}_presolve.nl", "nl_presolve_file_available",
         "nl_presolve", "nl_presolve_conversion"),
    ]
    for fname, avail_key, files_key, ckey in variants:
        fpath = pdir / fname
        exists = fpath.exists() and fpath.stat().st_size > 0
        meta[avail_key] = exists
        if exists:
            files[files_key] = {"filename": fname, "bytes": fpath.stat().st_size}
        else:
            files.pop(files_key, None)
        if ckey == conv_key:
            meta[ckey] = {"status": status, "reason": reason}
        elif exists and ckey not in meta:
            meta[ckey] = {"status": "present", "reason": ""}
    meta["files"] = files

    meta_path.write_text(json.dumps(meta, indent=2))


def _reorder_summary(df):
    """Place the nl columns right after res_file_available, keep the rest."""
    cols = [c for c in df.columns if c not in NL_COLUMNS]
    anchor = "res_file_available"
    idx = cols.index(anchor) + 1 if anchor in cols else len(cols)
    cols[idx:idx] = NL_COLUMNS
    return df[cols]


def update_summary_csv(corpus_dir: Path):
    """Refresh summary.csv's nl_* columns from each metadata.json (source of
    truth): nl_file_available, nl_presolve_file_available, and the two
    conversion-status columns. If summary.csv is missing, rebuilds the base
    table from metadata.json first. Returns (df, csv_path).
    """
    import pandas as pd

    off_avail, on_avail, off_status, on_status = {}, {}, {}, {}
    meta_rows = []
    for meta_path in sorted(corpus_dir.glob("*/metadata.json")):
        try:
            m = json.loads(meta_path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        nm = m.get("name")
        if nm is None:
            continue
        off_avail[nm] = bool(m.get("nl_file_available", False))
        on_avail[nm] = bool(m.get("nl_presolve_file_available", False))
        off_status[nm] = (m.get("nl_conversion") or {}).get("status")
        on_status[nm] = (m.get("nl_presolve_conversion") or {}).get("status")
        meta_rows.append(m)

    csv_path = corpus_dir / "summary.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        # Fallback: rebuild the base table from metadata.json files.
        rows = []
        for m in meta_rows:
            row = {c: m.get(c) for c in BASE_SUMMARY_COLUMNS}
            row["other_files"] = ";".join(m.get("other_files") or [])
            rows.append(row)
        df = pd.DataFrame(rows, columns=BASE_SUMMARY_COLUMNS)
        if "number" in df:
            df = df.sort_values("number", na_position="last")

    df["nl_file_available"] = df["name"].map(off_avail).fillna(False).astype(bool)
    df["nl_presolve_file_available"] = df["name"].map(on_avail).fillna(False).astype(bool)
    df["nl_conversion_status"] = df["name"].map(off_status)
    df["nl_presolve_conversion_status"] = df["name"].map(on_status)
    df = _reorder_summary(df)
    df.to_csv(csv_path, index=False)
    return df, csv_path


def write_report(corpus_dir: Path, results, presolve: bool):
    import pandas as pd

    rows = [{
        "name": r["name"], "presolve": presolve, "status": r["status"],
        "reason": r["reason"], "nl_bytes": r["nbytes"],
        "in_uno_429_subset": r["in_subset"],
    } for r in results]
    path = corpus_dir / "nl_conversion_report.csv"
    pd.DataFrame(rows, columns=["name", "presolve", "status", "reason",
                                "nl_bytes", "in_uno_429_subset"]).to_csv(
        path, index=False)
    return path


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #
def _in_subset(pdir: Path) -> bool:
    meta_path = pdir / "metadata.json"
    if not meta_path.exists():
        return False
    try:
        return bool(json.loads(meta_path.read_text()).get("in_uno_429_subset"))
    except (json.JSONDecodeError, OSError):
        return False


def discover_problems(corpus_dir: Path, subset_only: bool):
    """Return [(name, pdir, mod_path)] for folders that have a <name>.mod."""
    selected = []
    for pdir in sorted(corpus_dir.iterdir()):
        if not pdir.is_dir():
            continue
        name = pdir.name
        mod = pdir / f"{name}.mod"
        if not mod.exists():
            continue
        if subset_only and not _in_subset(pdir):
            continue
        selected.append((name, pdir, mod))
    return selected


def _is_size_limit(reason: str) -> bool:
    return bool(re.search(r"demo|licen[sc]e|too (big|large)|exceed|limited to|size",
                          reason or "", re.I))


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Convert CUTE .mod models to UNO-ready .nl files via amplpy.")
    ap.add_argument("--corpus-dir", default=None,
                    help="corpus dir (default: <repo>/problems/CUTE)")
    ap.add_argument("--only", default=None,
                    help="comma-separated problem names to convert (test mode)")
    ap.add_argument("--limit", type=int, default=None,
                    help="only convert the first N problems")
    ap.add_argument("--subset-only", action="store_true",
                    help="only convert problems flagged in_uno_429_subset")
    ap.add_argument("--presolve", action="store_true",
                    help="enable AMPL presolve (default off); writes the reduced "
                         "<name>_presolve.nl instead of the faithful <name>.nl")
    ap.add_argument("--force", action="store_true",
                    help="re-convert even if the target .nl already exists")
    ap.add_argument("--no-summary", action="store_true",
                    help="skip refreshing summary.csv")
    ap.add_argument("--report", action="store_true",
                    help="also write nl_conversion_report.csv")
    args = ap.parse_args(argv)

    variant = variant_spec(args.presolve)

    repo_root = Path(__file__).resolve().parent.parent
    corpus_dir = Path(args.corpus_dir) if args.corpus_dir else repo_root / "problems" / "CUTE"
    if not corpus_dir.is_dir():
        print(f"corpus dir not found: {corpus_dir}", file=sys.stderr)
        return 1

    selected = discover_problems(corpus_dir, args.subset_only)
    if args.only:
        wanted = {n.strip() for n in args.only.split(",") if n.strip()}
        selected = [t for t in selected if t[0] in wanted]
        print(f"--only: converting {len(selected)} of {len(wanted)} requested")
    if args.limit:
        selected = selected[: args.limit]
        print(f"--limit: converting first {len(selected)}")
    if not selected:
        print("No matching problems with a .mod file found.", file=sys.stderr)
        return 1

    AMPL = require_ampl()
    try:
        ampl = AMPL()
    except Exception as exc:
        print(f"! failed to start the AMPL engine: {exc}", file=sys.stderr)
        print(INSTALL_HINT, file=sys.stderr)
        return 2

    print(f"Converting {len(selected)} problem(s) in {corpus_dir} "
          f"(presolve {variant['label'].strip()} -> <name>{variant['suffix']}.nl)")
    results = []
    converted = skipped = failed = 0
    try:
        for i, (name, pdir, mod) in enumerate(selected, 1):
            nl_path = pdir / f"{name}{variant['suffix']}.nl"
            if nl_path.exists() and nl_path.stat().st_size > 0 and not args.force:
                status, reason, nbytes = "skipped", "exists", nl_path.stat().st_size
            else:
                ampl = _fresh_ampl(ampl, AMPL)
                status, reason, nbytes = convert_one(
                    ampl, name, mod, nl_path, variant["presolve_passes"])

            update_metadata(pdir, name, variant["conv_key"], status, reason)
            in_subset = _in_subset(pdir)
            results.append({"name": name, "status": status, "reason": reason,
                            "nbytes": nbytes, "in_subset": in_subset})

            if status == "converted":
                converted += 1
                tag = "conv"
            elif status == "skipped":
                skipped += 1
                tag = "skip"
            else:
                failed += 1
                tag = "FAIL"
            sub = "*" if in_subset else " "
            size = f"{nbytes}b" if status in ("converted", "skipped") else "-"
            note = f"  {reason}" if status == "failed" else ""
            print(f"  [{i:>3}/{len(selected)}] {tag} {sub} {name:<16} "
                  f"nl={size:<9}{note}")
    except KeyboardInterrupt:
        print("\nInterrupted — progress saved; re-run to resume.", file=sys.stderr)
    finally:
        try:
            ampl.close()
        except Exception:
            pass

    if not args.no_summary:
        try:
            df, csv_path = update_summary_csv(corpus_dir)
            n_off = int(df["nl_file_available"].sum())
            n_on = int(df["nl_presolve_file_available"].sum())
            print(f"\nUpdated {csv_path} — nl_file_available={n_off}/{len(df)}, "
                  f"nl_presolve_file_available={n_on}/{len(df)}")
        except Exception as exc:
            print(f"! could not update summary.csv: {exc}", file=sys.stderr)

    if args.report:
        try:
            path = write_report(corpus_dir, results, args.presolve)
            print(f"Wrote {path}")
        except Exception as exc:
            print(f"! could not write report: {exc}", file=sys.stderr)

    # Final report.
    size_fails = [r for r in results if r["status"] == "failed" and _is_size_limit(r["reason"])]
    other_fails = [r for r in results if r["status"] == "failed" and not _is_size_limit(r["reason"])]

    print("\n=== Summary ===")
    print(f"selected       : {len(selected)}")
    print(f"converted      : {converted}")
    print(f"skipped(exist) : {skipped}")
    print(f"failed         : {failed}")
    if size_fails:
        names = ", ".join(r["name"] for r in size_fails[:20])
        more = " ..." if len(size_fails) > 20 else ""
        print(f"  size-limit failures ({len(size_fails)}) — use a full/academic AMPL license to fix:")
        print(f"    {names}{more}")
    if other_fails:
        print(f"  other failures ({len(other_fails)}):")
        for r in other_fails[:20]:
            print(f"    {r['name']}: {r['reason']}")
        if len(other_fails) > 20:
            print(f"    ... and {len(other_fails) - 20} more")

    return 1 if other_fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
