
from pathlib import Path
import csv

import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

# Indiana Biofloc - per 1 kg live shrimp
# Al Eissa et al. (2022), Table 2

PROVIDERS = {
    "electricity_US": {
        "uuid": "483cde5f-7ae5-379e-ae10-54bb8fbbe6a2",
        "expected_product": "electricity, low voltage",
        "unit": "kWh",
        "quantity": 0.921,
    },
    "sodium_bicarbonate_RoW": {
        "uuid": "e93a63af-e80f-31c8-b9e9-c49d2a3c5e5d",
        "expected_product": "sodium bicarbonate",
        "unit": "kg",
        "quantity": 0.110,
    },
    "tap_water_RoW_proxy": {
        "uuid": "6354808d-1c16-3d24-a016-9da90503bf67",
        "expected_product": "tap water",
        "unit": "kg",
        # 0.075 m3 * 1000 kg/m3
        "quantity": 75.0,
    },
    "tap_water_Global_proxy": {
        "uuid": "0b1b340c-ca7d-3c98-912f-ef873f3f8e7c",
        "expected_product": "tap water",
        "unit": "kg",
        "quantity": 75.0,
    },
}

rows = []

print("=== STEP 30: FARMING PROVIDER VALIDATION ===")

for label, cfg in PROVIDERS.items():
    process = client.get(o.Process, cfg["uuid"])

    if process is None:
        print(f"NOT FOUND: {label}")
        continue

    refs = [
        ex for ex in (process.exchanges or [])
        if ex.is_quantitative_reference and not ex.is_input
    ]

    if len(refs) != 1:
        print(f"CHECK REFERENCE: {label}")
        continue

    ref = refs[0]

    product = getattr(ref.flow, "name", "")
    unit = getattr(ref.unit, "name", "")
    location = getattr(process.location, "name", "")

    valid = (
        product.lower() == cfg["expected_product"]
        and unit == cfg["unit"]
    )

    status = "PASS" if valid else "CHECK"

    print(f"\n{status}: {label}")
    print("Process:", process.name)
    print("Location:", location)
    print("Reference product:", product)
    print("Unit:", unit)
    print("Quantity per kg shrimp:", cfg["quantity"])

    rows.append({
        "label": label,
        "process_uuid": process.id,
        "process_name": process.name,
        "location": location,
        "reference_product": product,
        "unit": unit,
        "quantity_per_kg_shrimp": cfg["quantity"],
        "validation": status,
        "assumption": (
            "Treated tap-water proxy; source unverified"
            if "water" in label
            else "Background geography requires review"
        ),
    })

path = OUT / "farming_provider_mapping.csv"

with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "label",
            "process_uuid",
            "process_name",
            "location",
            "reference_product",
            "unit",
            "quantity_per_kg_shrimp",
            "validation",
            "assumption",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

print("\nSaved:", path)
print("No database changes made.")
