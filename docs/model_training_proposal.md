# Model Training Proposal

## Objective:
The objective of this work is to develop a model capable of predicting the sentence order (such as SVO, OSV, etc.) of subject (S), verb (V), and object (O) in Slovenian sentences. This task will be approached using machine learning, starting with logistic regression, and progressing towards more advanced models like transformers.

## Methodology:

### 1. Data Preparation:
- **STARK Extraction:** Begin by utilizing the STARK tool to extract relevant sentence examples that contain subject (nsubj), verb (VERB), and object (obj) relations. The query `query = upos=VERB >nsubj _ >obj _` will be used to obtain examples that follow a common sentence structure in Slovenian.
Data Structure: The extracted examples will be processed into a format where each sentence is paired with its corresponding word order label. For example, the sentence:

`plavut <nsubj ima >obj plavutnic`

will be processed into the following format:
- **Text:** `plavut ima plavutnic`
- **Label:** `SVO`

This will involve:
1. Extracting the relevant words (subject, verb, and object) from the syntactic relations.
2. Reconstructing the sentence from the extracted components.
3. Assigning a label based on the order of the components (e.g., `SVO`, `OSV`, etc.).

The output for the example sentence will look like this:

```
Text: "plavut ima plavutnic"
Label: "SVO"
```
This structure ensures that the model receives both the sentence text and its corresponding word order label, which will be essential for supervised learning during training.

### 2. Data Processing:
- **Tokenization and UD Tagging:** To handle raw input sentences, [Classla](https://github.com/classla) will be used for tokenization, and [Trankit](https://github.com/nlp-uoregon/trankit) will be employed for automatic Universal Dependency (UD) annotation. These tools will enable processing of text into its syntactic components (tokens and their dependencies), providing essential information like subject, verb, and object.
- **Feature Extraction:** The processed data will focus on extracting only the relevant syntactic components (subject, verb, and object), which are crucial for predicting sentence order. This will involve handling cases where the root word (usually the verb) is identified and ensuring proper alignment with the subject and object labels.

### 3. Model Training and Evaluation:
- **Initial Model:** The model will be trained using the dataset derived from step 2. Initially, logistic regression can be used as a baseline. This simple model will serve to assess the basic feasibility of predicting sentence order based on the extracted features.
- **Advanced Models:** Upon establishing the baseline, the model will be upgraded to more advanced models, such as transformers, which are better equipped to handle syntactic complexity and can potentially improve the model’s performance.

### 4. Prediction on Raw Sentences:
- **Input Processing:** For a random input sentence, the model will first process it using tokenization and UD annotation. It will then extract the subject, verb, and object, alongside their respective relations (nsubj and obj).
- **Sentence Order Prediction:** Using the trained model, the sentence order will be predicted based on the extracted components. The model should output a classification corresponding to one of the six possible sentence structures (e.g., SVO, OSV, etc.).

### 6. Publishing:
To increase the accessibility and impact of this research, the following steps will be taken:

- **Publishing the Dataset:** The model training dataset will be split into training, validation, and test sets and published on HuggingFace. This will allow others to use and build upon the data for their own projects, contributing to the field of syntactic analysis.
- **Publishing a Demo or Final App:** A demo or final application will be published on HuggingFace using Gradio, providing an interactive platform where users can test the sentence order prediction model with their own input sentences. This will not only showcase the capabilities of the model but also offer an easy-to-use tool for educators, researchers, and language enthusiasts.



## Tools and Technologies:
- **STARK:** For extracting syntactic patterns and relationships from the Slovenian corpus.
- **Classla:** For tokenization of raw Slovenian text.
- **Trankit:** For automatic Universal Dependency annotation of Slovenian sentences.
- **Python:** For data processing, feature extraction, and model training.

## Expected Challenges:
- **Complexity of Slovenian Syntax:** Slovenian has flexible word order, which may present challenges in correctly identifying subject, object, and verb relations in more complex sentences.
- **Data Quality:** The quality and completeness of the extracted data from STARK may affect the model’s ability to generalize, especially for less common word orders.
- **Model Complexity:** While logistic regression is a good starting point, transitioning to transformers will require careful tuning and experimentation to optimize performance.

## Future Directions:
Upon successful completion of the sentence order prediction model, additional work can be focused on:
- Fine-tuning the model to handle sentences with more than three core components (e.g., adverbials, objects of prepositions).
- Exploring domain-specific sentence structures (e.g., formal vs. colloquial language).
- Expanding the dataset by including more varied examples from both written and spoken Slovenian corpora.
- Investigating more complex syntactic relations, which would make the model more capable of understanding a wider range of sentence structures. This would not only enhance the model's predictive power but also make the research more interesting and impactful.
- Making the project more accessible to a broader audience, such as those who are not experts in linguistics. This could be achieved by making the dataset and model available as a learning resource, useful for educational purposes in schools or universities.
