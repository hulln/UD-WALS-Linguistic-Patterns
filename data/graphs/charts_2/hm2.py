import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# === SVO DATA ===
svo_data = {
    "Word Order": ["SVO", "SOV", "OSV", "OVS", "VSO", "VOS"],
    "French Written": [0.8449, 0.1016, 0.0407, 0.0098, 0.0023, 0.0006],
    "French Spoken": [0.7115, 0.1905, 0.0868, 0.0093, 0.0019, 0],
    "English Written": [0.9737, 0, 0.0263, 0, 0, 0],
    "English Spoken": [0.9295, 0.0013, 0.0688, 0.0004, 0, 0],
    "Slovenian Written": [0.5453, 0.1093, 0.0852, 0.2114, 0.0276, 0.0212],
    "Slovenian Spoken": [0.3916, 0.2084, 0.1557, 0.1737, 0.0467, 0.0240],
    "Spanish Written": [0.8454, 0.0615, 0.0206, 0.0552, 0.0038, 0.0136],
    "Spanish Spoken": [0.4628, 0.2066, 0.0413, 0.1983, 0.0496, 0.0413],
    "Norwegian Written (bokmaal)": [0.8386, 0.0008, 0.0290, 0.0195, 0.1111, 0.0009],
    "Norwegian Written (nynorsk)": [0.8233, 0.0005, 0.0270, 0.0219, 0.1250, 0.0022],
    "Norwegian Spoken (nynorsk)": [0.5948, 0.0093, 0.1235, 0.0975, 0.1736, 0.0013]
}

# === VO/OV DATA ===
vo_data = {
    "Word Order": ["VO", "OV"],
    "English Written": [0.984394396, 0.015605604],
    "English Spoken": [0.952143045, 0.047856955],
    "French Written": [0.85397116, 0.14602884],
    "French Spoken": [0.742327736, 0.257672264],
    "Norwegian Written (bokmaal)": [0.966821843, 0.033178157],
    "Norwegian Written (nynorsk)": [0.966642495, 0.033357505],
    "Norwegian Spoken (nynorsk)": [0.809819121, 0.190180879],
    "Slovenian Written": [0.627361447, 0.372638553],
    "Slovenian Spoken": [0.496921724, 0.503078276],
    "Spanish Written": [0.90632685, 0.09367315],
    "Spanish Spoken": [0.620481928, 0.379518072]
}

# === Common settings ===
column_order = [
    "English Written", "English Spoken",
    "French Written", "French Spoken",
    "Norwegian Written (bokmaal)", "Norwegian Written (nynorsk)", "Norwegian Spoken (nynorsk)",
    "Slovenian Written", "Slovenian Spoken",
    "Spanish Written", "Spanish Spoken"
]
base_labels = [
    "English (W)", "English (S)",
    "French (W)", "French (S)",
    "Norwegian Bokmål (W)", "Norwegian Nynorsk (W)", "Norwegian Nynorsk (S)",
    "Slovenian (W)", "Slovenian (S)",
    "Spanish (W)", "Spanish (S)"
]

def create_heatmap(df, title, filename):
    melted = df.melt(id_vars="Word Order", var_name="Language-Modality", value_name="Proportion")
    heatmap_data = melted.pivot(index="Word Order", columns="Language-Modality", values="Proportion")
    heatmap_data = heatmap_data[column_order]

    heatmap_data = heatmap_data.loc[heatmap_data.mean(axis=1).sort_values(ascending=False).index]
    formatted_values = heatmap_data.applymap(lambda x: f"{x:.1%}")

    plt.figure(figsize=(13, 7), facecolor='white')  # Back to original height
    sns.set(style="white", font_scale=1.05)

    ax = sns.heatmap(
        heatmap_data,
        annot=formatted_values,
        fmt='',
        cmap="Blues",
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Proportion", "shrink": 0.8},
        annot_kws={"size": 10},
        vmin=0,
        vmax=1
    )

    ax.collections[0].colorbar.ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{x:.0%}')
    )

    ax.set_xticklabels(base_labels, rotation=45, ha="right", fontsize=10)
    plt.title(title, fontsize=14, pad=20)
    plt.xlabel("Language (W = Written, S = Spoken)", labelpad=15, fontsize=11)
    plt.ylabel("Word Order", labelpad=15, fontsize=11)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"{title} heatmap saved to {filename}!")


# Create both heatmaps
create_heatmap(
    pd.DataFrame(svo_data),
    "Distribution of Word Order Patterns (SVO, SOV, etc.) Across Languages and Modalities",
    "data/graphs/charts_2/heatmap_svo.png"
)

create_heatmap(
    pd.DataFrame(vo_data),
    "Distribution of Verb–Object (VO) vs. Object–Verb (OV) Patterns Across Languages and Modalities",
    "data/graphs/charts_2/heatmap_vo.png"
)

print("Both heatmaps saved!")