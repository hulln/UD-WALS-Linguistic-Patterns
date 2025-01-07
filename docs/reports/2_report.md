# Midterm Report #2
(updated: 2024-12-01)

This week, I conducted a literature review on the task I’m working on for this project. The articles I reviewed are accessible at the following links:  
- [Multilingual Gradient Word-Order Typology from Universal Dependencies](https://aclanthology.org/2024.eacl-short.6)  
- [Corpus-based language universals analysis using Universal Dependencies](https://aclanthology.org/2021.quasy-1.3)
- [Basic word order typology revisited: a crosslinguistic quantitative study based on UD and WALS](https://doi.org/10.1515/lingvan-2021-0001)  

The three articles advocate for moving away from rigid linguistic classifications and towards data-driven, gradient-based approaches to better capture the diversity of language structures. By using datasets like Universal Dependencies (UD), they analyze word order patterns and validate Greenberg’s linguistic universals. Continuous data representations, rather than traditional methods, offer better insights into linguistic nuances and hold promise for improving both typological studies and multilingual NLP tasks, such as machine translation. However, there are still challenges to address, including biases in datasets and limited language coverage. These findings emphasize the importance of flexible, probabilistic modeling in understanding and applying linguistic patterns.

In the Zoom meeting with my colleagues, we discussed the articles’ content and how to proceed with our project. To date, I’ve extracted all features and identified the statistics for Slovenian data. We’ve now decided to focus solely on the “word order” section and proposed the following steps:

1. **Review each feature**:  
   - **Step 1**: Go through the list of features within the word order group and determine if they can be examined using the Universal Dependencies system. For the broader project (Gravitacija), I need to decide whether the feature can be analyzed this way and mark it as "yes," "no," or "not sure."  
   - **Step 2**: For features marked as "yes," determine if we can extract them in the form of a dependency tree using the [STARK](https://github.com/clarinsi/STARK) or [Drevesnik](https://orodja.cjvt.si/drevesnik/) tool. For this step, it would be helpful to introduce a two-level classification based on the difficulty of obtaining the information.

We also considered using [Grambank](https://grambank.clld.org/) instead of [WALS](https://wals.info/), but we decided against it. Grambank contains too many descriptive categories, which we anticipate would make it more challenging to navigate compared to WALS, which has the added advantage of subcategories (e.g., word order).

I’ve started working on both tasks but encountered some difficulties with the usage patterns of STARK. Specifically, I can't achieve the desired order of word categories when the relation is not direct. For direct relations, I can specify the direction; however, I am unsure how to handle cases where multiple words, such as a subject and object, are not directly connected (unlike a direct object-verb relation). My next step is to consult with [Luka Terčon](https://www.fri.uni-lj.si/sl/o-fakulteti/osebje/luka-tercon), my contact person for this task, as he is also familiar with STARK and can provide guidance.

At the meeting, we also discussed the second phase of the project, which involves a small analysis of selected categories for Slovenian. We agreed that the methodology proposed in the articles could be applicable to Slovenian data as well. However, I’m concerned that the process, which involves calculating probabilities and other advanced techniques, may be too complex at this stage.
