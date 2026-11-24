from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
FIG = ROOT / "figures"

OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

# Electricity GWP from your openLCA calculation
ELECTRICITY_GWP = 0.1353780587964153  # kg CO2-eq / kWh

# Foreground LCI from Al Eissa et al. (2022), Table 2
df = pd.DataFrame([
    {
        "system": "Indiana Biofloc",
        "electricity_kwh_per_kg": 0.921
    },
    {
        "system": "Alabama Pond",
        "electricity_kwh_per_kg": 8.799
    }
])

df["electricity_gwp_kg_co2eq_per_kg"] = (
    df["electricity_kwh_per_kg"] * ELECTRICITY_GWP
)

csv_path = OUT / "electricity_only_shrimp_gwp.csv"
df.to_csv(csv_path, index=False)

print("\nElectricity-only GWP results:")
print(df.to_string(index=False))
print(f"\nSaved CSV: {csv_path}")

# Plot
fig, ax = plt.subplots(figsize=(7, 4.8))

bars = ax.bar(
    df["system"],
    df["electricity_gwp_kg_co2eq_per_kg"],
    width=0.55
)

ax.bar_label(bars, fmt="%.3f", padding=4)
ax.set_ylabel("Electricity-related GWP (kg CO2-eq/kg live shrimp)")
ax.set_title("Electricity-related GWP of U.S. Shrimp Farming Systems")
ax.set_ylim(0, df["electricity_gwp_kg_co2eq_per_kg"].max() * 1.2)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()

png_path = FIG / "fig04_electricity_only_shrimp_gwp.png"
pdf_path = FIG / "fig04_electricity_only_shrimp_gwp.pdf"

fig.savefig(png_path, dpi=300, bbox_inches="tight")
fig.savefig(pdf_path, bbox_inches="tight")
plt.close(fig)

print(f"Saved figure: {png_path}")
print(f"Saved figure: {pdf_path}")