# Final Report #3
(updated: 2025-01-10)

This is the final report of the work done in the project. It was divided into two main phases: the first phase involved extracting features from the WALS database and creating UD queries and linguistic questions, while the second phase focused on reviewing literature and carrying out my own analysis focusing on a specific WALS feature.

## Phase 1: Feature Table Creation

In the first phase, I faced challenges with automatically extracting the list of features from the WALS database. Unfortunately, this had to be done manually by copying and pasting, then editing the table. Initially, I worked on Slovenian and the Word Order category, but later expanded this to the entire WALS database. Automating this task would have made the process much easier, and this was the biggest problem I encountered in this phase.

During this phase, I relied mainly on my previous knowledge of [Universal Dependencies (UD)](https://universaldependencies.org/). However, since I am not a comparative linguist, understanding the specific features and their linguistic backgrounds took longer than I expected. Although this phase wasn’t critical for my university project, it was important for my colleagues in Slovenia, who are developing LLMs that would ideally understand UD queries. These LLMs aim to help researchers and the public use UD queries more easily. Currently, tools like [GrewMatch](https://match.grew.fr/), [Drevesnik](https://orodja.cjvt.si/drevesnik/), and [STARK](https://github.com/clarinsi/STARK) are specialized and not easy to use, so having UD knowledge built into LLMs could be very helpful.

While I didn’t learn a lot of new things personally in this phase, I did improve my skills in using Excel and Google Sheets and learned more about linguistic typology, which was useful. My contribution in this phase, although not directly related to my project, was still valuable to the larger project.

The final feature table, which included the UD queries and linguistic questions, is available [here](https://docs.google.com/spreadsheets/d/1__Yex-3RSVxV5EE73O_gWyB7J7DTcTU0/edit?gid=1396940900#gid=1396940900).

## Phase 2: Literature Review and Analysis

The second phase included reviewing existing research and doing my own analysis. I focused on the relationship between subject, object, and verb in two Slovenian corpora: SSJ (written) and SST (spoken). Both corpora are available on the UD website and already pre-annotated, which made the further work easier, but I had to clean up the punctuation in SSJ to make it comparable to SST that doesn’t include punctuation.

For the analysis, I chose WALS [Feature 82A: Order of Subject and Verb](https://docs.google.com/spreadsheets/d/1__Yex-3RSVxV5EE73O_gWyB7J7DTcTU0/edit?gid=1396940900#gid=1396940900) because it wasn’t too difficult to work with, but still offered a challenge. I started by using the STARK tool and modified the configuration settings. Performing the search query on both corpora took more time than I expected, as I had to familiarize myself with how the tool and query language worked.

After generating separate files for each corpus, I used Python to clean up the data, remove unnecessary columns, assign word order patterns, and combine the files into one for further analysis. The most time-consuming part was assigning word order patterns, as I initially had trouble tagging the correct parts of speech (POS). However, I eventually found a solution, and the data was successfully cleaned.

In the beginning, I also tried using Python for the entire process because I wanted to extract whole sentences rather than just isolated words from STARK. However, I ran into difficulties with parsing certain clauses, so I decided to stick with the method suggested by my colleagues, which worked better.

For the analysis, I looked at frequency distributions, identified dominant word orders, and used cosine similarity to compare the two corpora. I also analyzed proportional differences and applied probabilistic modeling using Dirichlet distributions to calculate expected proportions and variability for each corpus. To test statistical significance, I used a chi-square test and calculated bootstrap confidence intervals. I created various visualizations, such as bar plots and heatmaps, to present the results.

This part of the project helped me learn how to use Python for data analysis and visualization. While the findings weren’t groundbreaking and similar studies already exist, the process itself was valuable and gave me a deeper understanding of the topic.

## Phase 3: Drafting the Paper

The final phase involved drafting the paper. While the research didn’t lead to any major new findings, the process of writing the paper was a valuable experience. I used [LaTeX](https://www.latex-project.org/) to format the paper, learning how to modify a template, format text, insert figures, and manage references.

Although the findings from this research may not yet be ready for publication, I believe that expanding the analysis to include other languages or exploring a different WALS feature could yield more original insights. This area of research is specific and not widely explored, so it could be suitable for publication in the future.

## Additional Contributions

A major takeaway from this project was the creation of a [GitHub repository](https://github.com/hulln/UD-WALS-Linguistic-Patterns), where I organized the code and documentation in a clear, consistent, and transparent way. This experience taught me how to design GitHub repositories, which will be useful for future research and collaboration.

## Conclusion

Throughout the project, I faced some challenges, including needing more support from colleagues, but I also learned a lot about the topic and gained new skills in data analysis, programming, and academic writing. While the results may not be groundbreaking, I maybe plan to expand the analysis in the future, possibly focusing on rarer linguistic relations and aiming for publication.
