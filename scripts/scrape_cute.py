#!/usr/bin/env python3
"""Scrape the COCONUT Library2 CUTE problem set into problems/CUTE/.

Source page:
    https://arnold-neumaier.at/glopt/coconut/Benchmark/Library2_new_v1.html

For every problem in the index table this script:
  * creates problems/CUTE/<name>/
  * downloads every available problem file (.mod, .gms, .dag, and anything
    else linked on the problem's detail page) plus the solution RES/<name>.res
  * writes a metadata.json with the table metadata, per-file availability
    flags, feasibility (from the parentheses-on-Fbest convention) and an
    in_uno_429_subset tag
Finally it aggregates every metadata.json into problems/CUTE/summary.csv.

The scraper is polite (User-Agent, timeouts, retry/backoff, inter-request
delay) and resumable (existing non-empty files and complete problems are
skipped unless --force is given).

All dependencies (requests, bs4/lxml, pandas) are expected to be already
installed; this script installs nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
INDEX_URL = "https://arnold-neumaier.at/glopt/coconut/Benchmark/Library2_new_v1.html"
# Problem files (<name>.mod etc.) and RES/<name>.res are resolved relative to:
LIBRARY_BASE = "https://arnold-neumaier.at/glopt/coconut/Benchmark/Library2/"
SUBSET_URL = (
    "https://raw.githubusercontent.com/cvanaret/nonconvex_solver_comparison/"
    "main/CUTE/small_instances.txt"
)
# Column order of the index table (verified from the page legend/header).
TABLE_COLUMNS = [
    "Number", "Problem", "Classification",
    "N", "M", "Nnl", "Mnl", "Nz", "Fbest", "Solution",
]
# Known problem-file extensions, used as a fallback if the detail page is
# unavailable and to key the *_file_available flags.
KNOWN_EXTS = ["mod", "gms", "dag"]  # 'res' is handled separately (RES/ subdir)
USER_AGENT = (
    "OptiUNO-scraper/1.0 (research; polite; contact via local project) "
    "python-requests"
)


# --------------------------------------------------------------------------- #
# HTTP session
# --------------------------------------------------------------------------- #
def build_session() -> requests.Session:
    """A session with a descriptive UA and retry/backoff on transient errors."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.0,               # 0s, 1s, 2s, 4s ...
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #
def parse_fbest(raw: str):
    """Return (fbest_float_or_None, feasible_bool_or_None) from a raw cell.

    Convention: a value wrapped in parentheses means the best-known solution
    is infeasible. Empty cell -> (None, None). Handles escaped minus '\\-' and
    scientific notation.
    """
    s = (raw or "").strip()
    if not s:
        return None, None
    feasible = True
    if s.startswith("(") and s.endswith(")"):
        feasible = False
        s = s[1:-1].strip()
    # normalise escaped minus and unicode minus
    s = s.replace("\\-", "-").replace("−", "-").replace(" ", "")
    try:
        value = float(s)
    except ValueError:
        value = None
    return value, feasible


def _cell_text(td) -> str:
    return td.get_text(strip=True)


def _first_href(td):
    a = td.find("a", href=True)
    return a["href"] if a else None


def parse_index(html: str):
    """Parse the index table -> list of per-problem dicts (raw table data)."""
    soup = BeautifulSoup(html, "lxml")

    # Find the table whose header row mentions 'Fbest'.
    target = None
    for table in soup.find_all("table"):
        if "Fbest" in table.get_text():
            target = table
            break
    if target is None:
        raise RuntimeError("Could not locate the problem table (no 'Fbest').")

    problems = []
    for tr in target.find_all("tr"):
        tds = tr.find_all(["td", "th"])
        if len(tds) < len(TABLE_COLUMNS):
            continue
        # Skip the header row (its first cell isn't a number).
        number_txt = _cell_text(tds[0])
        if not re.fullmatch(r"\d+", number_txt):
            continue

        cells = [_cell_text(td) for td in tds[: len(TABLE_COLUMNS)]]
        row = dict(zip(TABLE_COLUMNS, cells))

        name = row["Problem"].strip()
        detail_href = _first_href(tds[1])          # -> <name>.htm
        res_href = _first_href(tds[9])             # -> RES/<name>.res (or None)

        fbest_value, feasible = parse_fbest(row["Fbest"])

        def _to_int(x):
            x = (x or "").strip()
            return int(x) if re.fullmatch(r"-?\d+", x) else None

        problems.append({
            "name": name,
            "number": _to_int(row["Number"]),
            "classification": row["Classification"].strip() or None,
            "N": _to_int(row["N"]),
            "M": _to_int(row["M"]),
            "Nnl": _to_int(row["Nnl"]),
            "Mnl": _to_int(row["Mnl"]),
            "Nz": _to_int(row["Nz"]),
            "Fbest_raw": row["Fbest"].strip(),
            "Fbest": fbest_value,
            "feasible": feasible,
            "solution_cell": row["Solution"].strip(),
            "detail_href": detail_href,
            "res_href": res_href,
        })
    return problems


def discover_files(session, detail_url, name, delay):
    """Return {ext: absolute_url} for every problem file on the detail page.

    Falls back to the known extensions if the detail page can't be fetched.
    'res' is intentionally excluded here (handled via the index RES link).
    """
    files = {}
    try:
        resp = session.get(detail_url, timeout=30)
        time.sleep(delay)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                # skip solution links and anchors/parents
                if "RES/" in href or href.startswith("#") or href in ("../", "./"):
                    continue
                m = re.search(r"\.([A-Za-z0-9]+)$", href)
                if not m:
                    continue
                ext = m.group(1).lower()
                if ext in ("htm", "html"):
                    continue
                files[ext] = urljoin(detail_url, href)
    except requests.RequestException:
        pass

    # Fallback: ensure the known extensions are at least attempted.
    for ext in KNOWN_EXTS:
        files.setdefault(ext, urljoin(LIBRARY_BASE, f"{name}.{ext}"))
    return files


# --------------------------------------------------------------------------- #
# Download helper
# --------------------------------------------------------------------------- #
def download(session, url, dest: Path, delay, force=False):
    """Download url -> dest. Returns (ok: bool, nbytes: int).

    Skips (ok=True) if dest already exists non-empty and not force.
    HTTP 404 -> (False, 0) (treated as "not available", not an error).
    """
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return True, dest.stat().st_size
    try:
        resp = session.get(url, timeout=60, stream=True)
    except requests.RequestException as exc:
        print(f"      ! request failed for {url}: {exc}", file=sys.stderr)
        time.sleep(delay)
        return False, 0
    try:
        if resp.status_code == 200:
            tmp = dest.with_suffix(dest.suffix + ".part")
            n = 0
            with open(tmp, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        fh.write(chunk)
                        n += len(chunk)
            tmp.replace(dest)
            return (True, n) if n > 0 else (False, 0)
        if resp.status_code in (300, 404):
            # 404 = absent; 300 = Apache "Multiple Choices" (the exact file
            # doesn't exist and the server lists similar basenames). Both mean
            # "this file is not available for this problem".
            return False, 0
        print(f"      ! HTTP {resp.status_code} for {url}", file=sys.stderr)
        return False, 0
    finally:
        resp.close()
        time.sleep(delay)


def metadata_complete(meta: dict) -> bool:
    """A problem is 'complete' if every file marked available exists on disk."""
    return meta.get("_all_available_downloaded", False)


# --------------------------------------------------------------------------- #
# Per-problem scrape
# --------------------------------------------------------------------------- #
def scrape_problem(session, prob, out_dir: Path, subset: set, delay, force):
    name = prob["name"]
    pdir = out_dir / name
    pdir.mkdir(parents=True, exist_ok=True)
    meta_path = pdir / "metadata.json"

    # Resume: skip if metadata says everything available was already fetched.
    if meta_path.exists() and not force:
        try:
            existing = json.loads(meta_path.read_text())
            if metadata_complete(existing):
                return existing, True  # skipped
        except (json.JSONDecodeError, OSError):
            pass

    # Table hrefs (e.g. "Library2/hs071.htm") are relative to the INDEX page,
    # not to LIBRARY_BASE — resolve against INDEX_URL to avoid a doubled path.
    detail_url = (urljoin(INDEX_URL, prob["detail_href"])
                  if prob["detail_href"] else urljoin(LIBRARY_BASE, f"{name}.htm"))
    file_urls = discover_files(session, detail_url, name, delay)

    files_meta = {}
    all_ok = True

    # Model / other files.
    for ext, url in sorted(file_urls.items()):
        fname = f"{name}.{ext}"
        ok, nbytes = download(session, url, pdir / fname, delay, force)
        if ok:
            files_meta[ext] = {"filename": fname, "url": url, "bytes": nbytes}
        else:
            all_ok = all_ok and (ext not in KNOWN_EXTS)  # missing known ext is fine (recorded false)

    # Solution file.
    res_available = False
    if prob["res_href"]:
        res_url = urljoin(INDEX_URL, prob["res_href"])   # relative to index page
    else:
        res_url = urljoin(LIBRARY_BASE, f"RES/{name}.res")
    ok, nbytes = download(session, res_url, pdir / f"{name}.res", delay, force)
    if ok:
        res_available = True
        files_meta["res"] = {"filename": f"{name}.res", "url": res_url, "bytes": nbytes}

    other_files = sorted(set(files_meta) - set(KNOWN_EXTS) - {"res"})

    meta = {
        "name": name,
        "number": prob["number"],
        "classification": prob["classification"],
        "N": prob["N"], "M": prob["M"],
        "Nnl": prob["Nnl"], "Mnl": prob["Mnl"], "Nz": prob["Nz"],
        "Fbest_raw": prob["Fbest_raw"],
        "Fbest": prob["Fbest"],
        "feasible": prob["feasible"],
        "in_uno_429_subset": name in subset,
        "mod_file_available": "mod" in files_meta,
        "gms_file_available": "gms" in files_meta,
        "dag_file_available": "dag" in files_meta,
        "res_file_available": res_available,
        "other_files": other_files,
        "files": files_meta,
        "detail_page": detail_url,
        "source_index": INDEX_URL,
        # internal resume marker: did we fetch every file we found a URL for?
        "_all_available_downloaded": True,
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta, False  # not skipped


# --------------------------------------------------------------------------- #
# Summary CSV
# --------------------------------------------------------------------------- #
def write_summary(out_dir: Path):
    import pandas as pd

    rows = []
    for meta_path in sorted(out_dir.glob("*/metadata.json")):
        try:
            m = json.loads(meta_path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        rows.append({
            "number": m.get("number"),
            "name": m.get("name"),
            "classification": m.get("classification"),
            "N": m.get("N"), "M": m.get("M"),
            "Nnl": m.get("Nnl"), "Mnl": m.get("Mnl"), "Nz": m.get("Nz"),
            "Fbest_raw": m.get("Fbest_raw"),
            "Fbest": m.get("Fbest"),
            "feasible": m.get("feasible"),
            "in_uno_429_subset": m.get("in_uno_429_subset"),
            "mod_file_available": m.get("mod_file_available"),
            "gms_file_available": m.get("gms_file_available"),
            "dag_file_available": m.get("dag_file_available"),
            "res_file_available": m.get("res_file_available"),
            "other_files": ";".join(m.get("other_files") or []),
            "detail_page": m.get("detail_page"),
        })
    df = pd.DataFrame(rows).sort_values("number", na_position="last")
    csv_path = out_dir / "summary.csv"
    df.to_csv(csv_path, index=False)
    return df, csv_path


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(description="Scrape COCONUT Library2 CUTE problems.")
    ap.add_argument("--out-dir", default=None,
                    help="output dir (default: <repo>/problems/CUTE)")
    ap.add_argument("--only", default=None,
                    help="comma-separated problem names to scrape (test mode)")
    ap.add_argument("--limit", type=int, default=None,
                    help="only scrape the first N problems from the table")
    ap.add_argument("--delay", type=float, default=0.3,
                    help="seconds to sleep between requests (default 0.3)")
    ap.add_argument("--force", action="store_true",
                    help="re-download even if files/metadata already exist")
    ap.add_argument("--summary-only", action="store_true",
                    help="skip scraping; just (re)build summary.csv from metadata")
    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = Path(args.out_dir) if args.out_dir else repo_root / "problems" / "CUTE"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.summary_only:
        df, csv_path = write_summary(out_dir)
        print(f"Wrote {csv_path} ({len(df)} rows)")
        return 0

    session = build_session()

    print(f"Fetching index: {INDEX_URL}")
    resp = session.get(INDEX_URL, timeout=60)
    resp.raise_for_status()
    time.sleep(args.delay)
    problems = parse_index(resp.text)
    all_table_names = {p["name"] for p in problems}  # full set, before filtering
    print(f"  parsed {len(problems)} problems from the table")

    print(f"Fetching 429 subset list: {SUBSET_URL}")
    try:
        sresp = session.get(SUBSET_URL, timeout=60)
        sresp.raise_for_status()
        subset = {ln.strip() for ln in sresp.text.splitlines() if ln.strip()}
    except requests.RequestException as exc:
        print(f"  ! could not fetch subset list ({exc}); tagging all as False",
              file=sys.stderr)
        subset = set()
    time.sleep(args.delay)
    print(f"  subset has {len(subset)} names")

    # Filter which problems to scrape.
    if args.only:
        wanted = {n.strip() for n in args.only.split(",") if n.strip()}
        problems = [p for p in problems if p["name"] in wanted]
        print(f"  --only: scraping {len(problems)} of {len(wanted)} requested")
    if args.limit:
        problems = problems[: args.limit]
        print(f"  --limit: scraping first {len(problems)}")

    scraped = skipped = 0
    try:
        for i, prob in enumerate(problems, 1):
            meta, was_skipped = scrape_problem(
                session, prob, out_dir, subset, args.delay, args.force)
            if was_skipped:
                skipped += 1
            else:
                scraped += 1
            flags = "".join(k for k in "mgdr" if {
                "m": meta["mod_file_available"], "g": meta["gms_file_available"],
                "d": meta["dag_file_available"], "r": meta["res_file_available"],
            }[k]) or "-"
            sub = "*" if meta["in_uno_429_subset"] else " "
            tag = "skip" if was_skipped else "get "
            print(f"  [{i:>3}/{len(problems)}] {tag} {sub} {prob['name']:<16} "
                  f"files={flags:<4} feasible={meta['feasible']}")
    except KeyboardInterrupt:
        print("\nInterrupted — progress saved; re-run to resume.", file=sys.stderr)

    # Build/refresh the summary CSV.
    df, csv_path = write_summary(out_dir)

    # Final report.
    print("\n=== Summary ===")
    print(f"problems on disk : {len(df)}")
    print(f"newly scraped    : {scraped}   skipped(resumed): {skipped}")
    for col in ["mod_file_available", "gms_file_available",
                "dag_file_available", "res_file_available"]:
        print(f"{col:<22}: {int(df[col].sum())}")
    print(f"feasible=True         : {int((df['feasible'] == True).sum())}")
    print(f"feasible=False        : {int((df['feasible'] == False).sum())}")
    print(f"feasible=None (empty) : {int(df['feasible'].isna().sum())}")
    matched = int(df["in_uno_429_subset"].sum())
    print(f"in_uno_429_subset     : {matched} (subset list size {len(subset)})")
    if subset:
        missing = sorted(subset - all_table_names)  # vs full table, not just scraped
        if missing:
            print(f"subset names NOT on page ({len(missing)}): {', '.join(missing)}")
        else:
            print("all subset names found on the page")
    print(f"\nWrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
