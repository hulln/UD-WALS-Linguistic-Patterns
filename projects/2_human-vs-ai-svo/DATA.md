# Project 2 — data inventory

See the repo-wide index in [`../../DATA.md`](../../DATA.md). Tracked = pushed to
git; gitignored = kept locally only. Dataset key: `nh_svo_jun_2026`.

## Raw corpora — `data/raw/nh_svo_jun_2026/` 

16 CoNLL-U files: a **Human** and an **AI** corpus for each of 8 languages
(Arabic, Bulgarian, Chinese, English, Indonesian, Russian, Slovenian, Urdu),
derived from human-vs-AI text datasets.

| Item | What | In git? |
| --- | --- | --- |
| `*.conllu` (16) | the corpora | gitignored (large) |
| `metadata.csv` | per-file manifest: path, language, genre, source, model | **tracked** |
| `README.md` | how the folder was assembled | tracked |

`metadata.csv` is the machine-readable manifest the pipeline reads — the
authoritative per-file list.

## STARK intermediates — `data/interim/nh_svo_jun_2026/stark_svo_noun/`

| Subfolder | What | In git? |
| --- | --- | --- |
| `tsv/` | STARK output, one TSV per corpus (the reusable extraction) | **tracked** |
| `internal_saves/`, `chunks/` | STARK cache + chunk splits (regenerable, ~2 GB) | gitignored |
| `logs/`, `runtime/`, `chunk_logs/`, `chunk_runtime/` | run logs / timings (embed machine paths) | gitignored |

## Results — `data/results/nh_svo_jun_2026/` (tracked)

| File | What |
| --- | --- |
| `stark_svo_pattern_counts.tsv` | counts + proportions, all six orders |
| `stark_svo_ai_minus_human.tsv` | per-language `AI − Human` differences |
| `stark_svo_summary.tsv` | totals, SVO share, entropy by language/variety |
| `stark_svo_comparisons.tsv` | Jensen–Shannon distance, χ² per language |
| `stark_svo_tree_types.tsv` | all STARK tree types with S/V/O labels |
| `stark_vs_direct_validation.tsv` | STARK vs direct-parser cross-check |
| `*_heatmap.png`, `*_share_by_language.png` | figures |
| `direct_validation/` | direct-parser cross-check outputs (the large per-instance dump is gitignored) |

Gitignored here (regenerable / machine-specific): `input_files.csv`,
`analysis_config.json`, `direct_validation/direct_svo_instances.tsv`.
