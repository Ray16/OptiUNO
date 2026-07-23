#!/usr/bin/env python3
"""Translate Vanderbei .mod files to AMPL .nl format (one-time preprocessing).

Each cute .mod file ends with `solve;` + display statements; everything from
the first standalone `solve;` on is dropped, then the model is loaded into
AMPL (demo module) and written as an ASCII .nl file.

Models that fail to translate are removed from the test set and reported in
problems/HS_model/untranslatable.md with the failure reason.

Note: the Vanderbei .mod sources (MOD_DIR, user-provided) live at
problems/HS_model/mod/, and the translated .nl test set is written alongside
them at problems/HS_model/.
"""
import re
import sys
from pathlib import Path

from amplpy import AMPL, modules

REPO_ROOT = Path(__file__).resolve().parent.parent
MOD_DIR = REPO_ROOT / "problems" / "HS_model" / "mod"   # .mod source (input, user-provided)
NL_DIR = REPO_ROOT / "problems" / "HS_model"            # .nl test set (output)
REPORT = NL_DIR / "untranslatable.md"

# hs35i/hs76i: dead links on the Vanderbei index, absent from cute.tar.gz
UNAVAILABLE = {
    "hs35i": "source .mod unavailable (dead link on Vanderbei index, not in cute.tar.gz)",
    "hs76i": "source .mod unavailable (dead link on Vanderbei index, not in cute.tar.gz)",
}

# Translate to .nl but unusable: they call the user-defined AMPL function
# `myerf` (funcadd.c), which UNO's ASL cannot load ("function myerf not
# available" -> pfgh_read_ASL crash under every configuration).
UNUSABLE = {
    "hs068": "requires user-defined AMPL function myerf (funcadd.c); UNO's ASL crashes on load",
    "hs069": "requires user-defined AMPL function myerf (funcadd.c); UNO's ASL crashes on load",
}

SOLVE_RE = re.compile(r"^\s*solve\s*;", re.MULTILINE)


def model_text(path: Path) -> str:
    text = path.read_text()
    m = SOLVE_RE.search(text)
    return text[: m.start()] if m else text


def main() -> None:
    modules.load()
    NL_DIR.mkdir(parents=True, exist_ok=True)
    ok, failed = [], []

    for mod in sorted(MOD_DIR.glob("*.mod")):
        stem = mod.stem
        if stem in UNUSABLE:
            continue
        ampl = AMPL()
        try:
            ampl.eval(model_text(mod))
            nvar = int(ampl.get_value("_nvars"))
            ncon = int(ampl.get_value("_ncons"))
            ampl.eval(f'write "g{NL_DIR / stem}";')
            if not (NL_DIR / f"{stem}.nl").exists():
                raise RuntimeError("write produced no .nl file")
            ok.append((stem, nvar, ncon))
        except Exception as exc:  # noqa: BLE001 - report every failure kind
            reason = " ".join(str(exc).split())[:300]
            failed.append((stem, reason))
            (NL_DIR / f"{stem}.nl").unlink(missing_ok=True)
        finally:
            ampl.close()

    with open(REPORT, "w") as fh:
        fh.write("# Models excluded from the test set\n\n")
        fh.write("Removed during `.mod` -> `.nl` translation "
                 "(see scripts/translate_models.py).\n\n")
        fh.write("| Model | Reason |\n|---|---|\n")
        for name, reason in sorted(UNAVAILABLE.items()):
            fh.write(f"| {name} | {reason} |\n")
        for name, reason in sorted(UNUSABLE.items()):
            fh.write(f"| {name} | {reason} |\n")
        for stem, reason in failed:
            fh.write(f"| {stem} | translation failed: {reason} |\n")

    with open(NL_DIR / "MANIFEST.csv", "w") as fh:
        fh.write("problem,n_vars,n_cons\n")
        for stem, nvar, ncon in ok:
            fh.write(f"{stem},{nvar},{ncon}\n")

    print(f"translated: {len(ok)}  failed: {len(failed)}  "
          f"unavailable: {len(UNAVAILABLE)}")
    for stem, reason in failed:
        print(f"  FAILED {stem}: {reason[:120]}")
    if failed or UNAVAILABLE:
        print(f"report: {REPORT}")
    sys.exit(0)


if __name__ == "__main__":
    main()
