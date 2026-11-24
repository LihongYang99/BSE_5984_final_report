# Step 25: Refine processing-provider candidates using product, unit, and transport checks.
"""Step 25: read-only review of feed processing background providers.

Run with openLCA's Standard IPC server (port 8080) and the project database open.
Writes only outputs/processing_provider_shortlist.csv, not openLCA objects.
"""
from pathlib import Path
import csv
import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)
descriptors = client.get_descriptors(o.Process)


# Classify candidate names while excluding unsuitable transport and water services.
def matching_stage(name: str):
    n = name.lower()
    # Ordinary feed delivery: no refrigerated or special-fuel truck services.
    if ("transport, freight, lorry" in n or "transport, freight, truck" in n):
        excluded = (
            "reefer", "refrigerat", "freezing", "cooling", "ref. machine",
            "fatty acid methyl ester", "hydrogen", "natural gas",
            "electric", "biodiesel", "liquefied", "compressed",
        )
        if not any(word in n for word in excluded):
            return "ordinary_truck"
    # Water delivered to a factory, not wastewater treatment.
    if ("tap water" in n or "potable water" in n or
            "drinking water" in n or "market for water" in n or
            "water supply" in n):
        if not any(word in n for word in ("wastewater", "irrigation", "bottled")):
            return "freshwater"
    # Market/production of steam as a reference product (not steam-reforming hydrogen).
    if "steam" in n and ("market for steam" in n or "steam production" in n):
        return "steam"
    # Process heat is only an alternative after enthalpy/temperature assumptions.
    if ("market for heat" in n or "heat production" in n or
            "market group for heat" in n):
        return "process_heat_alternative"
    return None


selected = []
for d in descriptors:
    if not d.name:
        continue
    group = matching_stage(d.name)
    if group:
        selected.append((group, d))

# Prefer markets and shorter descriptors before the IPC expansion.
selected.sort(key=lambda x: (
    x[0],
    0 if (x[1].name or "").lower().startswith("market") else 1,
    len(x[1].name or ""),
    x[1].name or "",
))

# Bound detailed IPC reads to keep the shortlist review manageable.
limit_per_stage = 90
counts = {}
rows = []
for stage, d in selected:
    if counts.get(stage, 0) >= limit_per_stage:
        continue
    counts[stage] = counts.get(stage, 0) + 1
    proc = client.get(o.Process, d.id)
    if proc is None:
        continue
    for ex in (proc.exchanges or []):
        if ex.is_input or not ex.is_quantitative_reference or not ex.flow:
            continue
        product = ex.flow.name or ""
        unit = ex.unit.name if ex.unit else ""
        product_lower = product.lower()
        # Strict reference product checks; process names alone are insufficient.
        appropriate = (
            (stage == "ordinary_truck" and unit in ("t*km", "tkm") and
             ("transport, freight, lorry" in product_lower or
              "transport, freight, truck" in product_lower)) or
            (stage == "freshwater" and unit in ("kg", "m3") and
             any(s in product_lower for s in ("tap water", "potable water", "drinking water"))) or
            (stage == "steam" and unit == "kg" and "steam" in product_lower) or
            (stage == "process_heat_alternative" and unit == "MJ" and
             "heat" in product_lower)
        )
        if not appropriate:
            continue
        loc = proc.location.name if proc.location else "Unknown"
        score = (10 if "United States" in loc else
                 7 if "North America" in loc else
                 4 if loc in ("Rest of World", "Global") else 0)
        pname = (proc.name or "").lower()
        if pname.startswith("market"):
            score += 2
        rows.append({
            "stage": stage, "process_name": proc.name,
            "reference_product": product, "location": loc,
            "unit": unit, "uuid": proc.id, "score": score,
            "review_status": "REVIEW_REQUIRED",
        })

# Sort eligible reference products and export them with review-required status.
rows.sort(key=lambda row: (row["stage"], -row["score"], row["process_name"]))
output = OUT / "processing_provider_shortlist.csv"
with output.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=[
        "stage", "process_name", "reference_product", "location",
        "unit", "uuid", "score", "review_status",
    ])
    writer.writeheader()
    writer.writerows(rows)

for stage in ("ordinary_truck", "freshwater", "steam", "process_heat_alternative"):
    subset = [r for r in rows if r["stage"] == stage]
    print(f"\n=== {stage}: {len(subset)} eligible candidates ===")
    for row in subset[:12]:
        print(f"{row['location']} | {row['reference_product']} [{row['unit']}] | {row['process_name']} | {row['uuid']}")
print(f"\nSaved: {output}")
print("READ-ONLY: no openLCA database changes.")
print("CAUTION: kg steam and MJ process heat are not interchangeable without assumptions.")
print("CAUTION: kg tap water and m3 tap water need explicit density conversion.")
