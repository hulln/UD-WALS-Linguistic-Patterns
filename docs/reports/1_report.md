# Project Workflow

### Step 1: Repository Creation and Data Preparation (Observed Data from WALS)

The first step was to create a GitHub repository to document the work as we progressed. The next step involved gathering feature data from WALS to prepare the foundation for working with Slovenian data.

Initially, we aimed to extract all features into a list or similar format and then extract the features related to Slovenian. We wanted to compare these two lists. However, due to limited knowledge of web scraping, this approach did not work. Instead, we manually transformed the tables by copying and pasting into a `.txt` file. 

**Problem 1**: How to scrape the data, as it is embedded in a dynamic JavaScript element.

We then used a script to compare which features were available in Slovenian compared to the entire dataset, and we came to the following conclusions:

---

## Descriptive Summary

### Feature Distribution

**Total Features**: 206, with 52 (25.2%) in Slovenian.
- **Word Order** has the most features (56 total, 21 in Slovenian, 37.5%).
- **Verbal Categories** follows (17 total, 10 in Slovenian, 58.8%).
- **Phonology** (20 total, 4 in Slovenian, 20%), **Nominal Categories** (29 total, 3 in Slovenian, 10.3%), and **Simple Clauses** (26 total, 3 in Slovenian, 11.5%) have low Slovenian coverage.
- **Morphology** and **Lexicon** are nearly absent (12 and 13 total, 1 in Slovenian each, 8.3% and 7.7%).
- **Sign Languages** and **Other** have no Slovenian features.

### Conclusion

Slovenian features are mostly found in **Word Order** and **Verbal Categories**, with minimal representation in other areas like **Phonology** and **Lexicon**. **Sign Languages** and **Other** are entirely missing.

---

### Next Steps

For the next phase of the project, we will focus on the **Word Order** category, which has the highest number of Slovenian features.