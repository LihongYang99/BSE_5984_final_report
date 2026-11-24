
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"

DATA.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

# Missing ingredients in Feed C
# Based on Al Eissa et al. (2022), Table 1
records = [
    {
        "ingredient": "poultry_byproduct_meal",
        "mass_fraction": 0.05,
        "data_source": "Campos et al. (2020)",
        "candidate_method": "Literature EF or ecoinvent proxy",
        "status": "PROXY_TESTED",
        "notes": "Meat and bone meal is not equivalent to PBM"
    },
    {
        "ingredient": "rice_bran",
        "mass_fraction": 0.05,
        "data_source": "Henriksson et al. (2017)",
        "candidate_method": "Literature-based LCI or EF",
        "status": "NEEDS_REVIEW",
        "notes": "Verify allocation, geography and GWP method"
    },
    {
        "ingredient": "soybean_lecithin",
        "mass_fraction": 0.03,
        "data_source": "USDA (2023)",
        "candidate_method": "Degumming process model",
        "status": "NEEDS_MODEL",
        "notes": "Soybean oil is not equivalent to lecithin"
    },
    {
        "ingredient": "supplements",
        "mass_fraction": 0.04,
        "data_source": "Al Eissa et al. (2022)",
        "candidate_method": "Ingredient uncertainty scenario",
        "status": "COMPOSITION_UNKNOWN",
        "notes": "Do not assume zero environmental impact"
    }
]

df = pd.DataFrame(records)

df["kg_per_kg_shrimp"] = (
    df["mass_fraction"] * 1.5
)

# No emission factors are invented at this stage.
df["gwp_kg_co2eq_per_kg"] = float("nan")

output = DATA / "feed_c_missing_data_register.csv"
df.to_csv(output, index=False)

print(df.to_string(index=False))
print("\nTotal missing fraction:",
      f"{df['mass_fraction'].sum():.0%}")

print("Saved:", output)
print("No openLCA database changes.")
