import pandas as pd

# Load the two datasets with correct delimiter
ssj_df = pd.read_csv('data/extracted/processed_ssj_patterns.tsv', delimiter='\t')
sst_df = pd.read_csv('data/extracted/processed_sst_patterns.tsv', delimiter='\t')

# Add a 'Corpus' column to each dataset
ssj_df['Corpus'] = 'SSJ'
sst_df['Corpus'] = 'SST'

# Combine the two datasets
combined_df = pd.concat([ssj_df, sst_df], ignore_index=True)

# Save the combined file as a TSV
combined_df.to_csv('data/extracted/processed_combined_corpora.tsv', index=False, sep='\t')

# Display the combined data to confirm
print(combined_df.head())
