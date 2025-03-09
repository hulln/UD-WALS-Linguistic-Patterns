import plotly.express as px
import pandas as pd

# ✅ Define your data
data = {
    "Language": ["French Written", "French Spoken", "English Written", "English Spoken", "Slovenian Written", "Slovenian Spoken"],
    "SVO": [0.8449, 0.7115, 0.9737, 0.9295, 0.5453, 0.3916],
    "SOV": [0.1016, 0.1905, 0.0000, 0.0000, 0.1093, 0.2084],
    "OSV": [0.0407, 0.0868, 0.0263, 0.0688, 0.0852, 0.1557],
    "OVS": [0.0098, 0.0093, 0.0000, 0.0013, 0.2114, 0.1737],
    "VSO": [0.0023, 0.0019, 0.0000, 0.0000, 0.0276, 0.0467],
    "VOS": [0.0006, 0.0000, 0.0000, 0.0000, 0.0212, 0.0239]
}

# ✅ Convert data to DataFrame
df = pd.DataFrame(data)

# ✅ Melt the DataFrame for Plotly (for stacked bars)
df_melted = df.melt(id_vars="Language", var_name="Word Order", value_name="Proportion")

# ✅ Define **custom colors** for the word order types
custom_colors = {
    "SVO": "#1f77b4",  # Blue
    "SOV": "#ff7f0e",  # Orange
    "OSV": "#2ca02c",  # Green
    "OVS": "#d62728",  # Red
    "VSO": "#9467bd",  # Purple
    "VOS": "#8c564b"   # Brown
}

# ✅ Create stacked bar chart with **original structure + custom colors**
fig = px.bar(df_melted, x="Language", y="Proportion", color="Word Order",
             title="Word Order Proportions in Spoken vs. Written Corpora",
             barmode="stack",
             color_discrete_map=custom_colors)  # Apply the color scheme

# ✅ Save as interactive HTML and static PNG
fig.write_html("data/results_mar25/chart_final.html")
fig.write_image("data/results_mar25/chart_final.png")

print("Chart saved! Open 'data/results_mar25/chart_final.html' for interactive version.")
