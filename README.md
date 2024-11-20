# UD-WALS-Linguistic-Patterns

## Overview

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [System Information](#system-information)
  - [Cloning the Repository](#cloning-the-repository)
  - [Installation](#installation)
  - [Running the Scripts](#running-the-scripts)
- [Repository Structure](#repository-structure)
- [License](#license)
- [Credits](#credits)

### Prerequisites
- **Python**: This project requires Python 3.7 or later.
- **Libraries**: The following Python libraries are needed:
  - `matplotlib`
  - `pandas`

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
python scripts/2_compare_features.py
```

## Repository Structure

```bash
UD-WALS-Linguistic-Patterns
│
├── data/                                 # Data files
│   ├── 1_all_features.txt                # List of all linguistic features
│   ├── 1_slovene_features.txt            # Linguistic features specific to Slovenian
│   ├── 2_feature_distribution_plot.png   # Plot of feature distribution
│   ├── 2_slovene_features_info.csv       # Information on Slovenian linguistic features
│
├── scripts/                              # Scripts for data processing
│   ├── 1_get_data.py                     # Data extraction script (currently non-functional)
│   ├── 2_compare_features.py             # Script for comparing Slovenian vs. all features
│
├── docs/                                 # Documentation files
│   ├── project_proposal.pdf              # Project proposal PDF
│   └── reports/                          # Reports related to the project
│       └── 1_report.md                   # First report detailing project progress
│
├── requirements.txt                      # Dependencies
│
├── README.md                             # Project overview and setup instructions
│
├── LICENSE.txt                           # Apache License 2.0 for the project
│
└── .gitignore                            # Files/folders to ignore in version control
```

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
- Special thanks to [Kaja Dobrovoljc](https://kajad.github.io/) for giving me the opportunity to work on their project and for the invaluable guidance and support throughout the entire process.

### Resources
- **Libraries**: 
  - [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for web scraping and parsing HTML.
  - [Matplotlib](https://matplotlib.org/) for creating static, animated, and interactive visualizations in Python.
  - [Pandas](https://pandas.pydata.org/) for data manipulation and analysis.
  
- **References**:
  - [**Gravitacija Project**](https://www.aris-rs.si/sl/medn/gravity/predstavitev.asp)
  - [**Multilingual Gradient Word-Order Typology (EACL 2024)**](https://aclanthology.org/2024.eacl-short.6)
  - [**Universal Dependencies (UD)**](https://universaldependencies.org/)
  - [**World Atlas of Language Structures (WALS)**](https://wals.info/)

### Tools
- [**ChatGPT**](https://chat.openai.com/) for assistance with coding, debugging, and support with project-related tasks.
- [**GitHub**](https://github.com/) for version control and collaboration.
- [**Grew-match Tool**](https://match.grew.fr/) for matching and identifying syntactic structures in corpora.
- [**Python**](https://www.python.org/) for data processing and analysis.
- [**Q-CAT Tool**](https://slovnica.ijs.si/wp-content/uploads/2019/10/Q-CAT_prirocnik.pdf) for syntactic categorization and feature annotation.
- [**STARK Tool**](https://github.com/clarinsi/STARK) for syntactic analysis and pattern extraction in linguistic corpora.