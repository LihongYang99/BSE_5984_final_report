
from pathlib import Path
import csv

import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

# Validated ecoinvent 3.11 US electricity process
electricity_id = "483cde5f-7ae5-379e-ae10-54bb8fbbe6a2"

# IPCC 2021 impact assessment method
method_id = "9488e228-f9d7-4921-b616-0cad160d96f7"

process_ref = o.Ref(
    ref_type=o.RefType.Process,
    id=electricity_id
)

method_ref = o.Ref(
    ref_type=o.RefType.ImpactMethod,
    id=method_id
)

print("Creating electricity product system...")

config = o.LinkingConfig(
    prefer_unit_processes=True,
    provider_linking=o.ProviderLinking.PREFER_DEFAULTS,
)

system_ref = client.create_product_system(process_ref, config)

if system_ref is None:
    raise RuntimeError("Could not create product system")

print(f"Product system ID: {system_ref.id}")

# Explicit units are required: an omitted unit requests MJ, not kWh.
system = client.get(o.ProductSystem, system_ref.id)
# Calculate the impacts of 1 kWh electricity
setup = o.CalculationSetup(
    target=system_ref,
    impact_method=method_ref,
    amount=1.0,
    unit=system.target_unit,
    flow_property=system.target_flow_property,
)

print("Running LCIA calculation...")

result = client.calculate(setup)

try:
    result.wait_until_ready()
    impacts = result.get_total_impacts()

    if not impacts:
        raise RuntimeError("No LCIA results returned")

    rows = []

    for impact in impacts:
        category = impact.impact_category

        row = {
            "impact_category": category.name,
            "amount": impact.amount,
            "unit": category.ref_unit,
        }

        rows.append(row)

        print(
            f"{row['impact_category']}: "
            f"{row['amount']:.6f} {row['unit']}"
        )

    output_file = OUTPUT / "electricity_gwp_us.csv"

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=[
                "impact_category", "amount", "unit"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved: {output_file}")

finally:
    result.dispose()
