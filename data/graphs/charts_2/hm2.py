import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

# === CONSTANTS & MAPPINGS ===
LANGUAGE_FAMILY = {
    "English": "Germanic",
    "Norwegian": "Germanic",
    "French": "Romance",
    "Spanish": "Romance",
    "Slovenian": "Slavic"
}

FAMILY_CMAPS = {
    "Germanic": LinearSegmentedColormap.from_list("Germanic", ["#e1eff6", "#08306b"]),
    "Romance":  LinearSegmentedColormap.from_list("Romance",  ["#fde5d0", "#b30000"]),
    "Slavic":   LinearSegmentedColormap.from_list("Slavic",   ["#e3f2e1", "#005a32"])
}

COLUMN_ORDER = [
    "English Written", "English Spoken",
    "French Written", "French Spoken",
    "Norwegian Written (bokmaal)", "Norwegian Written (nynorsk)", "Norwegian Spoken (nynorsk)",
    "Slovenian Written", "Slovenian Spoken",
    "Spanish Written", "Spanish Spoken"
]

BASE_LABELS = [
    "English\n(W)", "English\n(S)",
    "French\n(W)", "French\n(S)",
    "Norwegian\nBokmål\n(W)", "Norwegian\nNynorsk\n(W)", "Norwegian\nNynorsk\n(S)",
    "Slovenian\n(W)", "Slovenian\n(S)",
    "Spanish\n(W)", "Spanish\n(S)"
]

# === HELPER FUNCTIONS ===
def identify_language(col_name):
    for lang in LANGUAGE_FAMILY.keys():
        if lang in col_name:
            return lang
    return None

def luminance(rgba_color):
    r, g, b, _ = rgba_color
    return 0.299 * r + 0.587 * g + 0.114 * b

def draw_heatmap(ax, heatmap_data):
    nrows, ncols = heatmap_data.shape
    for row in range(nrows):
        for col in range(ncols):
            value = heatmap_data.iloc[row, col]
            col_name = heatmap_data.columns[col]
            lang = identify_language(col_name)
            fam = LANGUAGE_FAMILY.get(lang)
            cmap = FAMILY_CMAPS.get(fam, plt.get_cmap("Greys"))
            color = cmap(value)
            text_color = 'white' if luminance(color) < 0.5 else 'black'

            rect = plt.Rectangle((col, row), 1, 1, facecolor=color, edgecolor="white", linewidth=0.5)
            ax.add_patch(rect)
            ax.text(col + 0.5, row + 0.5, f"{value:.1%}", ha="center", va="center", fontsize=10, color=text_color)

# === MAIN PLOTTING FUNCTION ===
def create_custom_heatmap(df, title, filename):
    # Prepare data
    melted = df.melt(id_vars="Word Order", var_name="Language-Modality", value_name="Proportion")
    heatmap_data = melted.pivot(index="Word Order", columns="Language-Modality", values="Proportion")
    heatmap_data = heatmap_data[COLUMN_ORDER]
    heatmap_data = heatmap_data.loc[heatmap_data.mean(axis=1).sort_values(ascending=False).index]

    # Setup plot
    fig, ax = plt.subplots(figsize=(10, 7), facecolor='white')
    plt.subplots_adjust(top=0.72)
    ax.set_frame_on(False)

    draw_heatmap(ax, heatmap_data)

    # Configure axes
    ax.set_xlim(0, heatmap_data.shape[1])
    ax.set_ylim(0, heatmap_data.shape[0])
    ax.invert_yaxis()

    ax.set_xticks([i + 0.5 for i in range(heatmap_data.shape[1])])
    ax.set_xticklabels(BASE_LABELS, fontsize=10, rotation=0)

    ax.set_yticks([i + 0.5 for i in range(heatmap_data.shape[0])])
    ax.set_yticklabels(heatmap_data.index.tolist(), fontsize=10)

    ax.set_title(title, fontsize=14, pad=30)
    ax.set_xlabel("Language (W = Written, S = Spoken)", fontsize=11, labelpad=15)
    ax.set_ylabel("Word Order", fontsize=11, labelpad=15)

    # Add legend
    legend_handles = [
        mpatches.Patch(color=FAMILY_CMAPS[family](1.0), label=family)
        for family in FAMILY_CMAPS
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.95),
        ncol=3,
        frameon=False
    )

    # Clean up borders and ticks
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(top=False, bottom=False, left=False, right=False)

    # Save figure
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"{title} heatmap saved to {filename}!")

# === RAW DATA ===
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

# === PLOT BOTH HEATMAPS ===
create_custom_heatmap(
    pd.DataFrame(svo_data),
    "Distribution of Word Order Patterns Across Languages and Modalities",
    "data/graphs/charts_2/custom_heatmap_svo.png"
)

create_custom_heatmap(
    pd.DataFrame(vo_data),
    "Distribution of Verb–Object (VO) vs. Object–Verb (OV) Patterns Across Languages and Modalities",
    "data/graphs/charts_2/custom_heatmap_vo.png"
)

print("Both custom heatmaps saved!")

# === END OF FILE ===