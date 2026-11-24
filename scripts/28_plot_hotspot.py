# Step 28: Combine feed ingredient, processing, and delivery results into hotspot shares.

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# =========================================
# STEP 28 - Feed C Environmental Hotspots
# Read calculated results, do not modify LCA
# =========================================

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = ROOT / "figures"

OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

# Load results from previous steps
v2 = pd.read_csv(
    OUT / "feed_c_v2_proxy_summary.csv"
)

processing = pd.read_csv(
    OUT / "feed_processing_transport_gwp.csv"
)

# Select the main V2 scenario, not Campos sensitivity
selected = v2.loc[
    v2["scenario"] == "V2 100%-mass proxy hybrid",
    "gwp_per_kg_nominal_feed"
]

if len(selected) != 1:
    raise RuntimeError(
        "Cannot uniquely identify the V2 proxy scenario"
    )

ingredient_gwp = float(selected.iloc[0])

stage_values = processing.set_index(
    "stage"
)["gwp_per_kg_feed"]

required_stages = [
    "steam",
    "electricity",
    "tap_water",
    "truck_transport"
]

# Require every modeled processing stage before building the combined total.
for stage in required_stages:
    if stage not in stage_values.index:
        raise RuntimeError(f"Missing stage: {stage}")

components = {
    "Ingredients (proxy hybrid)": ingredient_gwp,
    "Steam": float(stage_values["steam"]),
    "Electricity": float(stage_values["electricity"]),
    "Tap water": float(stage_values["tap_water"]),
    "Feed transport": float(stage_values["truck_transport"]),
}

df = pd.DataFrame([
    {
        "component": name,
        "gwp_per_kg_feed": value,
    }
    for name, value in components.items()
])

# Calculate each stage share and scale the feed total to the shrimp basis.
total = df["gwp_per_kg_feed"].sum()
df["share_pct"] = 100 * df["gwp_per_kg_feed"] / total

FCR = 1.5
gwp_per_kg_shrimp = total * FCR

print("\n=== FEED C HOTSPOT ANALYSIS ===")
print(df.to_string(index=False))

print(f"\nTotal screening GWP: {total:.6f} kg CO2-eq/kg feed")
print(
    f"Feed-related screening GWP: "
    f"{gwp_per_kg_shrimp:.6f} kg CO2-eq/kg shrimp"
)

# Save consolidated data
df.to_csv(
    OUT / "feed_c_hotspot_analysis.csv",
    index=False
)

# =========================================
# Figure: horizontal contribution chart
# =========================================

# Sort contributions for the hotspot chart; plotting does not rerun LCIA.
df_plot = df.sort_values(
    "gwp_per_kg_feed",
    ascending=True
)

fig, ax = plt.subplots(figsize=(9, 5.5))

bars = ax.barh(
    df_plot["component"],
    df_plot["gwp_per_kg_feed"]
)

for bar, percent in zip(
    bars,
    df_plot["share_pct"]
):
    ax.text(
        bar.get_width() + total * 0.012,
        bar.get_y() + bar.get_height() / 2,
        f"{percent:.1f}%",
        va="center",
        fontsize=10
    )

ax.set_xlim(
    0,
    df_plot["gwp_per_kg_feed"].max() * 1.25
)

ax.set_xlabel(
    "GWP (kg CO2-eq/kg nominal feed)"
)

ax.set_title(
    "Feed C Supply Chain: GWP Hotspots"
)

ax.text(
    0.5, -0.17,
    "Proxy-based hybrid screening model; "
    "not a fully harmonized LCA",
    transform=ax.transAxes,
    ha="center",
    fontsize=9
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()

fig.savefig(
    FIG / "fig07_feed_c_hotspots.png",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    FIG / "fig07_feed_c_hotspots.pdf",
    bbox_inches="tight"
)

plt.close(fig)

print("\nFigure saved successfully.")
print("Note: Background proxies and GWP need validation.")
