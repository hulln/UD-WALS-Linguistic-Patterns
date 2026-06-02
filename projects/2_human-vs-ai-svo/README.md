# Human-vs-AI S/V/O Word Order

Compares the linear order of **subject, verb, and object** in human-written vs
AI-generated text, across 8 languages, using the same extraction method as the
earlier SyntaxFest article (see project 1). For each `VERB` that governs a
nominal subject (`nsubj`) and a nominal object (`obj`), the surface order of the
three is classified as one of `SVO`, `SOV`, `VSO`, `VOS`, `OSV`, `OVS`, then
compared between the `Human` and `AI` versions of each language/source.

## Languages and sources

Arabic (wikipedia), Bulgarian (true-fake-news), English (wikipedia), Indonesian
(newspapers), Russian (ruatd), Slovenian (essays), Urdu (urdu-news), Chinese
(baike-web-qa). Each has a Human and an AI half; the manifest is
[`data/raw/nh_svo_jun_2026/metadata.csv`](data/raw/nh_svo_jun_2026/metadata.csv).

## Method

STARK is the official extraction step. For every file it runs the query

```text
upos=VERB >nsubj upos=NOUN >obj upos=NOUN
```

and emits tree types with frequencies; we aggregate by **summing STARK's
`Absolute frequency`** per language × genre × S/V/O pattern. A direct CoNLL-U
parser ([`scripts/validate_direct_conllu_svo.py`](scripts/validate_direct_conllu_svo.py))
re-extracts the same instances independently as a cross-check.

Full details, settings, flags, and data-quality notes:
[`docs/svo_ai_human_workflow.md`](docs/svo_ai_human_workflow.md).

## Run it

STARK is an external tool, not part of this repo. Point at it with `STARK_PY`
(or `--stark-py`); the runner resolves every other path relative to this project
folder, so it works from any working directory:

```bash
STARK_PY=/path/to/STARK/stark.py MPLCONFIGDIR=/tmp/mplconfig \
  python3 projects/2_human-vs-ai-svo/scripts/run_stark_svo_analysis.py
```

- Completed STARK TSVs are skipped, so an interrupted run resumes; add `--force`
  to recompute.
- `--process-only` rebuilds all tables/figures/report from existing TSVs without
  needing STARK.

## Outputs

Written to [`data/results/nh_svo_jun_2026/`](data/results/nh_svo_jun_2026/):

- `stark_svo_pattern_counts.tsv` — counts + proportions for all six orders.
- `stark_svo_ai_minus_human.tsv` — per-language `AI − Human` differences.
- `stark_svo_summary.tsv` — totals, SVO share, entropy by language/genre.
- `stark_svo_comparisons.tsv` — Jensen–Shannon distance, χ² test per language.
- `stark_vs_direct_validation.tsv` — STARK vs direct-parser cross-check.
- three heatmaps (`*_proportions_heatmap.png`, `*_ai_minus_human_heatmap.png`,
  `*_share_by_language.png`).

The narrative report is regenerated at
[`docs/nh_svo_jun_2026_results.md`](docs/nh_svo_jun_2026_results.md).

## Headline finding

AI text is more word-order-rigid (lower entropy, harder default to canonical
SVO) than human text in the flexible-order European/Slavic languages —
Slovenian +15.3pp SVO, Russian +12.6pp, Bulgarian +5.1pp — while in Arabic
(−8.4pp) and Urdu (−5.1pp) the AI shifts the other way. The direct-parser
cross-check agrees with STARK to within ~1% on every cell.
