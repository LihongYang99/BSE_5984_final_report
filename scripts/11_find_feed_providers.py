# Step 11: Find candidate background datasets for each Feed C ingredient.

from pathlib import Path
import csv
import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

# Al Eissa et al. (2022), Feed C
# Search terms are candidates, not approved substitutions.
ingredients = {
    "fish_meal": ["fishmeal", "fish meal"],
    "poultry_byproduct_meal": [
        "poultry by-product", "poultry meal", "chicken meal"
    ],
    "soybean_meal": ["soybean meal"],
    "wheat_flour": ["wheat flour"],
    "rice_bran": ["rice bran"],
    "fish_oil": ["fish oil"],
    "soybean_lecithin": ["lecithin"],
    "supplements": ["vitamin premix", "mineral premix"],
}

# Record the paper assumed origins as review targets, not verified supplier locations.
expected_origins = {
    "fish_meal": "Chile",
    "poultry_byproduct_meal": "Netherlands",
    "soybean_meal": "United States",
    "wheat_flour": "Belgium",
    "rice_bran": "China",
    "fish_oil": "Peru",
    "soybean_lecithin": "Netherlands",
    "supplements": "Not specified",
}

processes = client.get_descriptors(o.Process)

rows = []

# Search by ingredient name, then inspect up to 30 matching processes.
for ingredient, keywords in ingredients.items():

    matches = [
        p for p in processes
        if p.name and any(
            word in p.name.lower()
            for word in keywords
        )
    ]

    print(f"\n{ingredient}: {len(matches)} name matches")

    # Inspect matching processes without modifying the database
    for descriptor in matches[:30]:
        process = client.get(o.Process, descriptor.id)

        if process is None:
            continue

        refs = [
            ex for ex in (process.exchanges or [])
            if ex.is_quantitative_reference
            and not ex.is_input
        ]

        for ex in refs:
            rows.append({
                "ingredient": ingredient,
                "expected_origin": expected_origins[ingredient],
                "process_name": process.name,
                "location": getattr(
                    process.location, "name", ""
                ),
                "reference_product": getattr(
                    ex.flow, "name", ""
                ),
                "unit": getattr(ex.unit, "name", ""),
                "uuid": descriptor.id,
                "status": "PENDING_REVIEW",
            })

# Export candidate products and units with a pending-review label.
df_path = OUT / "feed_provider_candidates.csv"

with df_path.open(
    "w", newline="", encoding="utf-8"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "ingredient",
            "expected_origin",
            "process_name",
            "location",
            "reference_product",
            "unit",
            "uuid",
            "status",
        ]
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"\nSaved: {df_path}")
print(f"Candidate reference products: {len(rows)}")
print("Read-only search complete.")
