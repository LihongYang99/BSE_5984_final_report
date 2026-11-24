
from pathlib import Path
import csv
import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

# Search generic truck transport instead of one EURO class
terms = [
    "lorry, diesel, unspecified",
    "lorry, unspecified",
    "lorry, fleet average",
]

descriptors = client.get_descriptors(o.Process)
rows = []

for descriptor in descriptors:
    name = (descriptor.name or "").lower()

    if not any(term in name for term in terms):
        continue

    if any(term in name for term in [
        "refrigeration", "cooling", "freezing"
    ]):
        continue

    process = client.get(o.Process, descriptor.id)

    if process is None:
        continue

    for ex in process.exchanges or []:
        if ex.is_input or not ex.is_quantitative_reference:
            continue

        product = getattr(ex.flow, "name", "")
        unit = getattr(ex.unit, "name", "")
        location = getattr(process.location, "name", "")

        if "transport, freight, lorry" not in product.lower():
            continue

        if unit not in ("t*km", "tkm", "metric ton*km"):
            continue

        rows.append({
            "process_name": process.name,
            "reference_product": product,
            "location": location,
            "unit": unit,
            "uuid": process.id,
            "status": "REVIEW_REQUIRED",
        })

print("\n=== GENERIC TRUCK CANDIDATES ===")

for row in rows:
    print(
        row["location"],
        "|",
        row["reference_product"],
        "|",
        row["unit"],
        "|",
        row["uuid"]
    )

output = OUT / "generic_truck_candidates.csv"

with output.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "process_name",
        "reference_product",
        "location",
        "unit",
        "uuid",
        "status",
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"\nFound {len(rows)} candidates.")
print(f"Saved: {output}")
print("READ ONLY - no database changes.")
