import pandas as pd
import matplotlib.pyplot as plt

# Load data from the 'data' folder
all_features = pd.read_csv("data/features/all_features.txt", sep="\t")
slovene_features = pd.read_csv("data/features/slovene_features.txt", sep="\t")

# Find common and missing IDs
common_ids = set(all_features['Id']).intersection(set(slovene_features['Id']))
missing_ids = set(all_features['Id']).difference(set(slovene_features['Id']))

# Add a 'Slovene' column to indicate whether each Id is present in the Slovene features
all_features['Slovene'] = all_features['Id'].apply(lambda x: 'Y' if x in slovene_features['Id'].values else 'N')

# Merge the 'Value' column from slovene_features to all_features, where applicable
merged = all_features.merge(slovene_features[['Id', 'Value']], on='Id', how='left')

# Create the final dataframe for the CSV
merged['Value'] = merged.apply(lambda row: row['Value'] if row['Slovene'] == 'Y' else None, axis=1)

# Save to CSV with the '2_' prefix in the 'data' folder
merged.to_csv("data/2_slovene_features_info.csv", columns=['Id', 'Name', 'Area', 'Slovene', 'Value'], index=False)

# Create a visualization of feature distribution by area and Slovene status
area_slovene_count = merged.groupby(['Area', 'Slovene']).size().unstack(fill_value=0)

# Plot the bar chart
area_slovene_count.plot(kind='bar', stacked=True, figsize=(10, 6), color=['lightblue', 'lightgreen'])

# Add titles and labels
plt.title('Feature Distribution by Area and Slovenian Status')
plt.xlabel('Feature Area')
plt.ylabel('Count of Features')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Slovene Status', labels=['Missing (N)', 'Present (Y)'])
plt.tight_layout()

# Save the plot as a PNG file
plt.savefig("data/feature_distribution_plot.png")

# Show the plot (optional)
# plt.show()

# Output results
print(f"Number of common IDs: {len(common_ids)}")
print(f"Common IDs: {common_ids}")
print(f"Number of missing IDs: {len(missing_ids)}")
print(f"Missing IDs: {missing_ids}")
print("\nAll Features - Area Counts:")
print(all_features['Area'].value_counts())
print("\nSlovene Features - Area Counts:")
print(slovene_features['Area'].value_counts())

print("\nCSV 'data/features/slovene_features_info.csv' has been created.")
print("\nPlot saved as 'data/features/feature_distribution_plot.png'.")
