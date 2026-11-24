# Step 04: Plot physical electricity and feed demand before impact assessment.

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)

# Read both farming cases from the prepared inventory.
df = pd.read_csv(DATA_DIR / "us_lci_baseline.csv")

# Reuse the same chart layout for the electricity and feed comparisons.
def make_plot(column, ylabel, filename, title):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    bars = ax.bar(
        df["system"],
        df[column],
        width=0.55
    )

    ax.bar_label(bars, fmt="%.3f", padding=4)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_ylim(0, df[column].max() * 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()

    # Export a high-resolution PNG and a vector PDF for each chart.
    fig.savefig(
        FIG_DIR / f"{filename}.png",
        dpi=300,
        bbox_inches="tight"
    )
    fig.savefig(
        FIG_DIR / f"{filename}.pdf",
        bbox_inches="tight"
    )

    plt.close(fig)
    print(f"Saved: {filename}")

# Generate one plot per physical input; these are not GWP results.
make_plot(
    "electricity_kwh_per_kg",
    "Electricity (kWh/kg live shrimp)",
    "fig01_US_electricity",
    "Farming Electricity Consumption"
)

make_plot(
    "feed_kg_per_kg",
    "Feed (kg/kg live shrimp)",
    "fig02_US_feed",
    "Feed Consumption"
)

print("\nAll figures generated successfully!")
