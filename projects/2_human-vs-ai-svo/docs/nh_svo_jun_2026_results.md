# SVO Word Order in Human vs AI-Generated Text

## Method

This analysis uses STARK as the official extraction step. For every file listed in `projects/2_human-vs-ai-svo/data/raw/nh_svo_jun_2026/metadata.csv`, the same query pattern was applied:

```text
upos=VERB >nsubj upos=NOUN >obj upos=NOUN
```

STARK outputs tree types and their frequencies. Aggregation therefore does not count rows; instead, for each pattern we sum the `Absolute frequency` column. Word orders are classified as `SVO`, `SOV`, `VSO`, `VOS`, `OSV`, and `OVS`.

## Headline result

The largest drop in the SVO share of AI relative to human text is in **Arabic** (-8.4 pp). The largest rise in the SVO share of AI is in **Slovenian** (+15.3 pp).

These are differences between proportions, so prose and figures report them as **percentage points (pp)**.

| Summary | Value |
| --- | --- |
| Number of languages | 8 |
| Genres / classes | Human, AI |
| Max STARK − direct-parser difference (count) | 791 |
| Max STARK − direct-parser difference (proportion) | 0.93 pp |

## SVO shares

| language   |   human_count |   ai_count |   human_proportion |   ai_proportion |   ai_minus_human |
|:-----------|--------------:|-----------:|-------------------:|----------------:|-----------------:|
| Arabic     |           977 |        448 |             0.2170 |          0.1326 |          -0.0843 |
| Urdu       |           458 |        289 |             0.1016 |          0.0504 |          -0.0512 |
| English    |         22328 |       5984 |             0.9951 |          0.9987 |           0.0035 |
| Indonesian |          7809 |      12087 |             0.9828 |          0.9961 |           0.0134 |
| Chinese    |         11550 |       6240 |             0.9677 |          0.9976 |           0.0299 |
| Bulgarian  |         13815 |       8113 |             0.9323 |          0.9835 |           0.0512 |
| Russian    |          6798 |       5153 |             0.8143 |          0.9408 |           0.1265 |
| Slovenian  |          1237 |       2902 |             0.7403 |          0.8935 |           0.1532 |

## Summary by language and variety

| language   | genre   |   total |   svo_count |   svo_proportion |   entropy |
|:-----------|:--------|--------:|------------:|-----------------:|----------:|
| Arabic     | AI      |    3378 |         448 |           0.1326 |    0.4407 |
| Arabic     | Human   |    4503 |         977 |           0.2170 |    0.7958 |
| Bulgarian  | AI      |    8249 |        8113 |           0.9835 |    0.1019 |
| Bulgarian  | Human   |   14818 |       13815 |           0.9323 |    0.3047 |
| Chinese    | AI      |    6255 |        6240 |           0.9976 |    0.0194 |
| Chinese    | Human   |   11935 |       11550 |           0.9677 |    0.1866 |
| English    | AI      |    5992 |        5984 |           0.9987 |    0.0107 |
| English    | Human   |   22437 |       22328 |           0.9951 |    0.0369 |
| Indonesian | AI      |   12134 |       12087 |           0.9961 |    0.0276 |
| Indonesian | Human   |    7946 |        7809 |           0.9828 |    0.1017 |
| Russian    | AI      |    5477 |        5153 |           0.9408 |    0.2747 |
| Russian    | Human   |    8348 |        6798 |           0.8143 |    0.6894 |
| Slovenian  | AI      |    3248 |        2902 |           0.8935 |    0.4722 |
| Slovenian  | Human   |    1671 |        1237 |           0.7403 |    0.9308 |
| Urdu       | AI      |    5729 |         289 |           0.0504 |    0.3252 |
| Urdu       | Human   |    4507 |         458 |           0.1016 |    1.1307 |

## Largest shifts in non-SVO patterns

| language   | pattern   |   human_proportion |   ai_proportion |   ai_minus_human |
|:-----------|:----------|-------------------:|----------------:|-----------------:|
| Urdu       | SOV       |             0.6630 |          0.9237 |           0.2608 |
| Arabic     | VSO       |             0.7189 |          0.8591 |           0.1402 |
| Urdu       | OVS       |             0.0954 |          0.0012 |          -0.0942 |
| Russian    | OVS       |             0.1126 |          0.0438 |          -0.0688 |
| Slovenian  | VSO       |             0.0790 |          0.0139 |          -0.0651 |
| Urdu       | OSV       |             0.0892 |          0.0243 |          -0.0649 |
| Slovenian  | OVS       |             0.0868 |          0.0450 |          -0.0418 |
| Bulgarian  | OVS       |             0.0496 |          0.0095 |          -0.0401 |
| Arabic     | VOS       |             0.0473 |          0.0077 |          -0.0396 |
| Urdu       | VSO       |             0.0291 |          0.0000 |          -0.0291 |

## Distances between distributions

| language   |   human_total |   ai_total |   jensen_shannon_distance |   chi2_p_value |
|:-----------|--------------:|-----------:|--------------------------:|---------------:|
| Urdu       |          4507 |       5729 |                   0.2685  |     1.171e-281 |
| Slovenian  |          1671 |       3248 |                   0.1549  |     3.383e-49  |
| Arabic     |          4503 |       3378 |                   0.1453  |     1.13e-57   |
| Russian    |          8348 |       5477 |                   0.1438  |     8.657e-99  |
| Bulgarian  |         14818 |       8249 |                   0.09573 |     9.525e-64  |
| Chinese    |         11935 |       6255 |                   0.09055 |     2.471e-35  |
| Indonesian |          7946 |      12134 |                   0.04872 |     3.075e-19  |
| English    |         22437 |       5992 |                   0.02765 |     0.006632   |

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
