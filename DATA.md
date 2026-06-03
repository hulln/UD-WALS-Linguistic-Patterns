# Data inventory

Where every dataset lives, what it is, and whether it is tracked in git.

**Convention:** large, derived, or third-party data is **gitignored** (kept
locally / re-downloadable, never pushed) — this means the `.conllu` corpora,
STARK caches, and reference PDFs. The actual analysis **inputs and outputs**
(extracted pattern tables, result tables, figures, manifests) are **tracked**.

Per-project detail:

- **Project 1** — [`projects/1_written-vs-spoken-svo/DATA.md`](projects/1_written-vs-spoken-svo/DATA.md)
- **Project 2** — [`projects/2_human-vs-ai-svo/DATA.md`](projects/2_human-vs-ai-svo/DATA.md)

## Summary

| Where | What | In git? |
| --- | --- | --- |
| `projects/1_.../data/src/*.conllu` | UD Slovenian SSJ (written) + SST (spoken) treebanks | gitignored (public UD) |
| `projects/1_.../data/extracted/*.tsv` | STARK-extracted + processed S/V/O patterns | tracked |
| `projects/1_.../data/features/` | WALS↔UD feature lists and info | tracked |
| `projects/1_.../results/` | figures, summary tables, comparison spreadsheets | tracked |
| `projects/1_.../references/papers/` | third-party reference PDFs | gitignored (see references/README.md) |
| `projects/2_.../data/raw/nh_svo_jun_2026/*.conllu` | 16 Human/AI corpora, 8 languages | gitignored |
| `projects/2_.../data/raw/nh_svo_jun_2026/metadata.csv` | per-file manifest (machine-readable) | tracked |
| `projects/2_.../data/interim/.../tsv/` | STARK output TSVs | tracked |
| `projects/2_.../data/interim/.../{internal_saves,chunks,logs,runtime}/` | STARK caches/logs | gitignored |
| `projects/2_.../data/results/nh_svo_jun_2026/` | result tables, figures, report | tracked (a few machine-path files gitignored) |
