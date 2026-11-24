# Step 23: Normalize feed-processing and delivery inputs from the literature inventory.

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# Al Eissa et al. (2022), Table 2
# Inventory per 1000 kg live shrimp
SHRIMP_KG = 1000
FEED_KG = 1500

# Retain the original quantities and units reported for 1000 kg live shrimp.
records = [
    ("feed_processing", "steam", 480, "kg"),
    ("feed_processing", "electricity", 195, "kWh"),
    ("feed_processing", "freshwater", 2.0, "m3"),
    ("feed_processing", "land_area", 2.1, "m2"),
    ("feed_transport", "diesel_truck", 1509, "t*km"),
]

df = pd.DataFrame(
    records,
    columns=["stage", "input", "original_amount", "unit"]
)

# Express each input on both the feed basis and the shrimp basis.
df["amount_per_kg_feed"] = (
    df["original_amount"] / FEED_KG
)

df["amount_per_kg_shrimp"] = (
    df["original_amount"] / SHRIMP_KG
)

df["source"] = "Al Eissa et al. (2022), Table 2"

# Save physical quantities only; emission factors are applied in later steps.
output = DATA / "feed_c_processing_transport_lci.csv"
df.to_csv(output, index=False)

print("\n=== FEED PROCESSING AND TRANSPORT LCI ===")
print(df.to_string(index=False))
print(f"\nSaved: {output}")
print("No openLCA database changes.")
