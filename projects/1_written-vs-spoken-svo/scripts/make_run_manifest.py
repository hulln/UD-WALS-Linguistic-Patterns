#!/usr/bin/env python3
"""Generate or verify a canonical run manifest for the written-vs-spoken analysis.

An integrity snapshot of the canonical analysis state:
  - sha256 of the source corpora, the numbered scripts, the extracted pattern
    tables, and the key result tables;
  - the headline metrics (per corpus × S/V/O pattern counts + proportions);
  - the environment and git commit.

Usage:
  python3 scripts/make_run_manifest.py            # write canonical_run_manifest.json
  python3 scripts/make_run_manifest.py --verify   # re-check; exit 1 on any mismatch

Note: the source .conllu are gitignored, so `--verify` only checks their hashes
if they are present locally; otherwise it reports them as MISSING.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from importlib import metadata as importlib_metadata
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET = "sl_ssj_sst_written_vs_spoken"
MANIFEST_PATH = PROJECT_ROOT / "canonical_run_manifest.json"
SUMMARY_CSV = PROJECT_ROOT / "results" / "summary_table.csv"
PROP_TOLERANCE = 1e-6
PACKAGES = ["pandas", "numpy", "scipy", "matplotlib", "seaborn", "conllu", "scikit-learn"]


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_targets() -> list[Path]:
    return [
        *sorted((PROJECT_ROOT / "scripts").glob("[0-9]*.py")),
        *sorted((PROJECT_ROOT / "data" / "src").glob("*.conllu")),
        *sorted((PROJECT_ROOT / "data" / "extracted").glob("*.tsv")),
        PROJECT_ROOT / "results" / "summary_table.csv",
        PROJECT_ROOT / "results" / "proportional_differences.csv",
    ]


def collect_hashes() -> dict[str, str | None]:
    return {str(p.relative_to(PROJECT_ROOT)): sha256(p) for p in hash_targets()}


def collect_metrics() -> dict:
    summary = pd.read_csv(SUMMARY_CSV)
    patterns = {}
    for _, r in summary.iterrows():
        patterns[f"{r['Corpus']}|{r['Pattern']}"] = {
            "count": int(r["Count"]),
            "proportion": round(float(r["Proportion"]), 6),
        }
    return {"pattern_by_corpus": patterns}


def environment() -> dict:
    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = importlib_metadata.version(name)
        except importlib_metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": packages,
    }


def git_commit(path: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return None


def build_manifest() -> dict:
    return {
        "schema_version": 1,
        "dataset_tag": DATASET,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_commit": git_commit(PROJECT_ROOT),
        "note": "Written (UD Slovenian-SSJ) vs spoken (UD Slovenian-SST) S/V/O word order.",
        "environment": environment(),
        "metric_tolerance": PROP_TOLERANCE,
        "expected_metrics": collect_metrics(),
        "file_hashes": collect_hashes(),
    }


def verify(manifest: dict) -> int:
    problems = []
    current = collect_hashes()
    for name, expected in manifest["file_hashes"].items():
        now = current.get(name)
        if now is None:
            problems.append(f"MISSING input: {name}")
        elif now != expected:
            problems.append(f"CHANGED input: {name}")

    exp = manifest["expected_metrics"]["pattern_by_corpus"]
    now = collect_metrics()["pattern_by_corpus"]
    for key, e in exp.items():
        n = now.get(key)
        if n is None:
            problems.append(f"MISSING metric: {key}")
        elif n["count"] != e["count"]:
            problems.append(f"COUNT mismatch {key}: {n['count']} vs {e['count']}")
        elif abs(n["proportion"] - e["proportion"]) > PROP_TOLERANCE:
            problems.append(f"PROPORTION mismatch {key}: {n['proportion']} vs {e['proportion']}")

    if problems:
        print("VERIFY FAILED:")
        for p in problems:
            print("  -", p)
        return 1
    print("VERIFY OK: inputs and metrics match the canonical run.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Check against the existing manifest.")
    args = parser.parse_args(argv)

    if args.verify:
        if not MANIFEST_PATH.exists():
            print(f"No manifest at {MANIFEST_PATH}")
            return 1
        return verify(json.loads(MANIFEST_PATH.read_text(encoding="utf-8")))

    MANIFEST_PATH.write_text(json.dumps(build_manifest(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
