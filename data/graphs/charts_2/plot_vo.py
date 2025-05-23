import pandas as pd
import matplotlib.pyplot as plt

# VO/OV data
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

# Create DataFrame and format labels
df = pd.DataFrame(vo_data).set_index("Word Order").T

# Rename rows to match the "Language (W/S)" format
label_map = {
    "English Written": "English (W)",
    "English Spoken": "English (S)",
    "French Written": "French (W)",
    "French Spoken": "French (S)",
    "Norwegian Written (bokmaal)": "Norwegian Bokmål (W)",
    "Norwegian Written (nynorsk)": "Norwegian Nynorsk (W)",
    "Norwegian Spoken (nynorsk)": "Norwegian Nynorsk (S)",
    "Slovenian Written": "Slovenian (W)",
    "Slovenian Spoken": "Slovenian (S)",
    "Spanish Written": "Spanish (W)",
    "Spanish Spoken": "Spanish (S)"
}
df.index = df.index.map(label_map)

# Optional: sort by VO dominance
df = df.sort_values(by="VO", ascending=True)

# Muted and accessible color palette
vo_color = "#5b8fa8"  # Muted blue
ov_color = "#c66b5d"  # Muted red

# Plot
plt.figure(figsize=(11, 8), facecolor="white")
plt.barh(df.index, df["VO"], color=vo_color, label="VO")
plt.barh(df.index, df["OV"], left=df["VO"], color=ov_color, label="OV")

# Format
plt.xlabel("Proportion", fontsize=11)
plt.title("Verb–Object (VO) vs. Object–Verb (OV) Word Order by Language and Modality", fontsize=14, pad=30)
plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.tick_params(axis='y', length=0)
plt.tick_params(axis='x', length=0)

# Remove chart borders
ax = plt.gca()
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)

# Legend centered under the title
plt.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.03),
    ncol=2,
    frameon=False
)

# Disclaimer text below x-axis
plt.figtext(0.5, -0.03, "W = written, S = spoken", ha="center", fontsize=9, style="italic")

# Save
plt.tight_layout()
plt.savefig("data/graphs/charts_2/stacked_vo_ov_horizontal.png", dpi=300, bbox_inches="tight")
plt.close()
print("Horizontal stacked bar chart for VO/OV saved with updated colors!")
