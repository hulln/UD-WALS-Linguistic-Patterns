#!/usr/bin/env python3
"""Validate STARK S/V/O results with a direct CoNLL-U parser.

This is not the official analysis pipeline for the June 2026 task.
Official extraction is done with STARK. This script independently finds
VERB heads with a NOUN `nsubj` dependent and a NOUN `obj` dependent,
then classifies the linear order as one of SVO, SOV, VSO, VOS, OSV, or
OVS for validation and diagnostics.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from conllu import parse
from conllu.exceptions import ParseException
from scipy.spatial.distance import jensenshannon
from scipy.stats import chi2_contingency, entropy


WORD_ORDERS = ["SVO", "SOV", "VSO", "VOS", "OSV", "OVS"]
GENRE_ORDER = ["Human", "AI"]
CONLLU_SUFFIXES = (".conllu", ".conll", ".conllu.txt")

# Defaults resolve relative to the project folder (parent of this scripts/ dir),
# matching run_stark_svo_analysis.py, so the script works from any directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET = "nh_svo_jun_2026"
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "raw" / DATASET
DEFAULT_METADATA_CSV = DEFAULT_INPUT_DIR / "metadata.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "results" / DATASET / "direct_validation"

# Multilingual match tokens for guessing genre from folder/file names when no
# metadata is given (kept intentionally multilingual, incl. Slovenian, so e.g.
# an "umetno"/"generirano" folder is recognized as AI). Genre normally comes
# from metadata.csv; these are only a fallback.
AI_TOKENS = {
    "ai",
    "artificial",
    "chatgpt",
    "generated",
    "generirano",
    "generiran",
    "gpt",
    "llm",
    "machine",
    "synthetic",
    "umetno",
    "umetni",
}
HUMAN_TOKENS = {
    "clovesko",
    "human",
    "hum",
    "original",
    "reference",
    "real",
    "source",
    "written",
    "zlato",
}
NOISE_TOKENS = {
    "conll",
    "conllu",
    "cupt",
    "data",
    "nh",
    "share",
    "svo",
    "ud",
}


@dataclass(frozen=True)
class InputFile:
    path: Path
    language: str
    genre: str


def ascii_lower(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


def split_tokens(text: str) -> list[str]:
    return [token for token in re.split(r"[^0-9A-Za-z]+", ascii_lower(text)) if token]


def normalize_genre(value: str) -> str:
    tokens = set(split_tokens(value))
    lowered = ascii_lower(value).strip()
    if lowered in {"ai", "llm"} or tokens & AI_TOKENS:
        return "AI"
    if lowered in {"human", "hum"} or tokens & HUMAN_TOKENS:
        return "Human"
    return value.strip()


def is_ai_or_human_token(token: str) -> bool:
    return token in AI_TOKENS or token in HUMAN_TOKENS


def clean_language_label(tokens: Iterable[str]) -> str:
    kept = [token for token in tokens if token not in NOISE_TOKENS and not is_ai_or_human_token(token)]
    if not kept:
        return ""
    if len(kept) == 1 and len(kept[0]) <= 3:
        return kept[0].upper()
    return " ".join(token.capitalize() for token in kept)


def infer_metadata(path: Path, input_dir: Path) -> InputFile:
    try:
        rel_path = path.relative_to(input_dir)
    except ValueError:
        rel_path = path

    all_tokens: list[str] = []
    for part in rel_path.parts:
        all_tokens.extend(split_tokens(Path(part).stem))

    genre = ""
    for token in all_tokens:
        if token in AI_TOKENS:
            genre = "AI"
            break
        if token in HUMAN_TOKENS:
            genre = "Human"
            break

    stem_tokens = split_tokens(path.stem)
    language = clean_language_label(stem_tokens)

    if not language:
        for parent in reversed(rel_path.parents):
            if str(parent) == ".":
                continue
            language = clean_language_label(split_tokens(parent.name))
            if language:
                break

    return InputFile(path=path, language=language, genre=genre)


def discover_input_files(input_dir: Path) -> list[InputFile]:
    files = [
        path
        for path in sorted(input_dir.rglob("*"))
        if path.is_file() and ascii_lower(path.name).endswith(CONLLU_SUFFIXES)
    ]
    return [infer_metadata(path, input_dir) for path in files]


def read_metadata_csv(path: Path, base_dir: Path | None) -> list[InputFile]:
    df = pd.read_csv(path)
    required = {"path", "language", "genre"}
    missing = required - set(df.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise SystemExit(f"Metadata CSV is missing required column(s): {missing_text}")

    inputs: list[InputFile] = []
    for row in df.itertuples(index=False):
        file_path = Path(getattr(row, "path"))
        if not file_path.is_absolute() and base_dir is not None:
            file_path = base_dir / file_path
        inputs.append(
            InputFile(
                path=file_path,
                language=str(getattr(row, "language")).strip(),
                genre=normalize_genre(str(getattr(row, "genre"))),
            )
        )
    return inputs


def base_deprel(deprel: str | None, include_subtypes: bool) -> str:
    if not deprel:
        return ""
    return deprel.split(":", 1)[0] if include_subtypes else deprel


def token_id_value(token_id: object) -> int | None:
    return token_id if isinstance(token_id, int) else None


def token_feats(token: dict) -> dict:
    feats = token.get("feats") or {}
    return feats if isinstance(feats, dict) else {}


def is_finite_verb(token: dict) -> bool:
    verb_form = token_feats(token).get("VerbForm")
    if isinstance(verb_form, list):
        return "Fin" in verb_form
    return verb_form == "Fin"


def token_summary(token: dict, prefix: str) -> dict[str, object]:
    return {
        f"{prefix}_id": token.get("id"),
        f"{prefix}_form": token.get("form", ""),
        f"{prefix}_lemma": token.get("lemma", ""),
        f"{prefix}_upos": token.get("upos", ""),
        f"{prefix}_deprel": token.get("deprel", ""),
    }


def iter_conllu_sentences(path: Path, skip_malformed_sentences: bool) -> Iterable:
    buffer: list[str] = []
    start_line = 1

    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                if not buffer:
                    start_line = line_number
                buffer.append(line)
                continue

            if buffer:
                block = "".join(buffer)
                try:
                    yield from parse(block)
                except ParseException as exc:
                    message = f"{path}:{start_line}: malformed CoNLL-U sentence: {exc}"
                    if skip_malformed_sentences:
                        print(f"WARNING: {message}", file=sys.stderr)
                    else:
                        raise SystemExit(message) from exc
                buffer = []

        if buffer:
            block = "".join(buffer)
            try:
                yield from parse(block)
            except ParseException as exc:
                message = f"{path}:{start_line}: malformed CoNLL-U sentence: {exc}"
                if skip_malformed_sentences:
                    print(f"WARNING: {message}", file=sys.stderr)
                else:
                    raise SystemExit(message) from exc


def matching_dependents(
    tokens: list[dict],
    head_id: int,
    deprel: str,
    upos_values: set[str],
    include_deprel_subtypes: bool,
) -> list[dict]:
    matches = []
    for token in tokens:
        if token.get("head") != head_id:
            continue
        if base_deprel(token.get("deprel"), include_deprel_subtypes) != deprel:
            continue
        if token.get("upos") not in upos_values:
            continue
        if token_id_value(token.get("id")) is None:
            continue
        matches.append(token)
    return matches


def classify_order(subject: dict, verb: dict, obj: dict) -> str:
    ordered = sorted(
        [
            (token_id_value(subject.get("id")), "S"),
            (token_id_value(verb.get("id")), "V"),
            (token_id_value(obj.get("id")), "O"),
        ],
        key=lambda item: item[0],
    )
    return "".join(label for _, label in ordered)


def extract_instances(
    input_file: InputFile,
    predicate_upos: set[str],
    argument_upos: set[str],
    require_finite: bool,
    include_deprel_subtypes: bool,
    skip_malformed_sentences: bool,
) -> list[dict[str, object]]:
    instances: list[dict[str, object]] = []

    for sentence in iter_conllu_sentences(input_file.path, skip_malformed_sentences):
        tokens = [token for token in sentence if token_id_value(token.get("id")) is not None]
        metadata = sentence.metadata or {}
        sent_id = metadata.get("sent_id", "")
        text = metadata.get("text", "")

        for verb in tokens:
            verb_id = token_id_value(verb.get("id"))
            if verb_id is None or verb.get("upos") not in predicate_upos:
                continue
            if require_finite and not is_finite_verb(verb):
                continue

            subjects = matching_dependents(
                tokens, verb_id, "nsubj", argument_upos, include_deprel_subtypes
            )
            objects = matching_dependents(
                tokens, verb_id, "obj", argument_upos, include_deprel_subtypes
            )
            for subject in subjects:
                for obj in objects:
                    row = {
                        "language": input_file.language,
                        "genre": input_file.genre,
                        "file": str(input_file.path),
                        "sent_id": sent_id,
                        "text": text,
                        "pattern": classify_order(subject, verb, obj),
                    }
                    row.update(token_summary(verb, "verb"))
                    row.update(token_summary(subject, "subject"))
                    row.update(token_summary(obj, "object"))
                    instances.append(row)

    return instances


def validate_inputs(inputs: list[InputFile]) -> None:
    if not inputs:
        raise SystemExit("No CoNLL-U files found. Use --input-dir or --metadata-csv.")

    missing_files = [str(input_file.path) for input_file in inputs if not input_file.path.exists()]
    if missing_files:
        raise SystemExit("Missing file(s):\n" + "\n".join(missing_files))

    unknown = [
        input_file
        for input_file in inputs
        if not input_file.language or input_file.genre not in set(GENRE_ORDER)
    ]
    if unknown:
        lines = [
            "Could not infer language/genre for every file.",
            "Use --metadata-csv with columns: path,language,genre.",
            "",
            "Problem files:",
        ]
        for input_file in unknown:
            language = input_file.language or "?"
            genre = input_file.genre or "?"
            lines.append(f"- {input_file.path}  language={language} genre={genre}")
        raise SystemExit("\n".join(lines))


def write_manifest(inputs: list[InputFile], output_dir: Path) -> None:
    rows = [
        {"path": str(input_file.path), "language": input_file.language, "genre": input_file.genre}
        for input_file in inputs
    ]
    pd.DataFrame(rows).to_csv(output_dir / "input_files.csv", index=False)


def build_proportions(instances_df: pd.DataFrame) -> pd.DataFrame:
    counts = Counter(
        (row.language, row.genre, row.pattern)
        for row in instances_df[["language", "genre", "pattern"]].itertuples(index=False)
    )
    languages = sorted(instances_df["language"].unique())

    rows = []
    for language in languages:
        for genre in GENRE_ORDER:
            total = sum(counts[(language, genre, pattern)] for pattern in WORD_ORDERS)
            if total == 0:
                continue
            for pattern in WORD_ORDERS:
                count = counts[(language, genre, pattern)]
                rows.append(
                    {
                        "language": language,
                        "genre": genre,
                        "pattern": pattern,
                        "count": count,
                        "total": total,
                        "proportion": count / total,
                    }
                )
    return pd.DataFrame(rows)


def build_differences(proportions_df: pd.DataFrame) -> pd.DataFrame:
    prop_pivot = proportions_df.pivot_table(
        index=["language", "pattern"], columns="genre", values="proportion", fill_value=0
    )
    count_pivot = proportions_df.pivot_table(
        index=["language", "pattern"], columns="genre", values="count", fill_value=0
    )
    total_pivot = proportions_df.pivot_table(
        index=["language", "pattern"], columns="genre", values="total", fill_value=0
    )

    rows = []
    for (language, pattern), prop_row in prop_pivot.iterrows():
        human_prop = prop_row.get("Human", 0.0)
        ai_prop = prop_row.get("AI", 0.0)
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


def build_summary(proportions_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (language, genre), group in proportions_df.groupby(["language", "genre"]):
        proportions = group.set_index("pattern").reindex(WORD_ORDERS, fill_value=0)["proportion"]
        counts = group.set_index("pattern").reindex(WORD_ORDERS, fill_value=0)["count"]
        total = int(group["total"].iloc[0])
        svo_count = int(counts.get("SVO", 0))
        svo_proportion = float(proportions.get("SVO", 0))
        rows.append(
            {
                "language": language,
                "genre": genre,
                "total": total,
                "svo_count": svo_count,
                "svo_proportion": svo_proportion,
                "non_svo_proportion": 1 - svo_proportion,
                "entropy": entropy(proportions),
            }
        )
    return pd.DataFrame(rows)


def build_comparisons(proportions_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for language, group in proportions_df.groupby("language"):
        by_genre = {
            genre: group[group["genre"] == genre]
            .set_index("pattern")
            .reindex(WORD_ORDERS, fill_value=0)
            for genre in GENRE_ORDER
        }
        if any(by_genre[genre]["total"].sum() == 0 for genre in GENRE_ORDER):
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
                "human_total": int(by_genre["Human"]["total"].iloc[0]),
                "ai_total": int(by_genre["AI"]["total"].iloc[0]),
                "jensen_shannon_distance": float(jensenshannon(human_props, ai_props)),
                "human_entropy": float(entropy(human_props)),
                "ai_entropy": float(entropy(ai_props)),
                "chi2": float(chi2),
                "chi2_dof": int(dof),
                "chi2_p_value": float(p_value),
            }
        )
    return pd.DataFrame(rows)


def plot_proportions_heatmap(proportions_df: pd.DataFrame, output_dir: Path) -> None:
    heatmap_df = proportions_df.copy()
    heatmap_df["column"] = heatmap_df.apply(
        lambda row: f"{row['language']}\n{row['genre']}\n(n={int(row['total'])})", axis=1
    )
    pivot = heatmap_df.pivot(index="pattern", columns="column", values="proportion").reindex(WORD_ORDERS)

    width = max(8, 0.8 * len(pivot.columns))
    plt.figure(figsize=(width, 4.8))
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
    plt.title("S/V/O Word Order Proportions")
    plt.tight_layout()
    plt.savefig(output_dir / "svo_proportions_heatmap.png", dpi=300)
    plt.close()


def plot_difference_heatmap(differences_df: pd.DataFrame, output_dir: Path) -> None:
    pivot = differences_df.pivot(index="pattern", columns="language", values="ai_minus_human").reindex(
        WORD_ORDERS
    )
    max_abs = float(pivot.abs().max().max()) if not pivot.empty else 0.0
    max_abs = max(max_abs, 0.01)

    width = max(6, 0.7 * len(pivot.columns))
    plt.figure(figsize=(width, 4.8))
    sns.heatmap(
        pivot,
        annot=True,
        fmt="+.1%",
        cmap="vlag",
        center=0,
        vmin=-max_abs,
        vmax=max_abs,
        cbar_kws={"label": "AI - Human"},
    )
    plt.xlabel("")
    plt.ylabel("Word Order")
    plt.title("Difference in S/V/O Proportions (AI - Human)")
    plt.tight_layout()
    plt.savefig(output_dir / "svo_ai_minus_human_heatmap.png", dpi=300)
    plt.close()


def write_outputs(
    instances: list[dict[str, object]],
    inputs: list[InputFile],
    output_dir: Path,
    config: dict[str, object],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_manifest(inputs, output_dir)

    instances_df = pd.DataFrame(instances)
    if instances_df.empty:
        raise SystemExit("No matching S/V/O instances found.")

    instances_df.to_csv(output_dir / "svo_instances.tsv", sep="\t", index=False)
    proportions_df = build_proportions(instances_df)
    differences_df = build_differences(proportions_df)
    summary_df = build_summary(proportions_df)
    comparisons_df = build_comparisons(proportions_df)

    proportions_df.to_csv(output_dir / "svo_proportions.tsv", sep="\t", index=False)
    differences_df.to_csv(output_dir / "svo_ai_minus_human.tsv", sep="\t", index=False)
    summary_df.to_csv(output_dir / "svo_summary.tsv", sep="\t", index=False)
    comparisons_df.to_csv(output_dir / "svo_comparisons.tsv", sep="\t", index=False)

    plot_proportions_heatmap(proportions_df, output_dir)
    plot_difference_heatmap(differences_df, output_dir)

    with (output_dir / "analysis_config.json").open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)

    print(f"Files analyzed: {len(inputs)}")
    print(f"Instances extracted: {len(instances_df)}")
    print(f"Results written to: {output_dir}")
    print("\nSVO summary:")
    print(summary_df.sort_values(["language", "genre"]).to_string(index=False))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract and compare NOUN-nsubj / NOUN-obj S/V/O orders from CoNLL-U files."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing CoNLL-U files.",
    )
    parser.add_argument(
        "--metadata-csv",
        type=Path,
        default=DEFAULT_METADATA_CSV,
        help="Optional CSV with columns path,language,genre. Paths may be relative to --input-dir.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for TSV, JSON, and PNG outputs.",
    )
    parser.add_argument(
        "--predicate-upos",
        nargs="+",
        default=["VERB"],
        help="UPOS tag(s) allowed for predicate heads. Default: VERB.",
    )
    parser.add_argument(
        "--argument-upos",
        nargs="+",
        default=["NOUN"],
        help="UPOS tag(s) allowed for both nsubj and obj arguments. Default: NOUN.",
    )
    parser.add_argument(
        "--require-finite",
        action="store_true",
        help="Require predicate heads to have VerbForm=Fin.",
    )
    parser.add_argument(
        "--include-deprel-subtypes",
        action="store_true",
        help="Treat nsubj:* as nsubj and obj:* as obj.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only list discovered files and inferred metadata.",
    )
    parser.add_argument(
        "--skip-malformed-sentences",
        action="store_true",
        help="Skip malformed CoNLL-U sentence blocks instead of stopping with an error.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.input_dir is None and args.metadata_csv is None:
        raise SystemExit("Provide --input-dir, --metadata-csv, or both.")

    input_dir = args.input_dir.resolve() if args.input_dir else None
    if input_dir is not None and not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    if args.metadata_csv:
        inputs = read_metadata_csv(args.metadata_csv, input_dir)
    else:
        inputs = discover_input_files(input_dir)

    validate_inputs(inputs)

    if args.dry_run:
        for input_file in inputs:
            print(f"{input_file.language}\t{input_file.genre}\t{input_file.path}")
        return 0

    predicate_upos = set(args.predicate_upos)
    argument_upos = set(args.argument_upos)
    instances = []
    for input_file in inputs:
        instances.extend(
            extract_instances(
                input_file=input_file,
                predicate_upos=predicate_upos,
                argument_upos=argument_upos,
                require_finite=args.require_finite,
                include_deprel_subtypes=args.include_deprel_subtypes,
                skip_malformed_sentences=args.skip_malformed_sentences,
            )
        )

    config = {
        "input_dir": str(input_dir) if input_dir else None,
        "metadata_csv": str(args.metadata_csv) if args.metadata_csv else None,
        "predicate_upos": sorted(predicate_upos),
        "argument_upos": sorted(argument_upos),
        "subject_deprel": "nsubj",
        "object_deprel": "obj",
        "require_finite": args.require_finite,
        "include_deprel_subtypes": args.include_deprel_subtypes,
        "skip_malformed_sentences": args.skip_malformed_sentences,
        "word_orders": WORD_ORDERS,
        "genre_difference": "AI - Human",
    }
    write_outputs(instances, inputs, args.output_dir, config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
