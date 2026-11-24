
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# Al Eissa et al. (2022), Table 1, Feed C
# Quantities are for 1000 kg live shrimp.
ingredients = {
    "fish_meal": 450,
    "poultry_byproduct_meal": 75,
    "soybean_meal": 300,
    "wheat_flour": 450,
    "rice_bran": 75,
    "fish_oil": 45,
    "soybean_lecithin": 45,
    "supplements": 60,
}

df = pd.DataFrame(
    ingredients.items(),
    columns=["ingredient", "mass_kg"]
)

total_feed = df["mass_kg"].sum()

assert total_feed == 1500, "Feed mass balance failed"

# Normalize to 1 kg commercial feed
df["kg_per_kg_feed"] = df["mass_kg"] / total_feed

# Normalize to 1 kg live shrimp
df["kg_per_kg_shrimp"] = df["mass_kg"] / 1000

df["source"] = "Al Eissa et al. (2022), Table 1, Feed C"

output = DATA / "feed_c_lci.csv"
df.to_csv(output, index=False)

print("\nIndiana Biofloc - Feed C")
print(df.to_string(index=False))

print(f"\nTotal feed: {total_feed} kg")
print(f"FCR: {total_feed / 1000:.2f}")
print(f"Saved: {output}")
