import pandas as pd
from conllu import parse_incr

# Function to extract SVO word orders and example sentences from a CoNLL-U file
def extract_svo_order_with_examples(filepath):
    word_orders = []
    examples = []
    with open(filepath, "r", encoding="utf-8") as file:
        for sentence in parse_incr(file):
            words = {token['id']: token for token in sentence if isinstance(token['id'], int)}
            svo_sequence = []
            for token_id, token in words.items():
                if token['deprel'] == 'nsubj':  # Subject
                    svo_sequence.append(('S', token_id))
                elif token['deprel'] in ['obj', 'iobj']:  # Object
                    svo_sequence.append(('O', token_id))
                elif token['upos'] == 'VERB':  # Verb
                    svo_sequence.append(('V', token_id))
            svo_sequence.sort(key=lambda x: x[1])  # Sort by word order
            word_order = ''.join([x[0] for x in svo_sequence])
            if word_order:
                word_orders.append(word_order)
                # Save the full sentence as an example
                examples.append(" ".join([token['form'] for token in sentence]))
    return pd.DataFrame({"Word Order": word_orders, "Example Sentence": examples})

# Paths to your files
ssj_path = "data/src/fixed_sl_ssj-ud.conllu"  # Written corpus
sst_path = "data/src/sl_sst-ud.conllu"  # Spoken corpus

# Extract word orders and examples for both corpora
ssj_data = extract_svo_order_with_examples(ssj_path)
sst_data = extract_svo_order_with_examples(sst_path)

# Summarize and add examples
ssj_summary = ssj_data.groupby("Word Order").agg(
    Frequency_SSJ=("Word Order", "size"), Example_Sentence_SSJ=("Example Sentence", "first")
).reset_index()

sst_summary = sst_data.groupby("Word Order").agg(
    Frequency_SST=("Word Order", "size"), Example_Sentence_SST=("Example Sentence", "first")
).reset_index()

# Merge and compare
comparison = pd.merge(ssj_summary, sst_summary, on="Word Order", how="outer").fillna(0)
comparison.sort_values(by="Word Order", inplace=True)

# Save the comparison as a CSV file
comparison.to_csv("svo_word_order_comparison_with_examples.csv", index=False)

print("Analysis complete! Results with examples saved as 'svo_word_order_comparison_with_examples.csv'.")
