
from pathlib import Path
import pandas as pd

# =============================================
# Step 29 - Indiana Biofloc Farming LCI
# Source: Al Eissa et al. (2022), Table 2
# Functional unit: 1 kg live-weight shrimp
# =============================================

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# Original functional unit in the paper
ORIGINAL_SHRIMP_KG = 1000

records = [
    {
        "stage": "farming",
        "flow": "live_shrimp",
        "direction": "output",
        "original_amount": 1000,
        "unit": "kg",
        "status": "REFERENCE_PRODUCT",
    },
    {
        "stage": "farming",
        "flow": "feed_c",
        "direction": "input",
        "original_amount": 1500,
        "unit": "kg",
        "status": "HYBRID_FEED_MODEL_AVAILABLE",
    },
    {
        "stage": "farming",
        "flow": "electricity",
        "direction": "input",
        "original_amount": 921,
        "unit": "kWh",
        "status": "BACKGROUND_PROVIDER_AVAILABLE",
    },
    {
        "stage": "farming",
        "flow": "sodium_bicarbonate",
        "direction": "input",
        "original_amount": 110,
        "unit": "kg",
        "status": "PROXY_PROVIDER_AVAILABLE",
    },
    {
        "stage": "farming",
        "flow": "water_use",
        "direction": "input",
        "original_amount": 75,
        "unit": "m3",
        "status": "WATER_SOURCE_NEEDS_REVIEW",
    },
]

df = pd.DataFrame(records)

# Normalize all quantities to 1 kg live shrimp
df["amount_per_kg_shrimp"] = (
    df["original_amount"] / ORIGINAL_SHRIMP_KG
)

df["source"] = "Al Eissa et al. (2022), Table 2"
df["scenario"] = "Indiana_closed_biofloc"
df["system_boundary"] = "cradle-to-farm-gate"

# Basic verification
values = df.set_index("flow")["amount_per_kg_shrimp"]

assert abs(values["live_shrimp"] - 1.0) < 1e-9
assert abs(values["feed_c"] - 1.5) < 1e-9
assert abs(values["electricity"] - 0.921) < 1e-9
assert abs(values["sodium_bicarbonate"] - 0.110) < 1e-9
assert abs(values["water_use"] - 0.075) < 1e-9

output = DATA / "indiana_biofloc_farming_lci.csv"
df.to_csv(output, index=False)

print("\n=== INDIANA BIOFLOC FARMING LCI ===")
print(
    df[[
        "flow",
        "direction",
        "amount_per_kg_shrimp",
        "unit",
        "status"
    ]].to_string(index=False)
)

print("\nPASS: Inventory normalized to 1 kg shrimp")
print("Saved:", output)
print("No openLCA database changes.")
