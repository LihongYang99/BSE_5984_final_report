
from pathlib import Path
import csv

import olca_ipc as ipc
import olca_schema as o

# =========================================
# STEP 19 - Find remaining feed LCI routes
# Read-only: no database modifications
# =========================================

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

SEARCH_GROUPS = {
    "rice_bran": {
        "keywords": [
            "rice bran",
            "rice milling",
            "rice grain",
            "paddy",
            "rice processing",
            "rice husk",
        ],
        "preferred": [
            "rice bran",
            "rice milling",
            "rice grain processing",
        ],
        "exact_product": "rice bran",
    },
    "soybean_lecithin": {
        "keywords": [
            "lecithin",
            "degumming",
            "soybean oil",
            "soybean processing",
            "oil refining",
        ],
        "preferred": [
            "lecithin",
            "degumming",
            "soybean oil refining",
        ],
        "exact_product": "lecithin",
    },
}

print("Reading ecoinvent process descriptors...")

processes = client.get_descriptors(o.Process)
rows = []

for ingredient, config in SEARCH_GROUPS.items():

    matches = [
        p for p in processes
        if p.name and any(
            term in p.name.lower()
            for term in config["keywords"]
        )
    ]

    def priority(descriptor):
        name = (descriptor.name or "").lower()
        return (
            -sum(
                term in name
                for term in config["preferred"]
            ),
            name,
        )

    matches.sort(key=priority)

    print(f"\n=== {ingredient.upper()} ===")
    print(f"Name matches: {len(matches)}")

    # Inspect a bounded set of relevant candidates
    for descriptor in matches[:60]:

        process = client.get(o.Process, descriptor.id)

        if process is None:
            continue

        reference_outputs = [
            ex for ex in (process.exchanges or [])
            if ex.is_quantitative_reference
            and not ex.is_input
        ]

        for ex in reference_outputs:

            product = (
                ex.flow.name
                if ex.flow else ""
            )

            unit = (
                ex.unit.name
                if ex.unit else ""
            )

            is_exact = (
                config["exact_product"]
                in product.lower()
            )

            status = (
                "EXACT_PRODUCT_CANDIDATE"
                if is_exact
                else "UPSTREAM_ONLY_REVIEW"
            )

            row = {
                "ingredient": ingredient,
                "process_name": process.name,
                "location": getattr(
                    process.location,
                    "name",
                    ""
                ),
                "reference_product": product,
                "unit": unit,
                "uuid": process.id,
                "status": status,
            }

            rows.append(row)

            print(
                f"{status} | "
                f"{product} | "
                f"{row['location']}"
            )

output = OUT / "remaining_feed_routes.csv"

with output.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "ingredient",
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

print("\n=== COMPLETE ===")
print("Candidates reviewed:", len(rows))
print("Saved:", output)
print("No database changes made.")
