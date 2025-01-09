import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.special import digamma
from scipy.stats import dirichlet, chi2_contingency

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
    sorted_counts = group.sort_values('Count', ascending=False)
    if len(sorted_counts) > 1 and sorted_counts.iloc[0]['Count'] >= 2 * sorted_counts.iloc[1]['Count']:
        return sorted_counts.iloc[0]['Pattern']
    return 'NDO'

dominant_orders = pattern_counts.groupby('Corpus').apply(find_dominant_order).reset_index(name='Dominant_Order')
print("\nDominant Orders by Corpus:")
print(dominant_orders)

# Section 3: Proportions and Cosine Similarity
try:
    ssj_vector = pattern_counts[pattern_counts['Corpus'] == 'SSJ']['Proportion'].values
    sst_vector = pattern_counts[pattern_counts['Corpus'] == 'SST']['Proportion'].values
    similarity = cosine_similarity([ssj_vector], [sst_vector])[0][0]
    print(f"\nCosine Similarity between SSJ and SST: {similarity}")
except ValueError:
    print("Error in cosine similarity calculation. Ensure vectors have the same length.")

# Section 4: Proportional Differences
diff = pattern_counts.pivot(index='Pattern', columns='Corpus', values='Proportion').fillna(0)
diff['Difference'] = diff['SST'] - diff['SSJ']
diff_csv_path = 'data/results/proportional_differences.csv'
diff.to_csv(diff_csv_path)
print(f"\nProportional differences saved to: {diff_csv_path}")

# Heatmap for Differences
vmin, vmax = -max(abs(diff['Difference'])), max(abs(diff['Difference']))
plt.figure(figsize=(6, 8))
sns.heatmap(diff[['Difference']], annot=True, cmap='coolwarm', center=0, vmin=vmin, vmax=vmax)
plt.title('Difference in Word Order Proportions (SST - SSJ)')
heatmap_fig_path = 'data/results/word_order_proportions_difference_heatmap_zero_centered.png'
save_plot(heatmap_fig_path)
print(f"Heatmap of proportional differences saved to: {heatmap_fig_path}")

# Section 5: Continuous Analysis with Probabilistic Modeling
def fit_dirichlet(data, tol=1e-6, max_iter=1000):
    data = np.array(data)
    n, k = data.shape
    alpha = np.ones(k)
    for _ in range(max_iter):
        alpha_old = alpha
        g = n * (digamma(np.sum(alpha)) - digamma(alpha)) + np.sum(np.log(data), axis=0)
        h = -n * (digamma(np.sum(alpha) + 1) - digamma(alpha + 1))
        alpha = alpha_old - g / h
        alpha = np.maximum(alpha, 1e-6)
        if np.linalg.norm(alpha - alpha_old) < tol:
            break
    return alpha

ssj_proportions = pattern_counts[pattern_counts['Corpus'] == 'SSJ']['Proportion'].values.reshape(1, -1)
sst_proportions = pattern_counts[pattern_counts['Corpus'] == 'SST']['Proportion'].values.reshape(1, -1)
ssj_alpha = fit_dirichlet(ssj_proportions)
sst_alpha = fit_dirichlet(sst_proportions)
print("\nFitted Dirichlet parameters for SSJ:", ssj_alpha)
print("Fitted Dirichlet parameters for SST:", sst_alpha)

# Expected Proportions with Variability
ssj_expected = dirichlet.mean(ssj_alpha)
sst_expected = dirichlet.mean(sst_alpha)
fig, ax = plt.subplots(figsize=(8, 6))
patterns = pattern_counts['Pattern'].unique()
x = np.arange(len(patterns))
ax.bar(x - 0.2, ssj_expected, width=0.4, label='SSJ', yerr=dirichlet.var(ssj_alpha)**0.5)
ax.bar(x + 0.2, sst_expected, width=0.4, label='SST', yerr=dirichlet.var(sst_alpha)**0.5)
ax.set_xticks(x)
ax.set_xticklabels(patterns, rotation=45)
ax.set_title('Expected Proportions and Variability')
ax.set_ylabel('Proportion')
ax.legend()
ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
dirichlet_fig_path = 'data/results/dirichlet_expected_proportions.png'
save_plot(dirichlet_fig_path)
print(f"Dirichlet expected proportions plot saved to: {dirichlet_fig_path}")

# Section 6: Chi-Square Test
contingency_table = pattern_counts.pivot(index='Pattern', columns='Corpus', values='Count').fillna(0).astype(int)
chi2, p, dof, expected = chi2_contingency(contingency_table.values)
print("\nChi-Square Test Results:")
print(f"Chi-Square Statistic: {chi2}")
print(f"Degrees of Freedom: {dof}")
print(f"P-Value: {p}")

# Section 7: Bootstrap Confidence Intervals
def bootstrap_confidence_intervals(data, n_bootstrap=1000, alpha=0.05):
    boot_means = [np.mean(np.random.choice(data, size=len(data), replace=True)) for _ in range(n_bootstrap)]
    lower = np.percentile(boot_means, alpha / 2 * 100)
    upper = np.percentile(boot_means, (1 - alpha / 2) * 100)
    return lower, upper

ci_results = []
for pattern in pattern_counts['Pattern'].unique():
    for corpus in ['SSJ', 'SST']:
        subset = pattern_counts[(pattern_counts['Pattern'] == pattern) & (pattern_counts['Corpus'] == corpus)]
        proportions = subset['Proportion'].values
        if len(proportions) > 0:
            lower, upper = bootstrap_confidence_intervals(proportions)
            ci_results.append({'Pattern': pattern, 'Corpus': corpus, 'Lower CI': lower, 'Upper CI': upper})

ci_df = pd.DataFrame(ci_results)
ci_csv_path = 'data/results/bootstrap_confidence_intervals.csv'
ci_df.to_csv(ci_csv_path, index=False)
print(f"\nBootstrap confidence intervals saved to: {ci_csv_path}")
