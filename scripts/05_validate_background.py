# Step 05: Review shortlisted background providers and search for bicarbonate.

from pathlib import Path
import csv

import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

# Shortlist extracted from your ecoinvent 3.11 CSV files
candidates = {
    "electricity_US": "483cde5f-7ae5-379e-ae10-54bb8fbbe6a2",
    "electricity_US_SERC": "9c9cc538-9fae-3f22-b413-517fc1b88b3f",
    "electricity_US_RFC": "b217ab31-ead1-3015-80c3-c24d6d33e38d",
    "soybean_meal_US": "355ad6bb-9864-3a8b-a369-39d41b991538",
    "wheat_flour_RoW": "ff154541-8003-3e3c-b66b-1bc7e4a05fc3",
    "fishmeal_Peru": "e65f571f-8fcc-3aff-8893-6433e9b2795a",
}

rows = []

# Inspect each provider reference product, unit, and geography.
for label, uid in candidates.items():
    process = client.get(o.Process, uid)

    if process is None:
        print(f"NOT FOUND: {label}")
        continue

    references = [
        ex for ex in (process.exchanges or [])
        if ex.is_quantitative_reference
        and not ex.is_input
    ]

    if len(references) != 1:
        print(f"CHECK REFERENCE: {label}")
        continue

    ref = references[0]

    row = {
        "label": label,
        "uuid": uid,
        "process_name": process.name,
        "location": getattr(process.location, "name", ""),
        "reference_product": getattr(ref.flow, "name", ""),
        "reference_unit": getattr(ref.unit, "name", ""),
        "reference_amount": ref.amount,
        "review_status": "Pending manual approval",
    }

    rows.append(row)
    print(
        f"{label}: {row['reference_product']} "
        f"({row['reference_unit']}) "
        f"[{row['location']}]"
    )

# Save the shortlist with review status; product matching does not prove suitability.
path = OUT / "background_mapping_review.csv"

with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "label", "uuid", "process_name", "location",
        "reference_product", "reference_unit",
        "reference_amount", "review_status"
    ])
    writer.writeheader()
    writer.writerows(rows)

# Search missing baking soda processes
terms = (
    "sodium bicarbonate",
    "sodium hydrogen carbonate",
    "sodium hydrogencarbonate",
    "baking soda",
)

matches = [
    p for p in client.get_descriptors(o.Process)
    if p.name and any(t in p.name.lower() for t in terms)
]

print("\nSODIUM BICARBONATE CANDIDATES:")
for p in matches:
    print(p.name, p.id)

print(f"\nSaved: {path}")
print(f"Sodium bicarbonate matches: {len(matches)}")
print("Database was not modified.")
