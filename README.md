# UD-WALS-Linguistic-Patterns

## Overview

This repository was created as part of a university project for the [*Digital Linguistics Project*](https://theta.ffzg.hr/ECTS/Predmet/Index/35946) course at the Faculty of Social Sciences and Humanities, University of Zagreb. The project aims to document and explore linguistic patterns using Universal Dependencies (UD) and the World Atlas of Language Structures (WALS).

The project was divided into two phases:
1. **Phase 1**: Contribution to a broader Slovenian linguistic project, involving the creation of a table mapping WALS features to UD queries.
2. **Phase 2**: An independent analysis focusing on word order patterns in Slovenian, comparing written and spoken corpora.

The repository serves as a transparent record of the work, including data processing scripts, [analysis results](#results-word-order-analysis), and relevant documentation.


## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [System Information](#system-information)
  - [Cloning the Repository](#cloning-the-repository)
  - [Installation](#installation)
  - [Running the Scripts](#running-the-scripts)
- [Repository Structure](#repository-structure)
- [Results: Word Order Analysis](#results-word-order-analysis)
- [License](#license)
- [Credits](#credits)

### Prerequisites
- **Python**: This project requires Python 3.7 or later.
- **Libraries**: The following Python libraries are needed:
  - `matplotlib`
  - `pandas`
  - `seaborn`
  - `numpy`
  - `scipy`
  - `conllu`
  - `scikit-learn`

You can install the required libraries using the `requirements.txt` file provided in the repository.


### System Information
- **Operating System:** Windows 11
- **Version:** 10.0.22631.4317 (Windows 11)
- **Windows Subsystem for Linux (WSL):** Enabled
- **WSL Distribution:** Ubuntu
- **WSL Version:** 2

### Cloning the Repository
To clone this repository, run the following command:

```bash
git clone https://github.com/UD-WALS-Linguistic-Patterns.git
```

### Installation
To install the required dependencies, navigate to the project directory and run:

```bash
pip install -r requirements.txt
```

### Running the Scripts
To run the scripts, navigate to the project directory and run:

```bash
python scripts/[script_name].py
```

## Repository Structure

```bash
UD-WALS-Linguistic-Patterns
│
├── data/                               # Data files
│   ├── extracted/                      # Processed datasets
│   ├── features/                       # Feature data and visualizations
│   ├── results/                        # Analysis outputs
│   ├── src/                            # Raw CoNLL-U files
│
├── docs/                               # Documentation
│   ├── reports/                        # Reports and drafts
│   ├── project_proposal.pdf            # Project proposal
│   ├── projekt_zg.v1.pdf               # Draft paper
│
├── scripts/                            # Python scripts
│   ├── 1_compare_features.py           # Compare features
│   ├── 2_fix_and_validate_conllu.py    # Fix and validate CoNLL-U files
│   ├── 3_remove_punct_conllu.py        # Remove punctuation
│   ├── 4_clean_stark_word_order.py     # Process word order
│   ├── 5_combine_both_processed.py     # Merge datasets
│   ├── 6_analyze_processed.py          # Analyze corpora
│
├── requirements.txt                    # Dependencies
├── README.md                           # Repository guide
└── LICENSE.txt                         # License
```

## Results: Word Order Analysis

The quantitative study conducted as part of this project reveals key differences in word order patterns between spoken and written Slovenian:

- **Written Corpus (SSJ)**:
  - Strong preference for SVO (Subject-Verb-Object), reflecting the structured syntax typical of written language and aligning with the WALS value for Slovenian.
- **Spoken Corpus (SST)**:
  - Greater variation, with word orders such as SOV, OSV, and OVS appearing more often.

### Interpretation
- Written language prioritizes unmarked SVO for clarity and consistency.
- Spoken language is more flexible, using varied word orders to emphasize topics or structure information.
- These findings highlight the adaptability of spoken syntax and the influence of pragmatics on word order, emphasizing the need to revisit and update outdated WALS feature values.

### Outputs
Visualizations and analysis results are available in `data/results/` and in the paper draft located at `docs/projekt_zg.v1.pdf`.

## License

This project is licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).

### Key Terms:
- **Permissions**: This license allows for the use, modification, and distribution of the code, provided that all copies or substantial portions of the code include the original license.
- **Limitations**: The code is provided "as is," without warranty of any kind, express or implied, and without liability for any claims or damages arising from its use.
- **Attribution**: If you modify and distribute this code, you must include a prominent notice stating that you modified the files.

For more details, please refer to the full license text.

## Credits

- **[Nives Hüll](https://hulln.github.io/)** (nh23084@student.uni-lj.si, nhull@m.ffzg.hr)

### Acknowledgments
- Special thanks to [Kaja Dobrovoljc](https://kajad.github.io/) for the opportunity to contribute to their project, which is part of the broader [Gravitacija Project](https://www.aris-rs.si/sl/medn/gravity/predstavitev.asp), a Slovenian initiative providing valuable resources and inspiration for research in syntactic typology and universal dependencies. I also thank [Luka Terčon](https://www.fri.uni-lj.si/sl/o-fakulteti/osebje/luka-tercon) for all support, guidance, and assistance during the project.


### Resources
- **Libraries**: 
  - [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for web scraping and parsing HTML.
  - [Matplotlib](https://matplotlib.org/) for visualizations.
  - [Pandas](https://pandas.pydata.org/) for data manipulation and analysis.
  - [Seaborn](https://seaborn.pydata.org/) for statistical data visualization.
  - [NumPy](https://numpy.org/) for numerical computing.
  - [SciPy](https://scipy.org/) for scientific computing.
  - [Conllu](https://pypi.org/project/conllu/) for processing CoNLL-U files.
  - [Scikit-learn](https://scikit-learn.org/) for machine learning utilities.

### Tools
- [**ChatGPT**](https://chat.openai.com/) for coding, debigging, and writing assistance.
- [**GitHub**](https://github.com/) for version control and collaboration.
- [**Grew-match**](https://match.grew.fr/) for syntactic structure identification in corpora.
- [**Python**](https://www.python.org/) for data processing and analysis.
- [**Q-CAT**](https://slovnica.ijs.si/wp-content/uploads/2019/10/Q-CAT_prirocnik.pdf) for syntactic categorization.
- [**STARK**](https://github.com/clarinsi/STARK) for linguistic corpus processing.