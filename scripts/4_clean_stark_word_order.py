import pandas as pd

# Load the Excel file or TSV data
ssj_patterns_file = 'data/extracted/ssj_patterns.tsv'
sst_patterns_file = 'data/extracted/sst_patterns.tsv'

# Load the data from the TSV files
ssj_data = pd.read_csv(ssj_patterns_file, sep='\t')
sst_data = pd.read_csv(sst_patterns_file, sep='\t')

# Function to join elements with their corresponding UD relations, considering arrow direction
def join_ud_relations_with_direction(row):
    elements = row.split()
    result = []
    i = 0
    while i < len(elements):
        if elements[i].startswith('<') and i > 0:  # Relation pointing to the previous word
            result[-1] = f"{result[-1]} {elements[i]}"
        elif elements[i].startswith('>') and i + 1 < len(elements):  # Relation pointing to the next word
            result.append(f"{elements[i]} {elements[i + 1]}")
            i += 1
        else:
            result.append(elements[i])
        i += 1
    return result

# Function to classify elements into O, S, or V
def classify_element(element):
    # Check if the element contains 'obj' and also has a subject or object relation
    if '<obj' in element or '>obj' in element:
        if '<nsubj' in element or '>nsubj' in element:
            return 'S'  # It’s a subject in the context of an object relation
        else:
            return 'O'  # It’s an object (contains 'obj', but no subject relation)
    elif '<nsubj' in element or '>nsubj' in element:
        return 'S'  # It’s a subject (based on 'nsubj' relation)
    else:
        return 'V'  # Default classification as verb if it’s neither subject nor object


# Define a function to process each dataset
def process_data(data):
    # Step 1: Transform the 'Tree' column
    data['Transformed_Tree'] = data['Tree'].apply(
        lambda x: join_ud_relations_with_direction(x) if isinstance(x, str) else []
    )
    # Step 2: Classify elements into O, S, or V
    data['One'] = data['Transformed_Tree'].apply(
        lambda x: classify_element(x[0]) if len(x) > 0 else ''
    )
    data['Two'] = data['Transformed_Tree'].apply(
        lambda x: classify_element(x[1]) if len(x) > 1 else ''
    )
    data['Three'] = data['Transformed_Tree'].apply(
        lambda x: classify_element(x[2]) if len(x) > 2 else ''
    )

    # Step 3: Create a Pattern column combining One, Two, and Three
    data['Pattern'] = data['One'] + data['Two'] + data['Three']

    # Step 4: Remove unnecessary columns
    columns_to_remove = ['Node A-form', 'Node B-form', 'Node C-form', 'Absolute frequency', 'Relative frequency', 'Order', 'Grew-match query', 'Grew-match URL', 'Number of nodes', 'Head node']
    data = data.drop(columns=[col for col in columns_to_remove if col in data.columns], errors='ignore')
    
    return data

# Process both datasets
processed_ssj_data = process_data(ssj_data)
processed_sst_data = process_data(sst_data)

# Save the processed datasets
output_ssj_file = 'data/extracted/processed_ssj_patterns.tsv'
output_sst_file = 'data/extracted/processed_sst_patterns.tsv'

processed_ssj_data.to_csv(output_ssj_file, sep='\t', index=False)
processed_sst_data.to_csv(output_sst_file, sep='\t', index=False)

print(f"SSJ data saved to {output_ssj_file}")
print(f"SST data saved to {output_sst_file}")
