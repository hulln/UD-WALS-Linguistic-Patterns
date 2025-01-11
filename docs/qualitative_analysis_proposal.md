# Qualitative Analysis Proposal

## **Objective**
To perform a qualitative analysis comparing word order patterns (V, S, O) between spoken (SST) and written (SSJ) corpora. This analysis will use full sentence examples matched to extracted patterns, focusing on word selection and exploring differences between the two corpora.

---

## **1. Sampling and Data Preparation**

### **1.1 Random Proportional Selection**
#### **Goal**
- Select **100 examples** proportionally across patterns and corpora.
- Ensure all patterns present in the dataset, including rare ones, are represented.

#### **Proportional Sampling**
1. **Frequency Distribution Analysis**:
   - Analyze the frequency of each pattern (e.g., SVO, VSO) in both SST and SSJ corpora.
   - Allocate sample numbers proportionally to reflect the distribution in each corpus. Proportional sampling ensures reliable comparisons and avoids bias.

2. **Inclusion of Rare Patterns**:
   - Ensure rare patterns are included by selecting at least **one example per pattern**, where possible. Including less common structures can reveal important syntactic details.

#### **Output**
- A list of selected examples containing:
  - **Words** from the examples (excluding relations like `nsubj` and `obj`).
  - Metadata:
    - Pattern classification (e.g., SVO, VSO).
    - Corpus origin (SST or SSJ).

---

### **1.2 Matching Selected Examples to Full Sentences**
#### **Challenge**
- The STARK program outputs examples with only extracted words and their relations, not full sentences.
- The original corpora include complete sentences marked with `# text`.

#### **Solution**
1. **Word Extraction**:
   - Extract **only the words** for each selected example, ignoring relational tags.
   - *Example*: From `imajo >nsubj otroci >obj priložnosti`, extract `imajo`, `otroci`, `priložnosti`.

2. **Corpus Search**:
   - Search the original corpora to find sentences containing the extracted words:
     - SST corpus: `data/src/sl_sst-ud.conllu`
     - SSJ corpus: `data/src/cleaned_sl_ssj-ud.conllu`
   - Locate sentences marked by `# text` where **all extracted words** appear, regardless of word order. Including multiple matches allows for more contextual analysis.

3. **Match Resolution**:
   - If one sentence matches, select it.
   - If multiple sentences match, include all for further comparison and deal with this later.

4. **Result Annotation**:
   - Record the following for each match:
     - Full sentence (`# text` content).
     - Word order pattern (e.g., VSO, SVO).
     - Corpus source (SST or SSJ).

#### **Output**
A dataset containing:
- Full Sentence
- Pattern
- Corpus
- Example Words

---

## **2. Qualitative Analysis**

### **2.1 Focus Areas**
1. **Word Order Patterns**:
   - Compare the frequency and usage of word order patterns in SST and SSJ.
   - Explore rare patterns for structural and contextual differences. Spoken language often shows more syntactic variation due to the pressures of real-time processing, unlike written language, which is more planned.

2. **Word Selection**:
   - Examine the lexical choices made in each corpus.
   - Investigate differences between spoken (SST) and written (SSJ) language.

3. **Spoken vs. Written Differences**:
   - Analyze variability in spoken language (SST) and the greater syntactic rigidity of written language (SSJ).

4. **Sociolinguistic and Pragmatic Factors**:
   - Explore how word order reflects emphasis, conversational strategies, or topic-focus structures in spoken data.
   - Consider how stylistic or situational factors influence word order choices.

---

## **3. Validation and Future Considerations**

### **3.1 Validation**
- Review a subset of matches manually to ensure:
  - Words were extracted accurately.
  - Sentences were matched correctly.

### **3.2 Additional Considerations**
- **Pre-annotation as an Alternative**:
  - Ideally, corpora should have unique sentence IDs during preprocessing. Without this, matching based on words in `# text` provides a workable solution.

- **Future Steps**:
  - Annotate corpora with unique IDs for future projects to simplify matching and analysis.

---

## **5. Key Goals**
1. Establish a solid foundation for qualitative analysis by linking selected examples to full sentences.
2. Compare spoken and written language based on word order patterns, lexical choices, and pragmatic features.
3. Gain insights into linguistic variability and contextual influences in the corpora.
