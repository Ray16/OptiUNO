"""Locate the UNO solver binary (``uno_ampl``).

Single source of truth for *where UNO lives*. Selection is **system-first**: a
UNO installed on this machine (via the ``UNO_AMPL_BIN`` env var, or ``uno_ampl``
on ``PATH``) is preferred, and the self-contained build bundled in this repo at
``external/uno/`` is used only as a fallback when no system UNO is available.

Every caller that needs the binary should go through :func:`select_uno_bin` (or
:func:`bundled_uno_bin` when it must pin the bundled build), so the lookup logic
and the bundled path live in exactly one place.

Stdlib only -- installs nothing.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
ENV_BIN = "UNO_AMPL_BIN"          # env var pointing at the uno_ampl binary
DEFAULT_BIN_NAME = "uno_ampl"     # looked up on PATH

# Repo root = the parent of the optiuno/ package (this file is optiuno/utils.py).
REPO_ROOT = Path(__file__).resolve().parents[1]

# The self-contained UNO release bundled in the repo (moved here from quickRun/).
# This is the one place the bundled path is written down.
BUNDLED_UNO_BIN = REPO_ROOT / "external" / "uno" / "bin" / "uno_ampl"


# --------------------------------------------------------------------------- #
# Selection
# --------------------------------------------------------------------------- #
def _usable(cand) -> bool:
    """True if ``cand`` is an existing, executable file."""
    return bool(cand) and Path(cand).is_file() and os.access(cand, os.X_OK)


def bundled_uno_bin() -> Path:
    """Path to the bundled ``uno_ampl`` (``external/uno/bin/uno_ampl`` at the repo root).

    Returned unconditionally (not validated), so callers can reference the pinned
    build even before it is exercised. Use :func:`select_uno_bin` when you want
    system-first selection with this as the fallback.
    """
    return BUNDLED_UNO_BIN


def select_uno_bin(explicit: str | os.PathLike | None = None) -> str:
    """Locate ``uno_ampl``, preferring a system install over the bundled build.

    Precedence (first usable candidate wins; usable = existing, executable file):

    1. ``explicit`` -- a path passed by the caller (e.g. ``--uno-bin``)
    2. ``$UNO_AMPL_BIN`` -- a system UNO pointed at by the env var
    3. ``uno_ampl`` on ``PATH`` -- a system UNO on the shell path
    4. :data:`BUNDLED_UNO_BIN` -- the prebuilt UNO bundled under ``external/uno``

    Returns the resolved absolute path as a ``str``. Raises ``FileNotFoundError``
    with guidance if not even the bundled build is usable.
    """
    candidates = [
        explicit,
        os.environ.get(ENV_BIN),
        shutil.which(DEFAULT_BIN_NAME),
        BUNDLED_UNO_BIN,
    ]
    for cand in candidates:
        if _usable(cand):
            return str(Path(cand).resolve())
    raise FileNotFoundError(
        "Could not locate the 'uno_ampl' binary. Pass an explicit path (uno_bin=... "
        f"or --uno-bin), set the {ENV_BIN} environment variable to its path, put it "
        f"on PATH, or restore the bundled build at {BUNDLED_UNO_BIN}.")
