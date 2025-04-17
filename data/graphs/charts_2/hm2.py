import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import matplotlib.cm as cm

# === CONSTANTS ===

BLUE_CMAP = LinearSegmentedColormap.from_list("BlueScale", ["#e1eff6", "#08306b"])

LANGUAGE_GROUPS = [
    ["English Written", "English Spoken"],
    ["French Written", "French Spoken"],
    ["Norwegian Written (nynorsk)", "Norwegian Spoken (nynorsk)"],
    ["Slovenian Written", "Slovenian Spoken"],
    ["Spanish Written", "Spanish Spoken"]
]

COLUMN_ORDER = [col for group in LANGUAGE_GROUPS for col in group]
BASE_LABELS = [
    "English\n(W)", "English\n(S)",
    "French\n(W)", "French\n(S)",
    "Norwegian\nNynorsk\n(W)", "Norwegian\nNynorsk\n(S)",
    "Slovenian\n(W)", "Slovenian\n(S)",
    "Spanish\n(W)", "Spanish\n(S)"
]

# === HELPER FUNCTIONS ===

def luminance(rgba_color):
    r, g, b, _ = rgba_color
    return 0.299 * r + 0.587 * g + 0.114 * b

def draw_heatmap(ax, heatmap_data, col_positions):
    nrows, ncols = heatmap_data.shape
    for row in range(nrows):
        for col_idx, col_name in enumerate(heatmap_data.columns):
            value = heatmap_data.iloc[row, col_idx]
            color = BLUE_CMAP(value)
            text_color = 'white' if luminance(color) < 0.5 else 'black'
            xpos = col_positions[col_idx]

            rect = plt.Rectangle((xpos, row), 1, 1, facecolor=color, edgecolor="white", linewidth=0.5)
            ax.add_patch(rect)
            ax.text(xpos + 0.5, row + 0.5, f"{value:.1%}", ha="center", va="center", fontsize=10, color=text_color)

# === MAIN PLOTTING FUNCTION ===

def create_custom_heatmap(df, title, filename):
    melted = df.melt(id_vars="Word Order", var_name="Language-Modality", value_name="Proportion")
    heatmap_data = melted.pivot(index="Word Order", columns="Language-Modality", values="Proportion")
    heatmap_data = heatmap_data[COLUMN_ORDER]
    heatmap_data = heatmap_data.loc[heatmap_data.mean(axis=1).sort_values(ascending=False).index]

    # Calculate column x-positions with spacing between groups
    group_spacing = 0.2  # adjust this for more or less space
    col_positions = []
    xpos = 0
    for group in LANGUAGE_GROUPS:
        for _ in group:
            col_positions.append(xpos)
            xpos += 1
        xpos += group_spacing

    # Set up figure and axis
    fig = plt.figure(figsize=(11, 7), facecolor='white')
    ax = fig.add_axes([0.1, 0.1, 0.75, 0.8])  # [left, bottom, width, height]

    draw_heatmap(ax, heatmap_data, col_positions)

    ax.set_xlim(0, max(col_positions) + 1)
    ax.set_ylim(0, heatmap_data.shape[0])
    ax.invert_yaxis()
    ax.set_aspect('equal')  # Make all tiles square

    ax.set_xticks([x + 0.5 for x in col_positions])
    ax.set_xticklabels(BASE_LABELS, fontsize=10, rotation=0)

    ax.set_yticks([i + 0.5 for i in range(heatmap_data.shape[0])])
    ax.set_yticklabels(heatmap_data.index.tolist(), fontsize=10)

    ax.set_title(title, fontsize=14, pad=30)
    ax.set_xlabel("Language (W = Written, S = Spoken)", fontsize=11, labelpad=15)
    ax.set_ylabel("Word Order", fontsize=11, labelpad=15)

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(top=False, bottom=False, left=False, right=False)

    # === Colorbar perfectly aligned with tile grid ===
    heatmap_box = ax.get_position()
    cbar_width = 0.02
    cbar_padding = 0.02

    cbar_ax = fig.add_axes([
        heatmap_box.x1 + cbar_padding,  # x
        heatmap_box.y0,                 # y
        cbar_width,                     # width
        heatmap_box.height              # height
    ])

    sm = cm.ScalarMappable(cmap=BLUE_CMAP, norm=plt.Normalize(vmin=0, vmax=1))
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.ax.set_ylabel('Proportion', rotation=270, labelpad=15)
    cbar.outline.set_visible(False)
    cbar.ax.set_yticklabels([f"{int(t * 100)}%" for t in cbar.get_ticks()])

    # Save and finish
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"{title} heatmap saved to {filename}!")

# === RAW DATA: SVO ===

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
    "Norwegian Written (nynorsk)": [0.8233, 0.0005, 0.0270, 0.0219, 0.1250, 0.0022],
    "Norwegian Spoken (nynorsk)": [0.5948, 0.0093, 0.1235, 0.0975, 0.1736, 0.0013]
}

# === GENERATE THE SVO HEATMAP ===

create_custom_heatmap(
    pd.DataFrame(svo_data),
    "Distribution of Word Order Patterns Across Languages and Modalities",
    "data/graphs/charts_2/custom_heatmap_svo.png"
)

print("SVO heatmap saved!")
