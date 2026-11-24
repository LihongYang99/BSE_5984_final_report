# Step 21: Explore hypothetical rice-bran factors around the historical partial-feed result.

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

# Previously calculated partial Feed C inventory
BASELINE_GWP = 0.816535
RICE_BRAN_FRACTION = 0.05
FCR = 1.5

# Hypothetical values for sensitivity testing only
# NOT literature-derived emission factors
ef_values = np.linspace(0.5, 3.0, 26)

df = pd.DataFrame({
    "assumed_rice_bran_ef": ef_values
})

# Add the assumed rice-bran burden to the partial model and scale it by FCR.
df["rice_bran_contribution"] = (
    RICE_BRAN_FRACTION * df["assumed_rice_bran_ef"]
)

df["partial_feed_gwp"] = (
    BASELINE_GWP + df["rice_bran_contribution"]
)

df["partial_feed_gwp_per_kg_shrimp"] = (
    df["partial_feed_gwp"] * FCR
)

df["scenario_type"] = "HYPOTHETICAL_ONLY"

# Save each hypothetical factor and its calculated outcome for traceability.
df.to_csv(
    OUT / "rice_bran_sensitivity.csv",
    index=False
)

# Plot the sensitivity against the unchanged partial baseline.
fig, ax = plt.subplots(figsize=(7, 4.5))

ax.plot(
    df["assumed_rice_bran_ef"],
    df["partial_feed_gwp"],
    marker="o",
    markersize=3
)

ax.axhline(
    BASELINE_GWP,
    linestyle="--",
    label="83% partial baseline"
)

ax.set_xlabel(
    "Assumed rice bran GWP (kg CO2-eq/kg rice bran)"
)
ax.set_ylabel(
    "Partial ingredient GWP (kg CO2-eq/kg nominal feed)"
)
ax.set_title(
    "Sensitivity to Rice Bran Emission Factor"
)
ax.legend()
ax.grid(alpha=0.2)

fig.tight_layout()

fig.savefig(
    FIG / "fig05_rice_bran_sensitivity.png",
    dpi=300
)
fig.savefig(
    FIG / "fig05_rice_bran_sensitivity.pdf"
)

plt.close(fig)

print(df.to_string(index=False))
print("\nScenario analysis completed.")
print("WARNING: Assumed factors are hypothetical.")
print("Not a complete feed LCA.")
