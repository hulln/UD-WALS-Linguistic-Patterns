import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Data as a dictionary
data = {
    'Word Order': ['SVO', 'SOV', 'OSV', 'OVS', 'VSO', 'VOS'],
    'French Written': [0.844908007, 0.10158072, 0.040684115, 0.009847111, 0.00233221, 0.000647836],
    'French Spoken': [0.711484594, 0.19047619, 0.086834734, 0.009337068, 0.001867414, 0],
    'English Written': [0.973720137, 0, 0.026279863, 0, 0, 0],
    'English Spoken': [0.929476351, 0.001266892, 0.068834459, 0.000422297, 0, 0],
    'Slovenian Written': [0.545291709, 0.10926305, 0.085209826, 0.21136131, 0.027635619, 0.021238485],
    'Slovenian Spoken': [0.391616766, 0.208383234, 0.155688623, 0.173652695, 0.046706587, 0.023952096],
    'Spanish Written': [0.845420326, 0.061480552, 0.020577164, 0.055207026, 0.003764115, 0.013550816],
    'Spanish Spoken': [0.462809917, 0.20661157, 0.041322314, 0.198347107, 0.049586777, 0.041322314],
    'Norwegian Written (bokmaal)': [0.838648935, 0.00082382, 0.028951395, 0.019536307, 0.111098035, 0.000941509],
    'Norwegian Written (nynorsk)': [0.823314643, 0.00052158, 0.026991785, 0.021906376, 0.125048898, 0.002216717],
    'Norwegian Spoken (nynorsk)': [0.594793057, 0.009345794, 0.123497997, 0.097463284, 0.173564753, 0.001335113],
}

# Convert to DataFrame
df = pd.DataFrame(data)
df.set_index('Word Order', inplace=True)

# Transpose for plotting
df_t = df.T

# Create and save heatmap
plt.figure(figsize=(12, 7))
sns.heatmap(df_t, annot=True, fmt=".2f", cmap="YlGnBu", cbar_kws={'label': 'Proportion'})
plt.title("Heatmap of Word Order Proportions by Language Variant")
plt.ylabel("Language Variant")
plt.xlabel("Word Order")
plt.xticks(rotation=45)
plt.tight_layout()

# Save only heatmap
plt.savefig("data/graphs/charts_2/heatmap.png", dpi=300, bbox_inches="tight")
plt.close()

print("Heatmap saved!")