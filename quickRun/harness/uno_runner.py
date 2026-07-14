"""Run uno_ampl on a single .nl problem with a given option configuration.

UNO is used strictly through its run-time options (external, read-only
dependency). One call = one subprocess; the full solver log is saved.
"""
from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNO_BIN = ROOT / "external" / "uno" / "bin" / "uno_ampl"
UNO_ENV = {
    **os.environ,
    "LD_LIBRARY_PATH": f"{ROOT / 'external/uno/lib'}:{ROOT / 'external/uno/deps'}",
}

DEFAULT_TIME_LIMIT = 20.0  # seconds per problem (HS problems are tiny)

_RE_BANNER = re.compile(r"^Uno [\d.]+ \((?P<desc>.+)\)\s*$", re.MULTILINE)
_RE_FIELD = {
    "optimization_status": re.compile(r"Optimization status:\s*(.+)"),
    "solution_status": re.compile(r"Solution status:\s*(.+)"),
    "objective": re.compile(r"Objective value:\s*(\S+)"),
    "cpu_time": re.compile(r"CPU time:\s*([\d.eE+-]+)s"),
    "iterations": re.compile(r"Iterations:\s*(\d+)"),
    "objective_evaluations": re.compile(r"Objective evaluations:\s*(\d+)"),
}


def run_uno(nl_file: str | Path, options: dict, time_limit: float = DEFAULT_TIME_LIMIT,
            log_path: str | Path | None = None) -> dict:
    """Run one (problem, configuration) pair. Never raises on solver failure."""
    nl_file = Path(nl_file)
    cmd = [str(UNO_BIN), str(nl_file)]
    cmd += [f"{k}={v}" for k, v in sorted(options.items())]
    cmd += [f"time_limit={time_limit}"]

    result = {
        "problem": nl_file.stem,
        "options": dict(options),
        "optimization_status": None,
        "solution_status": None,
        "objective": None,
        "cpu_time": None,       # UNO's self-reported process CPU time (s)
        "wall_time": None,
        "iterations": None,
        "objective_evaluations": None,
        "banner": None,          # composed-method description (silent-override check)
        "exit_code": None,
        "timed_out": False,
    }

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, env=UNO_ENV,
            timeout=time_limit + 10.0,  # watchdog on top of UNO's own time_limit
        )
        output = proc.stdout + proc.stderr
        result["exit_code"] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes)
                  else (exc.stdout or ""))
        result["timed_out"] = True
        result["exit_code"] = -1
    result["wall_time"] = time.perf_counter() - t0

    m = _RE_BANNER.search(output)
    if m:
        result["banner"] = m.group("desc")
    for key, rx in _RE_FIELD.items():
        m = rx.search(output)
        if m:
            val = m.group(1).strip()
            if key in ("objective", "cpu_time"):
                try:
                    val = float(val)
                except ValueError:
                    pass
            elif key in ("iterations", "objective_evaluations"):
                val = int(val)
            result[key] = val

    if log_path is not None:
        log_path = Path(log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("$ " + " ".join(cmd) + "\n\n" + output)

    return result
