# Raw Data — nh_svo_jun_2026 (Human-vs-AI SVO, June 2026)

This folder contains the local raw CoNLL-U files for the Human-vs-AI SVO task.

The downloaded SharePoint structure had one file per language/genre subfolder. Those files were flattened here and renamed to the parent folder name:

`<language>_<source>_<genre-or-model>.conllu`

The `.conllu` files are intentionally gitignored because they are large local data files. The tracked `metadata.csv` file is the stable manifest used by the analysis script.

Run the official STARK-based analysis from the repo root (the runner resolves all
paths relative to the project folder, so no path flags are needed):

```bash
STARK_PY=/path/to/STARK/stark.py MPLCONFIGDIR=/tmp/mplconfig \
  python3 projects/2_human-vs-ai-svo/scripts/run_stark_svo_analysis.py
```

See [`../../docs/svo_ai_human_workflow.md`](../../docs/svo_ai_human_workflow.md)
for full options.
