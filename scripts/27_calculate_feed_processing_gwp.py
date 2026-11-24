# Step 27: Calculate the processing and delivery contributions per kg of Feed C.

from pathlib import Path
import sys
import csv

import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

METHOD_ID = "9488e228-f9d7-4921-b616-0cad160d96f7"

TARGET = (
    "Climate change: total (excl. biogenic CO2) "
    "- Global warming potential (GWP100)"
)

# Per 1 kg Feed C: Al Eissa et al. (2022)
INPUTS = {
    "steam": {
        "uuid": "4998756e-9c04-34fd-ba5a-1f93ad0410f3",
        "amount": 0.320,
        "unit": "kg",
        "product": "steam, in chemical industry",
    },
    "electricity": {
        "uuid": "483cde5f-7ae5-379e-ae10-54bb8fbbe6a2",
        "amount": 0.130,
        "unit": "kWh",
        "product": "electricity, low voltage",
    },
    "tap_water": {
        "uuid": "6354808d-1c16-3d24-a016-9da90503bf67",
        "amount": 1.333333,
        "unit": "kg",
        "product": "tap water",
    },
    "truck_transport": {
        "uuid": "10b1f069-3aa0-3e7a-84d2-9c9954215aae",
        "amount": 1.006,
        "unit": "t*km",
        "product": "transport, freight, lorry, diesel, unspecified",
    },
}

# Validate actual provider products and units first
print("=== PROVIDER VALIDATION ===")

validated = []

for label, cfg in INPUTS.items():
    process = client.get(o.Process, cfg["uuid"])

    if process is None:
        raise RuntimeError(f"Missing process: {label}")

    refs = [
        ex for ex in process.exchanges or []
        if ex.is_quantitative_reference and not ex.is_input
    ]

    if len(refs) != 1:
        raise RuntimeError(f"Invalid reference: {label}")

    ref = refs[0]
    unit = ref.unit.name if ref.unit else ""
    product = ref.flow.name if ref.flow else ""

    if unit != cfg["unit"] or product != cfg["product"]:
        raise RuntimeError(
            f"Mismatch for {label}: {product}, {unit}"
        )

    print(f"{label}: PASS | {process.name} | {unit}")
    validated.append((label, cfg, process))

# Stop after provider validation unless LCIA was requested.
if "--calculate" not in sys.argv:
    print("\nDRY RUN PASSED. No database changes.")
    print("Use --calculate to run the LCIA.")
    sys.exit(0)

# Reuse Product Systems where possible
existing_systems = {}

for desc in client.get_descriptors(o.ProductSystem):
    ps = client.get(o.ProductSystem, desc.id)
    if ps and ps.ref_process:
        existing_systems[ps.ref_process.id] = ps.id

rows = []

# For each input, reuse or create a system and calculate a factor in its stated unit.
for label, cfg, process in validated:
    print(f"\nCalculating: {label}")

    system_id = existing_systems.get(process.id)

    if system_id is None:
        config = o.LinkingConfig(
            prefer_unit_processes=True,
            provider_linking=o.ProviderLinking.PREFER_DEFAULTS,
        )

        system_ref = client.create_product_system(
            o.Ref(
                ref_type=o.RefType.Process,
                id=process.id,
            ),
            config,
        )

        if system_ref is None:
            raise RuntimeError(f"Cannot build system: {label}")

        system_id = system_ref.id

    reference = next(e for e in process.exchanges if e.is_quantitative_reference and not e.is_input)
    setup = o.CalculationSetup(
        target=o.Ref(
            ref_type=o.RefType.ProductSystem,
            id=system_id,
        ),
        impact_method=o.Ref(
            ref_type=o.RefType.ImpactMethod,
            id=METHOD_ID,
        ),
        amount=1.0,
        unit=reference.unit,
        flow_property=reference.flow_property,
    )

    result = client.calculate(setup)

    if result is None:
        raise RuntimeError(f"Calculation failed: {label}")

    try:
        result.wait_until_ready()
        impacts = result.get_total_impacts()

        match = next(
            (
                x for x in impacts
                if x.impact_category
                and x.impact_category.name == TARGET
            ),
            None,
        )

        if match is None:
            raise RuntimeError(f"GWP100 not found: {label}")

        ef = float(match.amount)

    finally:
        result.dispose()

    # Multiply the factor by the physical quantity per kg feed.
    contribution = ef * cfg["amount"]

    rows.append({
        "stage": label,
        "amount_per_kg_feed": cfg["amount"],
        "unit": cfg["unit"],
        "ef_per_unit": ef,
        "gwp_per_kg_feed": contribution,
        "provider_uuid": process.id,
    })

    print(f"EF = {ef:.6f} kg CO2-eq/{cfg['unit']}")
    print(f"Contribution = {contribution:.6f}")

# Sum processing and delivery only; ingredient supply is added separately.
total = sum(row["gwp_per_kg_feed"] for row in rows)

path = OUT / "feed_processing_transport_gwp.csv"

with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=list(rows[0].keys()),
    )
    writer.writeheader()
    writer.writerows(rows)

print("\n=== RESULTS ===")
print(f"Processing + transport GWP: {total:.6f} kg CO2-eq/kg feed")

# Previous proxy-based ingredient scenario
# This legacy console comparison uses a rounded ingredient total; reviewed runs use saved precision.
V2_INGREDIENTS = 0.912134

print(
    "Exploratory combined screening GWP:",
    f"{V2_INGREDIENTS + total:.6f}",
    "kg CO2-eq/kg nominal feed"
)

print("\nSaved:", path)
print("CAUTION: hybrid proxies; not yet a complete harmonized LCA.")
