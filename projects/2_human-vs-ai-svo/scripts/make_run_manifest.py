#!/usr/bin/env python3
"""Generate or verify a canonical run manifest for the Human-vs-AI SVO pipeline.

The manifest records, for one canonical run:
  - sha256 of the stable inputs (raw .conllu, metadata.csv, the scripts);
  - the headline metrics (per language/genre SVO counts + proportions, and the
    STARK-vs-direct-parser max difference);
  - the environment and git commit.

Usage:
  python3 scripts/make_run_manifest.py            # write canonical_run_manifest.json
  python3 scripts/make_run_manifest.py --verify   # re-check; exit 1 on any mismatch

Note: the raw .conllu are gitignored, so `--verify` only checks their hashes if
they are present locally; otherwise it reports them as MISSING.
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
DATASET = "nh_svo_jun_2026"
MANIFEST_PATH = PROJECT_ROOT / "canonical_run_manifest.json"
RESULTS_DIR = PROJECT_ROOT / "data" / "results" / DATASET
PROP_TOLERANCE = 1e-6
PACKAGES = ["pandas", "numpy", "scipy", "matplotlib", "seaborn", "conllu", "tabulate"]


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_targets() -> list[Path]:
    raw = PROJECT_ROOT / "data" / "raw" / DATASET
    targets = [
        PROJECT_ROOT / "scripts" / "run_stark_svo_analysis.py",
        PROJECT_ROOT / "scripts" / "validate_direct_conllu_svo.py",
        PROJECT_ROOT / "requirements.txt",
        raw / "metadata.csv",
        *sorted(raw.glob("*.conllu")),
    ]
    return targets


def collect_hashes() -> dict[str, str | None]:
    return {str(p.relative_to(PROJECT_ROOT)): sha256(p) for p in hash_targets()}


def collect_metrics() -> dict:
    summary = pd.read_csv(RESULTS_DIR / "stark_svo_summary.tsv", sep="\t")
    svo = {}
    for _, r in summary.iterrows():
        svo[f"{r['language']}|{r['genre']}"] = {
            "svo_count": int(r["svo_count"]),
            "total": int(r["total"]),
            "svo_proportion": round(float(r["svo_proportion"]), 6),
        }
    validation = {}
    vpath = RESULTS_DIR / "stark_vs_direct_validation.tsv"
    if vpath.exists():
        v = pd.read_csv(vpath, sep="\t")
        validation = {
            "max_count_diff": int(v["count_difference_stark_minus_direct"].abs().max()),
            "max_proportion_diff": round(float(v["proportion_difference_stark_minus_direct"].abs().max()), 6),
        }
    return {"svo_by_language_genre": svo, "validation": validation}


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
        "query": "upos=VERB >nsubj upos=NOUN >obj upos=NOUN",
        "environment": environment(),
        "metric_tolerance": PROP_TOLERANCE,
        "expected_metrics": collect_metrics(),
        "file_hashes": collect_hashes(),
    }


def verify(manifest: dict) -> int:
    problems = []
    # hashes
    current = collect_hashes()
    for name, expected in manifest["file_hashes"].items():
        now = current.get(name)
        if now is None:
            problems.append(f"MISSING input: {name}")
        elif now != expected:
            problems.append(f"CHANGED input: {name}")
    # metrics
    now_metrics = collect_metrics()
    exp = manifest["expected_metrics"]["svo_by_language_genre"]
    now = now_metrics["svo_by_language_genre"]
    for key, e in exp.items():
        n = now.get(key)
        if n is None:
            problems.append(f"MISSING metric: {key}")
            continue
        if n["svo_count"] != e["svo_count"] or n["total"] != e["total"]:
            problems.append(f"COUNT mismatch {key}: {n} vs {e}")
        elif abs(n["svo_proportion"] - e["svo_proportion"]) > PROP_TOLERANCE:
            problems.append(f"PROPORTION mismatch {key}: {n['svo_proportion']} vs {e['svo_proportion']}")

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
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return verify(manifest)

    MANIFEST_PATH.write_text(json.dumps(build_manifest(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
