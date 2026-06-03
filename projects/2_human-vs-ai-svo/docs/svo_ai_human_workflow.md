# SVO Human-vs-AI Workflow

## Repo timeline

- 2024-11 to 2025-01: original course/project repository, WALS-to-UD mapping, Slovenian SSJ/SST word-order analysis, reports, and Streamlit app.
- 2025-03 to 2025-04: additional cross-linguistic visualizations for the Depling/SyntaxFest article.
- 2025-04-12: intermediate save before article submission.
- 2025-09-15: final heatmap folder with hardcoded SVO proportions, including the NOUN-only and NOUN+PROPN variants.

## Published article method

The article compared spoken and written corpora by extracting clauses where a verb governs both a nominal subject and a direct object, then classifying the linear order of subject, verb, and object as one of:

`SVO`, `SOV`, `VSO`, `VOS`, `OSV`, `OVS`.

For the new task, the requested comparable setting is the stricter NOUN-only variant:

`VERB > nsubj NOUN` and `VERB > obj NOUN`

The two compared genres are now `Human` and `AI`, instead of `Written` and `Spoken`.

## Official STARK pipeline

All paths below are relative to this project folder, `projects/2_human-vs-ai-svo/`.
The raw corpora live in:

`data/raw/nh_svo_jun_2026/`

The `.conllu` files are large local files and are gitignored. The tracked
`metadata.csv` manifest and `README.md` in that folder document the inputs; the
STARK TSV outputs and final results are versioned.

The runner resolves all of its default paths relative to the project folder, so
from anywhere in the repo you can simply run:

```bash
MPLCONFIGDIR=/tmp/mplconfig python3 projects/2_human-vs-ai-svo/scripts/run_stark_svo_analysis.py
```

STARK lives outside this repo. Point the runner at it with the `STARK_PY`
environment variable (or the `--stark-py` flag); the default falls back to
`~/Projekti/STARK/stark.py` in the current user's home:

```bash
STARK_PY=/path/to/STARK/stark.py MPLCONFIGDIR=/tmp/mplconfig \
  python3 projects/2_human-vs-ai-svo/scripts/run_stark_svo_analysis.py
```

Useful flags:

- `--force` — rerun STARK even where a TSV already exists (otherwise completed
  files are skipped, so an interrupted run resumes cleanly).
- `--process-only` — skip STARK and just rebuild tables/figures/report from the
  existing TSVs (fast, no STARK needed).
- `--skip-validation` — skip the direct-parser cross-check.
- `--chunk-threshold-mb` / `--chunk-size-mb` — large `.conllu` files are split
  into sentence-safe chunks before STARK to avoid out-of-memory kills; defaults
  are 60 / 50 MB, which cleared the ~90 MB+ files on this machine. Lower them if
  STARK still gets OOM-killed (returncode -9).

The direct CoNLL-U parser is validation-only and can also be run standalone:

```bash
MPLCONFIGDIR=/tmp/mplconfig python3 projects/2_human-vs-ai-svo/scripts/validate_direct_conllu_svo.py \
  --input-dir projects/2_human-vs-ai-svo/data/raw/nh_svo_jun_2026 \
  --metadata-csv projects/2_human-vs-ai-svo/data/raw/nh_svo_jun_2026/metadata.csv \
  --output-dir projects/2_human-vs-ai-svo/data/results/nh_svo_jun_2026/direct_validation
```

Official STARK settings:

- query: `upos=VERB >nsubj upos=NOUN >obj upos=NOUN`
- `complete=no`, `greedy_counter=no`, `processing_size=3`
- `node_type=form`, `labeled=yes`, `label_subtypes=no`, `fixed=yes`
- aggregation: sum STARK `Absolute frequency` by language, genre, and S/V/O pattern

## Known data-quality handling

- A small number of STARK tree rows are unclassifiable as S/V/O because of
  Unicode artifacts in Arabic/Urdu/CJK text (e.g. a stray RLM `‏` parsed as
  a fourth token). These are reported and dropped; per file they are well under
  1% of rows.
- Some raw `.conllu` sentences are malformed (e.g. a POS tag in the `head`
  column). The direct-parser validation skips these with a warning; STARK
  ignores them too. They do not affect the official counts materially.
- The report uses `pandas.DataFrame.to_markdown`, which needs the `tabulate`
  package (in `requirements.txt`).

## Outputs

- `input_files.csv`: files, metadata, STARK TSVs, and logs.
- `analysis_config.json`: exact settings used for the run.
- `stark_svo_tree_types.tsv`: STARK tree types with S/V/O labels.
- `stark_svo_pattern_counts.tsv`: counts and proportions for all six word orders.
- `stark_svo_ai_minus_human.tsv`: per-language differences, computed as `AI - Human`.
- `stark_svo_summary.tsv`: totals, SVO share, non-SVO share, and entropy by language/genre.
- `stark_svo_comparisons.tsv`: Jensen-Shannon distance, entropy, and chi-square test per language.
- `stark_vs_direct_validation.tsv`: comparison between official STARK results and direct-parser validation.
- `stark_svo_proportions_heatmap.png`: language/genre proportions.
- `stark_svo_ai_minus_human_heatmap.png`: centered heatmap of `AI - Human` differences.
- `stark_svo_share_by_language.png`: SVO share by language and genre.
