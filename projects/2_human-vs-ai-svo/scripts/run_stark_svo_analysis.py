#!/usr/bin/env python3
"""Run the official STARK-based Human-vs-AI SVO analysis."""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.spatial.distance import jensenshannon
from scipy.stats import chi2_contingency, entropy

from validate_direct_conllu_svo import (
    GENRE_ORDER,
    WORD_ORDERS,
    InputFile,
    build_proportions as build_direct_proportions,
    extract_instances,
    read_metadata_csv,
    validate_inputs,
)


# Project root = the parent of this scripts/ directory. Defaults resolve from
# here so the pipeline runs identically from any working directory (and on a
# remote machine after a plain `git clone`).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET = "nh_svo_jun_2026"
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "raw" / DATASET
DEFAULT_METADATA_CSV = DEFAULT_INPUT_DIR / "metadata.csv"
DEFAULT_INTERIM_DIR = PROJECT_ROOT / "data" / "interim" / DATASET / "stark_svo_noun"
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "data" / "results" / DATASET
DEFAULT_REPORT = PROJECT_ROOT / "docs" / f"{DATASET}_results.md"
# STARK lives outside this repo; override per-machine with the STARK_PY env var.
# The fallback uses the current user's home dir (~/Projekti/STARK/stark.py).
DEFAULT_STARK_PY = Path(os.environ.get("STARK_PY", str(Path.home() / "Projekti" / "STARK" / "stark.py")))


STARK_QUERY = "upos=VERB >nsubj upos=NOUN >obj upos=NOUN"
STARK_SETTINGS = {
    "node_type": "form",
    "labeled": "yes",
    "label_subtypes": "no",
    "fixed": "yes",
    "complete": "no",
    "greedy_counter": "no",
    "processing_size": "3",
    "node_info": "yes",
    "head_info": "yes",
    "grew_match": "no",
    "depsearch": "no",
    "association_measures": "no",
    "complexity_measures": "no",
    "example": "no",
}
STARK_REQUIRED_COLUMNS = {
    "Tree",
    "Node A-form",
    "Node B-form",
    "Node C-form",
    "Absolute frequency",
    "Relative frequency",
    "Order",
    "Number of nodes",
    "Head node",
}


@dataclass(frozen=True)
class StarkJob:
    input_file: InputFile
    stem: str
    output_tsv: Path
    log_file: Path
    runtime_file: Path
    internal_saves_dir: Path
    chunks_dir: Path
    chunk_tsv_dir: Path
    chunk_log_dir: Path
    chunk_runtime_dir: Path


def safe_stem(path: Path) -> str:
    return path.name.removesuffix(".conllu").removesuffix(".conll")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def make_jobs(inputs: Iterable[InputFile], interim_dir: Path) -> list[StarkJob]:
    output_dir = interim_dir / "tsv"
    logs_dir = interim_dir / "logs"
    internal_saves_dir = interim_dir / "internal_saves"
    runtimes_dir = interim_dir / "runtime"
    chunks_dir = interim_dir / "chunks"
    chunk_tsv_dir = interim_dir / "chunk_tsv"
    chunk_log_dir = interim_dir / "chunk_logs"
    chunk_runtime_dir = interim_dir / "chunk_runtime"
    for path in [
        output_dir,
        logs_dir,
        internal_saves_dir,
        runtimes_dir,
        chunks_dir,
        chunk_tsv_dir,
        chunk_log_dir,
        chunk_runtime_dir,
    ]:
        ensure_dir(path)

    jobs = []
    for input_file in inputs:
        stem = safe_stem(input_file.path)
        jobs.append(
            StarkJob(
                input_file=input_file,
                stem=stem,
                output_tsv=output_dir / f"{stem}.tsv",
                log_file=logs_dir / f"{stem}.log",
                runtime_file=runtimes_dir / f"{stem}.json",
                internal_saves_dir=internal_saves_dir / stem,
                chunks_dir=chunks_dir / stem,
                chunk_tsv_dir=chunk_tsv_dir / stem,
                chunk_log_dir=chunk_log_dir / stem,
                chunk_runtime_dir=chunk_runtime_dir / stem,
            )
        )
    return jobs


def stark_command(
    stark_py: Path,
    input_path: Path,
    output_tsv: Path,
    internal_saves_dir: Path,
) -> list[str]:
    return [
        sys.executable,
        str(stark_py),
        "--input",
        str(input_path),
        "--output",
        str(output_tsv),
        "--internal_saves",
        str(internal_saves_dir),
        "--query",
        STARK_QUERY,
        "--node_type",
        STARK_SETTINGS["node_type"],
        "--labeled",
        STARK_SETTINGS["labeled"],
        "--label_subtypes",
        STARK_SETTINGS["label_subtypes"],
        "--fixed",
        STARK_SETTINGS["fixed"],
        "--complete",
        STARK_SETTINGS["complete"],
        "--greedy_counter",
        STARK_SETTINGS["greedy_counter"],
        "--processing_size",
        STARK_SETTINGS["processing_size"],
        "--node_info",
        STARK_SETTINGS["node_info"],
        "--head_info",
        STARK_SETTINGS["head_info"],
        "--grew_match",
        STARK_SETTINGS["grew_match"],
        "--depsearch",
        STARK_SETTINGS["depsearch"],
        "--association_measures",
        STARK_SETTINGS["association_measures"],
        "--complexity_measures",
        STARK_SETTINGS["complexity_measures"],
        "--example",
        STARK_SETTINGS["example"],
    ]


def run_single_stark(
    stark_py: Path,
    input_path: Path,
    output_tsv: Path,
    log_file: Path,
    runtime_file: Path,
    internal_saves_dir: Path,
    stem: str,
    language: str,
    genre: str,
    force: bool,
) -> dict[str, object]:
    if output_tsv.exists() and output_tsv.stat().st_size > 0 and not force:
        return {
            "stem": stem,
            "status": "skipped_existing",
            "output_tsv": str(output_tsv),
            "seconds": 0.0,
        }

    ensure_dir(internal_saves_dir)
    command = stark_command(stark_py, input_path, output_tsv, internal_saves_dir)
    started = time.monotonic()
    started_at = datetime.now().isoformat(timespec="seconds")
    with log_file.open("w", encoding="utf-8") as log_handle:
        log_handle.write("$ " + " ".join(command) + "\n\n")
        log_handle.flush()
        completed = subprocess.run(
            command,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    seconds = time.monotonic() - started
    record = {
        "stem": stem,
        "language": language,
        "genre": genre,
        "input": str(input_path),
        "output_tsv": str(output_tsv),
        "log_file": str(log_file),
        "command": command,
        "started_at": started_at,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "seconds": seconds,
        "returncode": completed.returncode,
        "status": "ok" if completed.returncode == 0 else "failed",
    }
    runtime_file.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"STARK failed for {stem}; see {log_file}")
    return record


def split_conllu_by_sentence(input_path: Path, chunk_dir: Path, max_bytes: int, force: bool) -> list[Path]:
    ensure_dir(chunk_dir)
    existing = sorted(chunk_dir.glob("chunk_*.conllu"))
    if existing and not force:
        return existing

    current_lines: list[str] = []
    current_size = 0
    chunk_index = 1
    chunk_paths: list[Path] = []

    def write_chunk(lines: list[str], index: int) -> Path:
        chunk_path = chunk_dir / f"chunk_{index:04d}.conllu"
        chunk_path.write_text("".join(lines), encoding="utf-8")
        return chunk_path

    with input_path.open("r", encoding="utf-8-sig") as handle:
        sentence_lines: list[str] = []
        sentence_size = 0
        for line in handle:
            sentence_lines.append(line)
            sentence_size += len(line.encode("utf-8"))
            if line.strip():
                continue

            if current_lines and current_size + sentence_size > max_bytes:
                chunk_paths.append(write_chunk(current_lines, chunk_index))
                chunk_index += 1
                current_lines = []
                current_size = 0
            current_lines.extend(sentence_lines)
            current_size += sentence_size
            sentence_lines = []
            sentence_size = 0

        if sentence_lines:
            if current_lines and current_size + sentence_size > max_bytes:
                chunk_paths.append(write_chunk(current_lines, chunk_index))
                chunk_index += 1
                current_lines = []
            current_lines.extend(sentence_lines)

    if current_lines:
        chunk_paths.append(write_chunk(current_lines, chunk_index))
    return chunk_paths


def merge_chunk_tsvs(chunk_tsvs: list[Path], output_tsv: Path) -> None:
    frames = [pd.read_csv(path, sep="\t") for path in chunk_tsvs]
    if not frames:
        raise ValueError(f"No chunk TSVs to merge for {output_tsv}")
    merged_input = pd.concat(frames, ignore_index=True)
    if merged_input.empty:
        merged_input.to_csv(output_tsv, sep="\t", index=False)
        return

    group_cols = [col for col in merged_input.columns if col not in {"Absolute frequency", "Relative frequency"}]
    merged = (
        merged_input.groupby(group_cols, dropna=False, as_index=False)["Absolute frequency"]
        .sum()
        .sort_values("Absolute frequency", ascending=False)
    )
    if "Relative frequency" in merged_input.columns:
        insert_at = list(merged_input.columns).index("Relative frequency")
        merged.insert(insert_at, "Relative frequency", "")
    merged = merged[[col for col in merged_input.columns if col in merged.columns]]
    merged.to_csv(output_tsv, sep="\t", index=False)


def run_stark_job(
    stark_py: Path,
    job: StarkJob,
    force: bool,
    chunk_threshold_bytes: int,
    chunk_size_bytes: int,
) -> dict[str, object]:
    if job.output_tsv.exists() and job.output_tsv.stat().st_size > 0 and not force:
        return {
            "stem": job.stem,
            "status": "skipped_existing",
            "output_tsv": str(job.output_tsv),
            "seconds": 0.0,
        }

    input_size = job.input_file.path.stat().st_size
    if input_size <= chunk_threshold_bytes:
        return run_single_stark(
            stark_py=stark_py,
            input_path=job.input_file.path,
            output_tsv=job.output_tsv,
            log_file=job.log_file,
            runtime_file=job.runtime_file,
            internal_saves_dir=job.internal_saves_dir,
            stem=job.stem,
            language=job.input_file.language,
            genre=job.input_file.genre,
            force=force,
        )

    ensure_dir(job.chunk_tsv_dir)
    ensure_dir(job.chunk_log_dir)
    ensure_dir(job.chunk_runtime_dir)
    chunk_paths = split_conllu_by_sentence(job.input_file.path, job.chunks_dir, chunk_size_bytes, force)
    chunk_records = []
    chunk_tsvs = []
    started = time.monotonic()
    for index, chunk_path in enumerate(chunk_paths, start=1):
        chunk_stem = f"{job.stem}.chunk_{index:04d}"
        chunk_tsv = job.chunk_tsv_dir / f"chunk_{index:04d}.tsv"
        chunk_tsvs.append(chunk_tsv)
        chunk_records.append(
            run_single_stark(
                stark_py=stark_py,
                input_path=chunk_path,
                output_tsv=chunk_tsv,
                log_file=job.chunk_log_dir / f"chunk_{index:04d}.log",
                runtime_file=job.chunk_runtime_dir / f"chunk_{index:04d}.json",
                internal_saves_dir=job.internal_saves_dir / f"chunk_{index:04d}",
                stem=chunk_stem,
                language=job.input_file.language,
                genre=job.input_file.genre,
                force=force,
            )
        )
    merge_chunk_tsvs(chunk_tsvs, job.output_tsv)
    seconds = time.monotonic() - started
    record = {
        "stem": job.stem,
        "language": job.input_file.language,
        "genre": job.input_file.genre,
        "input": str(job.input_file.path),
        "output_tsv": str(job.output_tsv),
        "log_file": str(job.log_file),
        "seconds": seconds,
        "status": "ok_chunked",
        "input_size_bytes": input_size,
        "chunk_threshold_bytes": chunk_threshold_bytes,
        "chunk_size_bytes": chunk_size_bytes,
        "chunks": chunk_records,
    }
    job.log_file.write_text(
        "\n".join(
            [
                f"Chunked STARK run for {job.input_file.path}",
                f"Chunks: {len(chunk_paths)}",
                f"Merged output: {job.output_tsv}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    job.runtime_file.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record


def split_tree_elements(tree: str) -> list[str]:
    elements = str(tree).split()
    result = []
    i = 0
    while i < len(elements):
        element = elements[i]
        if element.startswith("<") and result:
            result[-1] = f"{result[-1]} {element}"
        elif element.startswith(">") and i + 1 < len(elements):
            result.append(f"{element} {elements[i + 1]}")
            i += 1
        else:
            result.append(element)
        i += 1
    return result


def classify_tree_element(element: str) -> str:
    if "<obj" in element or ">obj" in element:
        if "<nsubj" in element or ">nsubj" in element:
            return "S"
        return "O"
    if "<nsubj" in element or ">nsubj" in element:
        return "S"
    return "V"


def classify_tree(tree: str) -> str:
    parts = split_tree_elements(tree)
    if len(parts) != 3:
        return ""
    pattern = "".join(classify_tree_element(part) for part in parts)
    return pattern if pattern in WORD_ORDERS else ""


def load_stark_output(job: StarkJob) -> pd.DataFrame:
    df = pd.read_csv(job.output_tsv, sep="\t")
    missing = STARK_REQUIRED_COLUMNS - set(df.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"{job.output_tsv} is missing STARK column(s): {missing_text}")
    df["language"] = job.input_file.language
    df["genre"] = job.input_file.genre
    df["source_file"] = job.stem
    df["pattern"] = df["Tree"].apply(classify_tree)
    invalid = df[df["pattern"] == ""]
    if not invalid.empty:
        print(
            f"  WARNING: {job.stem}: dropping {len(invalid)}/{len(df)} unclassifiable tree rows"
            " (Unicode artifacts in Arabic/Urdu/CJK text)",
            flush=True,
        )
        df = df[df["pattern"] != ""].copy()
    return df


def build_stark_outputs(jobs: list[StarkJob], results_dir: Path) -> dict[str, pd.DataFrame]:
    frames = [load_stark_output(job) for job in jobs]
    stark_trees = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    stark_trees = stark_trees.rename(columns={"Absolute frequency": "absolute_frequency"})
    stark_trees["absolute_frequency"] = stark_trees["absolute_frequency"].astype(int)

    counts = (
        stark_trees.groupby(["language", "genre", "pattern"], as_index=False)["absolute_frequency"]
        .sum()
        .rename(columns={"absolute_frequency": "count"})
    )
    language_order = sorted({job.input_file.language for job in jobs})
    all_keys = pd.MultiIndex.from_product(
        [
            language_order,
            GENRE_ORDER,
            WORD_ORDERS,
        ],
        names=["language", "genre", "pattern"],
    )
    counts = counts.set_index(["language", "genre", "pattern"]).reindex(all_keys, fill_value=0).reset_index()
    counts["total"] = counts.groupby(["language", "genre"])["count"].transform("sum")
    counts["proportion"] = counts.apply(
        lambda row: row["count"] / row["total"] if row["total"] else 0.0,
        axis=1,
    )

    differences = build_differences(counts)
    summary = build_summary(counts)
    comparisons = build_comparisons(counts)

    ensure_dir(results_dir)
    pd.DataFrame(
        [
            {
                "path": str(job.input_file.path),
                "language": job.input_file.language,
                "genre": job.input_file.genre,
                "stark_tsv": str(job.output_tsv),
                "stark_log": str(job.log_file),
            }
            for job in jobs
        ]
    ).to_csv(results_dir / "input_files.csv", index=False)
    stark_trees.to_csv(results_dir / "stark_svo_tree_types.tsv", sep="\t", index=False)
    counts.to_csv(results_dir / "stark_svo_pattern_counts.tsv", sep="\t", index=False)
    differences.to_csv(results_dir / "stark_svo_ai_minus_human.tsv", sep="\t", index=False)
    summary.to_csv(results_dir / "stark_svo_summary.tsv", sep="\t", index=False)
    comparisons.to_csv(results_dir / "stark_svo_comparisons.tsv", sep="\t", index=False)

    plot_proportions(counts, results_dir / "stark_svo_proportions_heatmap.png")
    plot_differences(differences, results_dir / "stark_svo_ai_minus_human_heatmap.png")
    plot_svo_summary(summary, results_dir / "stark_svo_share_by_language.png")

    return {
        "tree_types": stark_trees,
        "counts": counts,
        "differences": differences,
        "summary": summary,
        "comparisons": comparisons,
    }


def build_differences(counts: pd.DataFrame) -> pd.DataFrame:
    prop_pivot = counts.pivot_table(
        index=["language", "pattern"], columns="genre", values="proportion", fill_value=0
    )
    count_pivot = counts.pivot_table(
        index=["language", "pattern"], columns="genre", values="count", fill_value=0
    )
    total_pivot = counts.pivot_table(
        index=["language", "pattern"], columns="genre", values="total", fill_value=0
    )
    rows = []
    for (language, pattern), prop_row in prop_pivot.iterrows():
        human_prop = float(prop_row.get("Human", 0.0))
        ai_prop = float(prop_row.get("AI", 0.0))
        rows.append(
            {
                "language": language,
                "pattern": pattern,
                "human_count": int(count_pivot.loc[(language, pattern)].get("Human", 0)),
                "ai_count": int(count_pivot.loc[(language, pattern)].get("AI", 0)),
                "human_total": int(total_pivot.loc[(language, pattern)].get("Human", 0)),
                "ai_total": int(total_pivot.loc[(language, pattern)].get("AI", 0)),
                "human_proportion": human_prop,
                "ai_proportion": ai_prop,
                "ai_minus_human": ai_prop - human_prop,
            }
        )
    return pd.DataFrame(rows)


def build_summary(counts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (language, genre), group in counts.groupby(["language", "genre"]):
        by_pattern = group.set_index("pattern").reindex(WORD_ORDERS, fill_value=0)
        total = int(by_pattern["count"].sum())
        proportions = by_pattern["proportion"].to_numpy()
        svo_count = int(by_pattern.loc["SVO", "count"])
        svo_proportion = float(by_pattern.loc["SVO", "proportion"]) if total else 0.0
        rows.append(
            {
                "language": language,
                "genre": genre,
                "total": total,
                "svo_count": svo_count,
                "svo_proportion": svo_proportion,
                "non_svo_proportion": 1 - svo_proportion if total else 0.0,
                "entropy": float(entropy(proportions)) if total else 0.0,
            }
        )
    return pd.DataFrame(rows)


def build_comparisons(counts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for language, group in counts.groupby("language"):
        by_genre = {
            genre: group[group["genre"] == genre].set_index("pattern").reindex(WORD_ORDERS, fill_value=0)
            for genre in GENRE_ORDER
        }
        if any(int(by_genre[genre]["count"].sum()) == 0 for genre in GENRE_ORDER):
            continue
        human_props = by_genre["Human"]["proportion"].to_numpy()
        ai_props = by_genre["AI"]["proportion"].to_numpy()
        observed = pd.DataFrame(
            {
                "Human": by_genre["Human"]["count"].astype(int),
                "AI": by_genre["AI"]["count"].astype(int),
            },
            index=WORD_ORDERS,
        )
        observed = observed[observed.sum(axis=1) > 0]
        chi2, p_value, dof, _ = chi2_contingency(observed.to_numpy())
        rows.append(
            {
                "language": language,
                "human_total": int(by_genre["Human"]["count"].sum()),
                "ai_total": int(by_genre["AI"]["count"].sum()),
                "jensen_shannon_distance": float(jensenshannon(human_props, ai_props)),
                "human_entropy": float(entropy(human_props)),
                "ai_entropy": float(entropy(ai_props)),
                "chi2": float(chi2),
                "chi2_dof": int(dof),
                "chi2_p_value": float(p_value),
            }
        )
    return pd.DataFrame(rows)


def plot_proportions(counts: pd.DataFrame, output_path: Path) -> None:
    heatmap_df = counts.copy()
    heatmap_df["column"] = heatmap_df.apply(
        lambda row: f"{row['language']}\n{row['genre']}\n(n={int(row['total'])})",
        axis=1,
    )
    pivot = heatmap_df.pivot(index="pattern", columns="column", values="proportion").reindex(WORD_ORDERS)
    plt.figure(figsize=(max(9, 0.8 * len(pivot.columns)), 5.0))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".1%",
        cmap=sns.light_palette("#2c7fb8", as_cmap=True),
        vmin=0,
        vmax=1,
        cbar_kws={"label": "Proportion"},
    )
    plt.xlabel("")
    plt.ylabel("Word Order")
    plt.title("STARK S/V/O Word Order Proportions")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_differences(differences: pd.DataFrame, output_path: Path) -> None:
    pivot = differences.pivot(index="pattern", columns="language", values="ai_minus_human").reindex(WORD_ORDERS)
    max_abs = float(pivot.abs().max().max()) if not pivot.empty else 0.0
    max_abs = max(max_abs, 0.01)
    pivot_pp = pivot * 100
    plt.figure(figsize=(max(7, 0.8 * len(pivot.columns)), 5.0))
    sns.heatmap(
        pivot_pp,
        annot=True,
        fmt="+.1f",
        cmap="vlag",
        center=0,
        vmin=-(max_abs * 100),
        vmax=max_abs * 100,
        cbar_kws={"label": "AI - Human (percentage points)"},
    )
    plt.xlabel("")
    plt.ylabel("Word Order")
    plt.title("STARK S/V/O Differences (AI - Human, pp)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_svo_summary(summary: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(10, 5))
    plot_df = summary.copy()
    sns.barplot(data=plot_df, x="language", y="svo_proportion", hue="genre", hue_order=GENRE_ORDER)
    plt.ylabel("SVO proportion")
    plt.xlabel("")
    plt.ylim(0, 1)
    plt.title("STARK SVO Share by Language and Genre")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def run_direct_validation(inputs: list[InputFile], results_dir: Path) -> pd.DataFrame:
    rows = []
    instances = []
    for input_file in inputs:
        file_instances = extract_instances(
            input_file=input_file,
            predicate_upos={"VERB"},
            argument_upos={"NOUN"},
            require_finite=False,
            include_deprel_subtypes=False,
            skip_malformed_sentences=True,
        )
        instances.extend(file_instances)
        rows.append(
            {
                "language": input_file.language,
                "genre": input_file.genre,
                "file": input_file.path.name,
                "direct_instances": len(file_instances),
            }
        )

    validation_dir = results_dir / "direct_validation"
    ensure_dir(validation_dir)
    instances_df = pd.DataFrame(instances)
    if instances_df.empty:
        raise ValueError("Direct validation found no S/V/O instances.")
    instances_df.to_csv(validation_dir / "direct_svo_instances.tsv", sep="\t", index=False)
    direct_counts = build_direct_proportions(instances_df)
    direct_counts.to_csv(validation_dir / "direct_svo_pattern_counts.tsv", sep="\t", index=False)
    pd.DataFrame(rows).to_csv(validation_dir / "direct_file_totals.tsv", sep="\t", index=False)
    return direct_counts


def compare_validation(stark_counts: pd.DataFrame, direct_counts: pd.DataFrame, results_dir: Path) -> pd.DataFrame:
    stark = stark_counts.rename(columns={"count": "stark_count", "proportion": "stark_proportion"})[
        ["language", "genre", "pattern", "stark_count", "stark_proportion"]
    ]
    direct = direct_counts.rename(columns={"count": "direct_count", "proportion": "direct_proportion"})[
        ["language", "genre", "pattern", "direct_count", "direct_proportion"]
    ]
    comparison = stark.merge(direct, on=["language", "genre", "pattern"], how="outer").fillna(0)
    comparison["count_difference_stark_minus_direct"] = (
        comparison["stark_count"].astype(int) - comparison["direct_count"].astype(int)
    )
    comparison["proportion_difference_stark_minus_direct"] = (
        comparison["stark_proportion"] - comparison["direct_proportion"]
    )
    comparison.to_csv(results_dir / "stark_vs_direct_validation.tsv", sep="\t", index=False)
    return comparison


def pct(value: float) -> str:
    return f"{value:.1%}"


def signed_pp(value: float) -> str:
    return f"{value * 100:+.1f} pp"


def write_report(
    results_dir: Path,
    docs_path: Path,
    summary: pd.DataFrame,
    differences: pd.DataFrame,
    comparisons: pd.DataFrame,
    validation: pd.DataFrame,
    runtime_records: list[dict[str, object]],
) -> None:
    svo = differences[differences["pattern"] == "SVO"].copy()
    svo = svo.sort_values("ai_minus_human")
    largest_drop = svo.iloc[0]
    largest_rise = svo.iloc[-1]

    non_svo = differences[differences["pattern"] != "SVO"].copy()
    non_svo["abs_diff"] = non_svo["ai_minus_human"].abs()
    largest_non_svo = non_svo.sort_values("abs_diff", ascending=False).head(10)

    # When validation is skipped these columns hold NaN; show "n/a" instead of crashing.
    count_diff_max = validation["count_difference_stark_minus_direct"].abs().max()
    prop_diff_max = validation["proportion_difference_stark_minus_direct"].abs().max()
    if pd.notna(count_diff_max):
        validation_count_display = str(int(count_diff_max))
        validation_prop_display = f"{float(prop_diff_max) * 100:.2f} pp"
    else:
        validation_count_display = "n/a (validation skipped)"
        validation_prop_display = "n/a (validation skipped)"

    summary_table = summary.sort_values(["language", "genre"])[
        ["language", "genre", "total", "svo_count", "svo_proportion", "entropy"]
    ].to_markdown(index=False, floatfmt=".4f")
    svo_table = svo[
        [
            "language",
            "human_count",
            "ai_count",
            "human_proportion",
            "ai_proportion",
            "ai_minus_human",
        ]
    ].to_markdown(index=False, floatfmt=".4f")
    non_svo_table = largest_non_svo[
        ["language", "pattern", "human_proportion", "ai_proportion", "ai_minus_human"]
    ].to_markdown(index=False, floatfmt=".4f")
    comparison_table = comparisons.sort_values("jensen_shannon_distance", ascending=False)[
        ["language", "human_total", "ai_total", "jensen_shannon_distance", "chi2_p_value"]
    ].to_markdown(index=False, floatfmt=".4g")

    text = f"""# SVO Word Order in Human vs AI-Generated Text

## Method

This analysis uses STARK as the official extraction step. For every file listed in `projects/2_human-vs-ai-svo/data/raw/nh_svo_jun_2026/metadata.csv`, the same query pattern was applied:

```text
{STARK_QUERY}
```

STARK outputs tree types and their frequencies. Aggregation therefore does not count rows; instead, for each pattern we sum the `Absolute frequency` column. Word orders are classified as `SVO`, `SOV`, `VSO`, `VOS`, `OSV`, and `OVS`.

## Headline result

The largest drop in the SVO share of AI relative to human text is in **{largest_drop['language']}** ({signed_pp(float(largest_drop['ai_minus_human']))}). The largest rise in the SVO share of AI is in **{largest_rise['language']}** ({signed_pp(float(largest_rise['ai_minus_human']))}).

These are differences between proportions, so prose and figures report them as **percentage points (pp)**.

| Summary | Value |
| --- | --- |
| Number of languages | {summary['language'].nunique()} |
| Genres / classes | Human, AI |
| Max STARK − direct-parser difference (count) | {validation_count_display} |
| Max STARK − direct-parser difference (proportion) | {validation_prop_display} |

## SVO shares

{svo_table}

## Summary by language and variety

{summary_table}

## Largest shifts in non-SVO patterns

{non_svo_table}

## Distances between distributions

{comparison_table}

## Output files

- `projects/2_human-vs-ai-svo/data/results/nh_svo_jun_2026/stark_svo_pattern_counts.tsv`
- `projects/2_human-vs-ai-svo/data/results/nh_svo_jun_2026/stark_svo_ai_minus_human.tsv`
- `projects/2_human-vs-ai-svo/data/results/nh_svo_jun_2026/stark_svo_summary.tsv`
- `projects/2_human-vs-ai-svo/data/results/nh_svo_jun_2026/stark_svo_comparisons.tsv`
- `projects/2_human-vs-ai-svo/data/results/nh_svo_jun_2026/stark_vs_direct_validation.tsv`
- `projects/2_human-vs-ai-svo/data/results/nh_svo_jun_2026/stark_svo_proportions_heatmap.png`
- `projects/2_human-vs-ai-svo/data/results/nh_svo_jun_2026/stark_svo_ai_minus_human_heatmap.png`
- `projects/2_human-vs-ai-svo/data/results/nh_svo_jun_2026/stark_svo_share_by_language.png`

## Notes

The results compare AI and human text within each language–source pair. The differences are therefore not purely linguistic; they also depend on the source, the model, and the generation method. The direct parser is used only for validation; the official results are based on the STARK output.
"""
    docs_path.write_text(text, encoding="utf-8")


def write_analysis_config(
    results_dir: Path,
    interim_dir: Path,
    metadata_csv: Path,
    input_dir: Path,
    stark_py: Path,
    chunk_threshold_mb: float,
    chunk_size_mb: float,
    runtime_records: list[dict[str, object]],
) -> None:
    config = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "official_pipeline": "STARK",
        "stark_py": str(stark_py),
        "metadata_csv": str(metadata_csv),
        "input_dir": str(input_dir),
        "interim_dir": str(interim_dir),
        "query": STARK_QUERY,
        "settings": STARK_SETTINGS,
        "chunk_threshold_mb": chunk_threshold_mb,
        "chunk_size_mb": chunk_size_mb,
        "aggregation": "sum STARK Absolute frequency by language, genre, pattern",
        "runtime_records": runtime_records,
    }
    (results_dir / "analysis_config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument(
        "--metadata-csv",
        type=Path,
        default=DEFAULT_METADATA_CSV,
    )
    parser.add_argument(
        "--stark-py",
        type=Path,
        default=DEFAULT_STARK_PY,
        help="Path to STARK's stark.py (or set the STARK_PY env var).",
    )
    parser.add_argument(
        "--interim-dir",
        type=Path,
        default=DEFAULT_INTERIM_DIR,
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
    )
    parser.add_argument("--force", action="store_true", help="Rerun STARK even if TSV output already exists.")
    parser.add_argument("--stark-only", action="store_true", help="Run STARK and stop before post-processing.")
    parser.add_argument("--process-only", action="store_true", help="Skip STARK and process existing TSV files.")
    parser.add_argument("--skip-validation", action="store_true", help="Skip direct parser validation.")
    parser.add_argument(
        "--chunk-threshold-mb",
        type=float,
        default=60.0,
        help="Split input files larger than this size before running STARK "
        "(60 MB avoids the out-of-memory kills seen on ~90 MB+ files).",
    )
    parser.add_argument(
        "--chunk-size-mb",
        type=float,
        default=50.0,
        help="Maximum sentence-safe chunk size for large CoNLL-U files.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.stark_py.exists():
        raise SystemExit(f"STARK script not found: {args.stark_py}")
    input_dir = args.input_dir.resolve()
    metadata_csv = args.metadata_csv.resolve()
    inputs = read_metadata_csv(metadata_csv, input_dir)
    validate_inputs(inputs)
    jobs = make_jobs(inputs, args.interim_dir)
    chunk_threshold_bytes = int(args.chunk_threshold_mb * 1024 * 1024)
    chunk_size_bytes = int(args.chunk_size_mb * 1024 * 1024)

    runtime_records = []
    if not args.process_only:
        for index, job in enumerate(jobs, start=1):
            print(f"[{index}/{len(jobs)}] STARK {job.stem}", flush=True)
            record = run_stark_job(
                args.stark_py,
                job,
                args.force,
                chunk_threshold_bytes=chunk_threshold_bytes,
                chunk_size_bytes=chunk_size_bytes,
            )
            runtime_records.append(record)
            print(f"  {record['status']} in {float(record['seconds']):.1f}s", flush=True)

    if args.stark_only:
        return 0

    missing_outputs = [str(job.output_tsv) for job in jobs if not job.output_tsv.exists()]
    if missing_outputs:
        raise SystemExit("Missing STARK output(s):\n" + "\n".join(missing_outputs))

    outputs = build_stark_outputs(jobs, args.results_dir)
    direct_counts = None
    validation = pd.DataFrame()
    if not args.skip_validation:
        print("Running direct CoNLL-U validation...", flush=True)
        direct_counts = run_direct_validation(inputs, args.results_dir)
        validation = compare_validation(outputs["counts"], direct_counts, args.results_dir)
    else:
        validation = pd.DataFrame(
            {
                "count_difference_stark_minus_direct": [math.nan],
                "proportion_difference_stark_minus_direct": [math.nan],
            }
        )

    if not runtime_records:
        runtime_records = [
            json.loads(job.runtime_file.read_text(encoding="utf-8"))
            for job in jobs
            if job.runtime_file.exists()
        ]
    write_analysis_config(
        args.results_dir,
        args.interim_dir,
        metadata_csv,
        input_dir,
        args.stark_py,
        args.chunk_threshold_mb,
        args.chunk_size_mb,
        runtime_records,
    )
    write_report(
        results_dir=args.results_dir,
        docs_path=args.report,
        summary=outputs["summary"],
        differences=outputs["differences"],
        comparisons=outputs["comparisons"],
        validation=validation,
        runtime_records=runtime_records,
    )
    print(f"Results written to {args.results_dir}")
    print(f"Report written to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
