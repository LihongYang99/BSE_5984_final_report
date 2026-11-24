
from pathlib import Path
import csv

import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

# Per 1 kg nominal Feed C
TARGETS = {
    "steam": {
        "quantity": 0.320,
        "unit": "kg",
        "terms": ["steam"],
    },
    "electricity": {
        "quantity": 0.130,
        "unit": "kWh",
        "terms": [
            "market for electricity, low voltage",
            "market group for electricity, low voltage",
        ],
    },
    "freshwater": {
        "quantity": 0.0013333333,
        "unit": "m3",
        "terms": [
            "market for tap water",
            "market group for tap water",
            "tap water production",
        ],
    },
    "truck_transport": {
        "quantity": 1.006,
        "unit": "t*km",
        "terms": [
            "market for transport, freight, lorry",
            "market group for transport, freight, lorry",
        ],
    },
}

processes = client.get_descriptors(o.Process)
rows = []

for group, cfg in TARGETS.items():
    matches = [
        p for p in processes
        if p.name and any(
            term in p.name.lower()
            for term in cfg["terms"]
        )
    ]

    print(f"\n=== {group.upper()} ===")
    print(f"Name matches: {len(matches)}")

    candidates = []

    for desc in matches:
        # Read detailed process and reference output
        process = client.get(o.Process, desc.id)
        if process is None:
            continue

        refs = [
            ex for ex in (process.exchanges or [])
            if ex.is_quantitative_reference
            and not ex.is_input
        ]

        for ref in refs:
            unit = getattr(ref.unit, "name", "")
            product = getattr(ref.flow, "name", "")

            # Prioritize correct reference units
            if unit.replace(" ", "") != cfg["unit"]:
                continue

            location = getattr(
                process.location, "name", ""
            )

            score = 0
            if "United States" in location:
                score += 5
            elif "North America" in location:
                score += 4
            elif location in ("Global", "Rest of World"):
                score += 2

            if "market" in (process.name or "").lower():
                score += 1

            candidates.append({
                "stage": group,
                "quantity_per_kg_feed": cfg["quantity"],
                "process_name": process.name,
                "reference_product": product,
                "location": location,
                "unit": unit,
                "uuid": process.id,
                "score": score,
                "status": "REVIEW_REQUIRED",
            })

    candidates.sort(
        key=lambda x: (-x["score"], x["process_name"])
    )

    for item in candidates[:20]:
        rows.append(item)
        print(
            f"{item['location']} | "
            f"{item['reference_product']} | "
            f"{item['process_name']}"
        )

path = OUT / "feed_processing_provider_candidates.csv"

fields = [
    "stage",
    "quantity_per_kg_feed",
    "process_name",
    "reference_product",
    "location",
    "unit",
    "uuid",
    "score",
    "status",
]

with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("\n=== COMPLETE ===")
print(f"Saved {len(rows)} candidates")
print(path)
print("No database changes.")
