import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import entropy, pearsonr, spearmanr, chi2_contingency
from scipy.spatial.distance import jensenshannon
from numpy.linalg import norm
import numpy as np

# Function to save plots
def save_plot(fig_path, dpi=300):
    plt.savefig(fig_path, dpi=dpi, bbox_inches='tight')
    plt.clf()

# Load the combined dataset
file_path = 'data/extracted/processed_combined_corpora.tsv'
try:
    df = pd.read_csv(file_path, delimiter='\t')
except FileNotFoundError:
    print(f"File not found: {file_path}")
    raise
except pd.errors.EmptyDataError:
    print(f"File is empty: {file_path}")
    raise

# Section 1: Frequency Distribution Analysis
print("\n--- Section 1: Frequency Distribution Analysis ---")
pattern_counts = df.groupby(['Corpus', 'Pattern']).size().reset_index(name='Count')
total_counts = pattern_counts.groupby('Corpus')['Count'].transform('sum')
pattern_counts['Proportion'] = pattern_counts['Count'] / total_counts

# Proportional bar plot for frequency distribution
sns.barplot(data=pattern_counts, x='Pattern', y='Proportion', hue='Corpus')
plt.title('Proportional Word Order Patterns in SSJ vs SST')
plt.ylabel('Proportion')
plt.xlabel('Word Order Pattern')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
freq_fig_path = 'data/results/proportional_distribution.png'
save_plot(freq_fig_path)
print(f"Proportional distribution plot saved to: {freq_fig_path}")

# Section 2: Dominant Word Orders
def find_dominant_order(group):
    print("\n--- Processing a new group ---")
    print("This group contains data for one specific corpus (e.g., SSJ or SST):")
    print(group)  # Display the current subset (group) being processed

    # Step 1: Sort the patterns by 'Count' in descending order
    sorted_counts = group.sort_values('Count', ascending=False)
    print("\nStep 1: Patterns in this group have been sorted by their count (highest to lowest):")
    print(sorted_counts)

    # Step 2: Check if the most frequent pattern is dominant
    # Dominance condition: If the most frequent pattern's count is >= 2x the second-most frequent pattern's count
    if len(sorted_counts) > 1:  # Ensure there is more than one pattern to compare
        most_frequent = sorted_counts.iloc[0]
        second_most_frequent = sorted_counts.iloc[1]
        print("\nStep 2: Checking if the most frequent pattern is dominant:")
        print(f"Most frequent pattern: {most_frequent['Pattern']} with count {most_frequent['Count']}")
        print(f"Second most frequent pattern: {second_most_frequent['Pattern']} with count {second_most_frequent['Count']}")

        if most_frequent['Count'] >= 2 * second_most_frequent['Count']:
            print(f"The most frequent pattern ({most_frequent['Pattern']}) is dominant because "
                  f"{most_frequent['Count']} >= 2 * {second_most_frequent['Count']}")
            return most_frequent['Pattern']
        else:
            print(f"The most frequent pattern ({most_frequent['Pattern']}) is NOT dominant because "
                  f"{most_frequent['Count']} < 2 * {second_most_frequent['Count']}")
    else:
        print("\nStep 2: Skipping dominance check because there is only one pattern in this group.")

    # If no dominant pattern is found, return 'NDO' (No Dominant Order)
    print("No dominant pattern found for this group. Returning 'NDO'.")
    return 'NDO'

# Group by 'Corpus' and apply the function
print("\nGrouping data by 'Corpus' and determining the dominant pattern for each corpus...")
dominant_orders = pattern_counts.groupby('Corpus').apply(find_dominant_order).reset_index(name='Dominant_Order')

print("\n--- Final Result: Dominant Orders by Corpus ---")
print(dominant_orders)

# Section 3: Proportions and Distribution Comparisons
print("\n--- Section 3: Proportions and Distribution Comparisons ---")

# Step 1: Extract proportions for SSJ
print("\nStep 1: Extracting proportion values for SSJ corpus...")
ssj_vector = pattern_counts[pattern_counts['Corpus'] == 'SSJ']['Proportion'].values
print("Proportions for SSJ:")
print(ssj_vector)

# Step 2: Extract proportions for SST
print("\nStep 2: Extracting proportion values for SST corpus...")
sst_vector = pattern_counts[pattern_counts['Corpus'] == 'SST']['Proportion'].values
print("Proportions for SST:")
print(sst_vector)

# Step 3: Calculate distribution comparisons
print("\nStep 3: Calculating distribution comparisons...")
try:
    # Jensen-Shannon Divergence
    js_divergence = jensenshannon(ssj_vector, sst_vector)
    print(f"Jensen-Shannon Divergence: {js_divergence}")

    # Entropy
    ssj_entropy = entropy(ssj_vector)
    sst_entropy = entropy(sst_vector)
    print(f"Entropy for SSJ: {ssj_entropy}, Entropy for SST: {sst_entropy}")

    # Pearson Correlation
    correlation, _ = pearsonr(ssj_vector, sst_vector)
    print(f"Pearson Correlation: {correlation}")

    # Spearman Rank Correlation
    rank_correlation, _ = spearmanr(ssj_vector, sst_vector)
    print(f"Spearman Rank Correlation: {rank_correlation}")

    # Euclidean Distance
    euclidean_distance = norm(ssj_vector - sst_vector)
    print(f"Euclidean Distance: {euclidean_distance}")
except ValueError as e:
    print(f"Error in distribution comparisons: {e}")

# Section 4: Proportional Differences
print("\n--- Section 4: Proportional Differences ---")

# Step 1: Pivot table to align SSJ and SST proportions
print("\nStep 1: Creating a pivot table to align proportions from both corpora by pattern...")
diff = pattern_counts.pivot(index='Pattern', columns='Corpus', values='Proportion').fillna(0)
print("Pivot table (Proportions of patterns in SSJ and SST):")
print(diff)

# Step 2: Calculate the proportional difference (SST - SSJ)
print("\nStep 2: Calculating the proportional differences (SST - SSJ)...")
diff['Difference'] = diff['SST'] - diff['SSJ']
print("Proportional differences by pattern:")
print(diff[['Difference']])

# Save the differences to a CSV file
diff_csv_path = 'data/results/proportional_differences.csv'
diff.to_csv(diff_csv_path)
print(f"\nProportional differences saved to: {diff_csv_path}")

# Step 3: Visualize the differences with a heatmap
print("\nStep 3: Creating a heatmap to visualize the differences...")
vmin, vmax = -max(abs(diff['Difference'])), max(abs(diff['Difference']))  # Ensure symmetrical color scale
plt.figure(figsize=(6, 8))
sns.heatmap(diff[['Difference']], annot=True, cmap='coolwarm', center=0, vmin=vmin, vmax=vmax)
plt.title('Difference in Word Order Proportions (SST - SSJ)')
plt.xlabel('Corpus')
plt.ylabel('Word Order Pattern')
heatmap_fig_path = 'data/results/word_order_proportions_difference_heatmap_zero_centered.png'
save_plot(heatmap_fig_path)
print(f"Heatmap of proportional differences saved to: {heatmap_fig_path}")

# Interpretation
print("\nInterpretation:")
print("- The pivot table aligns proportions for each word order pattern across the SSJ and SST corpora.")
print("- The 'Difference' column shows how much more frequent each pattern is in SST compared to SSJ.")
print("- Positive values in the heatmap indicate patterns more frequent in SST, while negative values indicate patterns more frequent in SSJ.")

# Section 5: Chi-Square Test
print("\n--- Section 5: Chi-Square Test ---")

# Step 1: Create a contingency table
print("\nStep 1: Creating a contingency table with observed counts for each pattern in SSJ and SST...")
contingency_table = pattern_counts.pivot(index='Pattern', columns='Corpus', values='Count').fillna(0).astype(int)
print("Contingency Table (Observed Counts):")
print(contingency_table)

# Step 2: Perform the Chi-Square test
print("\nStep 2: Performing the Chi-Square test...")
chi2, p, dof, expected = chi2_contingency(contingency_table.values)

# Step 3: Display the test results
print("\nStep 3: Results of the Chi-Square test:")
print(f"Chi-Square Statistic: {chi2}")
print(f"Degrees of Freedom: {dof}")
print(f"P-Value: {p}")

# Step 4: Display observed vs. expected counts
print("\nStep 4: Observed vs. Expected Counts")

# Observed counts
print("\nObserved Counts:")
print(contingency_table)

# Expected counts
expected_table = pd.DataFrame(expected, index=contingency_table.index, columns=contingency_table.columns)
print("\nExpected Counts:")
print(expected_table)

# Contribution to Chi-Square Statistic
contributions = (contingency_table - expected_table) ** 2 / expected_table
print("\nContribution to Chi-Square Statistic (for each cell):")
print(contributions)

# Total contribution per pattern
contributions['Total_Contribution'] = contributions.sum(axis=1)
print("\nTotal Contribution to Chi-Square by Pattern:")
print(contributions[['Total_Contribution']])

# Step 5: Visualize observed vs. expected counts
print("\nStep 5: Visualizing Observed vs. Expected Counts...")
patterns = contingency_table.index
x = np.arange(len(patterns))  # Bar positions
width = 0.35  # Width of the bars

fig, ax = plt.subplots(figsize=(10, 6))

# Plot observed counts
ax.bar(x - width/2, contingency_table['SSJ'], width, label='Observed SSJ')
ax.bar(x + width/2, contingency_table['SST'], width, label='Observed SST')

# Plot expected counts
ax.scatter(x - width/2, expected_table['SSJ'], color='red', label='Expected SSJ', zorder=3)
ax.scatter(x + width/2, expected_table['SST'], color='blue', label='Expected SST', zorder=3)

# Customize plot
ax.set_xticks(x)
ax.set_xticklabels(patterns, rotation=45)
ax.set_ylabel('Counts')
ax.set_title('Observed vs. Expected Counts by Pattern')
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Save and show plot
visualization_path = 'data/results/observed_vs_expected_counts.png'
save_plot(visualization_path)
print(f"Visualization saved to: {visualization_path}")

# Interpretation
print("\nInterpretation:")
if p < 0.05:
    print("- The P-value is less than 0.05, indicating that the differences in word order patterns between SSJ and SST are statistically significant.")
else:
    print("- The P-value is greater than 0.05, indicating that the differences in word order patterns between SSJ and SST are NOT statistically significant.")
print("- The Chi-Square statistic measures the extent of deviation between the observed and expected counts.")
print("- Patterns with higher contributions to the Chi-Square statistic are those where observed counts deviate most from expected counts.")