# UD-WALS-Linguistic-Patterns

Word-order research using Universal Dependencies (UD) and the World Atlas of
Language Structures (WALS). The repository holds two self-contained projects.

## Projects

Both projects ask the same question — *how does S/V/O word order differ between
two varieties of text?* — with the same STARK-based method, on different variety
pairs:

| # | Folder | Comparison | Period |
| - | ------ | ---------- | ------ |
| 1 | [`projects/1_written-vs-spoken-svo/`](projects/1_written-vs-spoken-svo/) | **Written vs spoken** SVO (Slovenian), grown from a WALS→UD course project into the SyntaxFest article. | 2024–2025 |
| 2 | [`projects/2_human-vs-ai-svo/`](projects/2_human-vs-ai-svo/) | **Human vs AI** SVO across 8 languages. | 2026 |

Each project folder is independent and has its own `README.md`, `scripts/`,
`data/`, `docs/`, and (where relevant) `results/`.

## Layout

```text
.
├── README.md            # this file
├── requirements.txt     # shared Python dependencies for both projects
└── projects/
    ├── 1_written-vs-spoken-svo/
    │   ├── README.md      # project guide
    │   ├── app/           # Streamlit app
    │   ├── scripts/       # numbered pipeline 1..6
    │   ├── data/          # extracted/, features/, src/ (CoNLL-U)
    │   ├── results/       # graphs/, analysis/ spreadsheets, result CSVs/PNGs
    │   ├── references/    # third-party papers + literature-review tracker
    │   └── docs/          # paper/, drafts/, midterm_reports/, meeting-notes/, PDFs
    └── 2_human-vs-ai-svo/
        ├── README.md
        ├── scripts/       # run_stark_svo_analysis.py, validate_direct_conllu_svo.py
        ├── data/          # raw/ (gitignored .conllu), interim/, results/
        └── docs/          # workflow + Slovenian results report
```

## Setup

```bash
pip install -r requirements.txt
```

See each project's `README.md` for how to run it.

## License

Apache License 2.0.

## Credits

[N. Hüll](https://hulln.github.io/). See
[`projects/1_written-vs-spoken-svo/README.md`](projects/1_written-vs-spoken-svo/README.md)
for full acknowledgments.
