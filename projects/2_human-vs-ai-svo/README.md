# Project 2 — Human vs AI SVO Word Order

> Does AI-generated text order **subject, verb, and object** differently from
> human text? Measured across 8 languages with the exact method of the SyntaxFest
> paper. Part of [UD-WALS-Linguistic-Patterns](../../README.md); sibling of
> [Project 1](../1_written-vs-spoken-svo/) (written vs spoken).

**Jump to:** [Goal](#goal) · [Method](#method) · [Data](#data) · [Run](#run) · [Results](#results) · [Data quality](#data-quality) · [Folder layout](#folder-layout)

## Goal

For each language we have a **Human** corpus and an **AI** corpus. In every verb
clause that has a noun subject and a noun object, we classify the linear order of
the three elements as one of `SVO`, `SOV`, `VSO`, `VOS`, `OSV`, `OVS`, and compare
the distribution between Human and AI.

> **Brief (K. Dobrovoljc):** *"Metodologijo uporabi povsem enako kot nazadnje
> (NOUN-nsubj in NOUN-obj), le da imamo tokrat namesto spoken in written dve drugi
> zvrsti."* — Use the identical methodology as last time (NOUN subject + NOUN
> object); the two varieties are now **Human** and **AI** instead of spoken and
> written.

## Method

Identical to the paper — only the two compared varieties changed.

| Brief / paper requirement | How it is implemented |
| --- | --- |
| Predicate is a verb | `upos=VERB` |
| Subject is a noun (`NOUN`-`nsubj`) | `>nsubj upos=NOUN` |
| Object is a noun (`NOUN`-`obj`) | `>obj upos=NOUN` |
| Classify the **linear** S/V/O order | STARK `fixed=yes` keeps surface order |
| `nsubj:pass` etc. treated as `nsubj` | `label_subtypes=no` |
| Count by frequency, not by row | sum STARK `Absolute frequency` per pattern |
| Two varieties | **Human** vs **AI** (was written vs spoken) |

STARK is the official extraction step and runs this query on every file:

```text
upos=VERB >nsubj upos=NOUN >obj upos=NOUN
```

An independent CoNLL-U parser
([`scripts/validate_direct_conllu_svo.py`](scripts/validate_direct_conllu_svo.py))
re-extracts the same triples a second way as a **cross-check**; the two methods
agree to within **0.93%** on every cell. Full settings and flags:
[`docs/svo_ai_human_workflow.md`](docs/svo_ai_human_workflow.md).

## Data

Eight language pairs (manifest:
[`data/raw/nh_svo_jun_2026/metadata.csv`](data/raw/nh_svo_jun_2026/metadata.csv)).
The `.conllu` corpora are gitignored (multi-GB); only the manifest is versioned.
The last two columns are the number of extracted S/V/O triples per side.

| Language | Source | AI model | Human | AI |
| --- | --- | --- | ---: | ---: |
| Arabic | wikipedia | gpt-3.5-turbo | 4,503 | 3,378 |
| Bulgarian | true-fake-news | gpt-3.5-turbo | 14,818 | 8,249 |
| Chinese | baike-web-qa | chatgpt | 11,935 | 6,255 |
| English | wikipedia | gpt-3.5-turbo | 22,437 | 5,992 |
| Indonesian | newspapers | gpt-3.5-turbo | 7,946 | 12,134 |
| Russian | ruatd | gpt-3.5-turbo | 8,348 | 5,477 |
| Slovenian | essays (4th-year) | gpt-5 | 1,671 | 3,248 |
| Urdu | urdu-news | gpt-3.5-turbo | 4,507 | 5,729 |

## Run

STARK is external to this repo; point at it with `STARK_PY`. Every other path is
resolved relative to this folder, so the command works from anywhere.

**On the CJVT server (Docker, from the repo root):**

```bash
docker compose up
```

**Locally (Python):**

```bash
STARK_PY=/path/to/STARK/stark.py MPLCONFIGDIR=/tmp/mplconfig \
  python3 projects/2_human-vs-ai-svo/scripts/run_stark_svo_analysis.py
```

- Completed STARK outputs are skipped, so an interrupted run resumes; `--force`
  recomputes from scratch.
- `--process-only` rebuilds tables/figures/report from existing TSVs (no STARK).

## Results

Written to [`data/results/nh_svo_jun_2026/`](data/results/nh_svo_jun_2026/):

| File | Contents |
| --- | --- |
| `stark_svo_pattern_counts.tsv` | counts + proportions, all six orders |
| `stark_svo_ai_minus_human.tsv` | per-language `AI − Human` differences |
| `stark_svo_summary.tsv` | totals, SVO share, entropy by language/variety |
| `stark_svo_comparisons.tsv` | Jensen–Shannon distance, χ² test per language |
| `stark_vs_direct_validation.tsv` | STARK vs direct-parser cross-check |
| `*_heatmap.png`, `*_share_by_language.png` | figures |

Narrative report: [`docs/nh_svo_jun_2026_results.md`](docs/nh_svo_jun_2026_results.md).

**Headline — change in SVO share, AI minus Human:**

| Language | Human | AI | AI − Human |
| --- | ---: | ---: | ---: |
| Slovenian | 74.0% | 89.3% | **+15.3** |
| Russian | 81.4% | 94.1% | **+12.7** |
| Bulgarian | 93.2% | 98.4% | +5.1 |
| Chinese | 96.8% | 99.8% | +3.0 |
| Indonesian | 98.3% | 99.6% | +1.3 |
| English | 99.5% | 99.9% | +0.4 |
| Urdu | 10.2% | 5.0% | −5.1 |
| Arabic | 21.7% | 13.3% | −8.4 |

AI text is **more rigidly SVO** (lower entropy) than human text in the
flexible-order European/Slavic languages, but **less** SVO than human text in
Arabic and Urdu, where the human baseline is already verb-initial / non-SVO.

## Data quality

Two source-data issues are handled automatically. Both are independent of the
methodology and too small to affect the proportions. Files not listed have zero
of both.

| File | Malformed sentences (skipped) | Unclassifiable triples (dropped) |
| --- | ---: | ---: |
| ar_wikipedia_human | 12 | 12 |
| bg_true-fake-news_gpt-3.5-turbo | 3 | 9 |
| bg_true-fake-news_human | 18 | 21 |
| en_wikipedia_human | 172 | 10 |
| id_newspapers_gpt-3.5-turbo | 0 | 2 |
| id_newspapers_human | 0 | 4 |
| ru_ruatd_human | 14 | 5 |
| ur_urdu-news_gpt-3.5-turbo | 0 | 10 |
| ur_urdu-news_human | 0 | 72 |
| zh_baike-web-qa_chatgpt | 7 | 3 |
| zh_baike-web-qa_human | 298 | 22 |
| **Total** | **524** | **170** |

1. **Malformed CoNLL-U sentences (524).** In the source corpora some sentences
   have corrupted columns from the original conversion — a POS tag or
   morphological features land in the `HEAD` field, or a token form with embedded
   spaces / invisible bidirectional marks shifts the columns. The parser cannot
   read these, so they are skipped before extraction. They cluster in
   web-scraped human corpora (Chinese 298, English 172) and are non-sentence
   material — tables, "See also" lists, cross-script fragments — with no clause to
   extract.
2. **Unclassifiable S/V/O triples (170).** STARK finds a triple, but an invisible
   right-/left-to-left mark (`U+200E` / `U+200F`) in Arabic/Urdu/Chinese text is
   counted as a 4th node, so a 3-way S/V/O order cannot be assigned. These rows
   are reported and dropped. Worst case Urdu-human 72 / 4,306 tree types (1.7%);
   every other file is below 0.5%.

## Folder layout

```text
projects/2_human-vs-ai-svo/
├── README.md                  # this file
├── scripts/
│   ├── run_stark_svo_analysis.py     # official pipeline (STARK → tables → report)
│   └── validate_direct_conllu_svo.py # independent cross-check parser
├── data/
│   ├── raw/nh_svo_jun_2026/          # metadata.csv (.conllu gitignored)
│   ├── interim/nh_svo_jun_2026/      # STARK TSV outputs (caches gitignored)
│   └── results/nh_svo_jun_2026/      # result tables + figures
└── docs/
    ├── svo_ai_human_workflow.md      # full method, settings, flags
    └── nh_svo_jun_2026_results.md    # narrative report (auto-generated)
```
