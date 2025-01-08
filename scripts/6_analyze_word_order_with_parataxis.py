import pandas as pd
from conllu import parse_incr

# Function to extract SVO word orders and handle clause splitting for parataxis and conj relations
def extract_svo_with_relations(filepath, corpus_name):
    word_orders = []
    examples = []
    corpora = []
    
    with open(filepath, "r", encoding="utf-8") as file:
        for sentence in parse_incr(file):
            # Create a dictionary of words by ID
            words = {token['id']: token for token in sentence if isinstance(token['id'], int)}
            
            # Identify tokens in separate clauses based on `parataxis` and `conj`
            clauses = []
            current_clause = []
            for token in sentence:
                if token['deprel'] in ['parataxis', 'conj'] and current_clause:
                    # Save the current clause when a `parataxis` or `conj` relation is encountered
                    clauses.append(current_clause)
                    current_clause = []
                current_clause.append(token)
            if current_clause:  # Add the final clause
                clauses.append(current_clause)
            
            # Process each clause separately
            for clause in clauses:
                svo_sequence = []
                for token in clause:
                    if token['deprel'] == 'nsubj':  # Subject
                        svo_sequence.append(('S', token['id']))
                    elif token['deprel'] in ['obj', 'iobj']:  # Object
                        svo_sequence.append(('O', token['id']))
                    elif token['upos'] == 'VERB':  # Verb
                        svo_sequence.append(('V', token['id']))
                svo_sequence.sort(key=lambda x: x[1])  # Sort by word order
                word_order = ''.join([x[0] for x in svo_sequence])
                if word_order:
                    word_orders.append(word_order)
                    # Save the clause as an example
                    examples.append(" ".join([token['form'] for token in clause]))
                    corpora.append(corpus_name)
    
    return pd.DataFrame({"Word Order": word_orders, "Example Sentence": examples, "Corpus": corpora})

# Paths to the corpora
ssj_path = "data/src/cleaned_sl_ssj-ud.conllu"  # Written corpus
sst_path = "data/src/sl_sst-ud.conllu"  # Spoken corpus

# Extract word orders and examples for both corpora (parataxis and conj relations)
ssj_data = extract_svo_with_relations(ssj_path, "SSJ")
sst_data = extract_svo_with_relations(sst_path, "SST")

# Combine data from both corpora
combined_data = pd.concat([ssj_data, sst_data], ignore_index=True)

# Filter for the main word orders
main_word_orders = ["SVO", "SOV", "VSO", "OSV", "OVS", "VOS"]
filtered_data = combined_data[combined_data["Word Order"].isin(main_word_orders)]

# Write all filtered examples to a file with corpus information in tab-separated format
with open("main_word_order_examples_with_corpus.tsv", "w", encoding="utf-8") as outfile:
    for _, row in filtered_data.iterrows():
        outfile.write(f"{row['Word Order']}\t{row['Example Sentence']}\t{row['Corpus']}\n")

print("Filtered examples with word orders and corpus info saved to 'main_word_order_examples_with_corpus.tsv'.")

# Summarize and focus on main types
ssj_summary = ssj_data[ssj_data["Word Order"].isin(main_word_orders)].groupby("Word Order").agg(
    Frequency_SSJ=("Word Order", "size"), Example_Sentence_SSJ=("Example Sentence", "first")
).reset_index()

sst_summary = sst_data[sst_data["Word Order"].isin(main_word_orders)].groupby("Word Order").agg(
    Frequency_SST=("Word Order", "size"), Example_Sentence_SST=("Example Sentence", "first")
).reset_index()

# Merge and compare
comparison = pd.merge(ssj_summary, sst_summary, on="Word Order", how="outer").fillna(0)
comparison.sort_values(by="Word Order", inplace=True)

# Save the comparison as a CSV file
comparison.to_csv("1_svo_word_order_parataxis_only.csv", index=False)

print("Analysis complete! Results with parataxis and conj splitting saved as 'svo_word_order_parataxis_only.csv'.")
