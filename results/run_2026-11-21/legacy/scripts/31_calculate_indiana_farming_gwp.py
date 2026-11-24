
from pathlib import Path
import sys

import pandas as pd
import olca_ipc as ipc
import olca_schema as o

# ============================================
# STEP 31 - Indiana Biofloc Screening GWP
# Al Eissa et al. (2022), Table 2
# Functional unit: 1 kg live shrimp
# ============================================

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

METHOD_ID = "9488e228-f9d7-4921-b616-0cad160d96f7"

GWP_CATEGORY = (
    "Climate change: total (excl. biogenic CO2) "
    "- Global warming potential (GWP100)"
)

# Inputs per kg live shrimp
PROVIDERS = {
    "farming_electricity": {
        "uuid": "483cde5f-7ae5-379e-ae10-54bb8fbbe6a2",
        "amount": 0.921,
        "unit": "kWh",
        "product": "electricity, low voltage",
    },
    "sodium_bicarbonate": {
        "uuid": "e93a63af-e80f-31c8-b9e9-c49d2a3c5e5d",
        "amount": 0.110,
        "unit": "kg",
        "product": "sodium bicarbonate",
    },
    "tap_water_proxy": {
        "uuid": "6354808d-1c16-3d24-a016-9da90503bf67",
        "amount": 75.0,
        "unit": "kg",
        "product": "tap water",
    },
}

print("=== STEP 31: PROVIDER VALIDATION ===")

validated = {}

for label, cfg in PROVIDERS.items():
    process = client.get(o.Process, cfg["uuid"])

    if process is None:
        raise RuntimeError(f"Process not found: {label}")

    refs = [
        ex for ex in (process.exchanges or [])
        if ex.is_quantitative_reference and not ex.is_input
    ]

    if len(refs) != 1:
        raise RuntimeError(f"Invalid reference: {label}")

    ref = refs[0]
    product = ref.flow.name if ref.flow else ""
    unit = ref.unit.name if ref.unit else ""

    if product != cfg["product"] or unit != cfg["unit"]:
        raise RuntimeError(
            f"Mismatch: {label} | {product} | {unit}"
        )

    validated[label] = process

    print(
        f"PASS: {label} | "
        f"{cfg['amount']} {unit} | "
        f"{getattr(process.location, 'name', '')}"
    )

if "--calculate" not in sys.argv:
    print("\nDRY RUN PASSED")
    print("No database changes made.")
    print("Use --calculate to run LCIA.")
    sys.exit(0)

# ============================================
# Reuse or create background Product Systems
# ============================================

existing_systems = {}

for descriptor in client.get_descriptors(o.ProductSystem):
    system = client.get(o.ProductSystem, descriptor.id)

    if system and system.ref_process:
        existing_systems[system.ref_process.id] = system.id


def calculate_gwp(label, cfg, process):
    system_id = existing_systems.get(process.id)

    if system_id is None:
        print(f"Creating Product System: {label}")

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
            raise RuntimeError(
                f"Product System creation failed: {label}"
            )

        system_id = system_ref.id

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
                and x.impact_category.name == GWP_CATEGORY
            ),
            None
        )

        if match is None:
            raise RuntimeError(
                f"GWP100 category not found: {label}"
            )

        ef = float(match.amount)
    finally:
        result.dispose()

    contribution = ef * cfg["amount"]

    return {
        "stage": label,
        "amount": cfg["amount"],
        "unit": cfg["unit"],
        "ef": ef,
        "gwp_per_kg_shrimp": contribution,
        "provider_uuid": process.id,
    }


rows = []

print("\n=== FARMING INPUT CALCULATIONS ===")

for label, cfg in PROVIDERS.items():
    row = calculate_gwp(
        label, cfg, validated[label]
    )
    rows.append(row)

    print(
        f"{label}: EF = {row['ef']:.6f}, "
        f"GWP contribution = "
        f"{row['gwp_per_kg_shrimp']:.6f}"
    )

farm = pd.DataFrame(rows)

farm.to_csv(
    OUT / "indiana_farming_inputs_gwp.csv",
    index=False,
)

# ============================================
# Read previously calculated Feed C results
# ============================================

v2 = pd.read_csv(
    OUT / "feed_c_v2_proxy_summary.csv"
)

matches = v2.loc[
    v2["scenario"] == "V2 100%-mass proxy hybrid",
    "gwp_per_kg_nominal_feed",
]

if len(matches) != 1:
    raise RuntimeError("Cannot locate Feed C V2")

ingredients_gwp = float(matches.iloc[0])

processing = pd.read_csv(
    OUT / "feed_processing_transport_gwp.csv"
)

processing_gwp = float(
    processing["gwp_per_kg_feed"].sum()
)

feed_gwp = ingredients_gwp + processing_gwp

FCR = 1.5
feed_contribution = feed_gwp * FCR

contrib = farm.set_index(
    "stage"
)["gwp_per_kg_shrimp"]

electricity = float(contrib["farming_electricity"])
bicarbonate = float(contrib["sodium_bicarbonate"])
water = float(contrib["tap_water_proxy"])

# No treated-water assumption in main scenario
without_water = (
    feed_contribution + electricity + bicarbonate
)

# Optional water-treatment proxy
with_water = without_water + water

scenarios = pd.DataFrame([
    {
        "scenario": "Without treated-water proxy",
        "gwp_per_kg_shrimp": without_water,
        "water_assumption": "Water supply treatment excluded",
    },
    {
        "scenario": "With RoW tap-water proxy",
        "gwp_per_kg_shrimp": with_water,
        "water_assumption": "75 kg treated tap water assumed",
    },
])

scenarios.to_csv(
    OUT / "indiana_screening_gwp_scenarios.csv",
    index=False,
)

print("\n=== INDIANA BIOFLOC RESULTS ===")
print(f"Feed C GWP/kg feed: {feed_gwp:.6f}")
print(f"Feed contribution/kg shrimp: {feed_contribution:.6f}")
print(f"Farming electricity: {electricity:.6f}")
print(f"Sodium bicarbonate: {bicarbonate:.6f}")
print(f"Tap-water proxy: {water:.6f}")

print("\n=== SCREENING SCENARIOS ===")
print(scenarios.to_string(index=False))

print("\nSaved CSV files in outputs/")
print("WARNING: Hybrid screening estimate, not full LCA.")
print("Water source, electricity EF and proxies need review.")
