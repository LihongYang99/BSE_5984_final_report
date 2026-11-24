
from pathlib import Path
import csv

import olca_ipc as ipc
import olca_schema as o

# =====================================
# STEP 17 - Feed C Partial GWP
# openLCA 2.7 / olca-ipc 2.7
# ecoinvent 3.11 Cut-off
# =====================================

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

SYSTEM_ID = "ae397b2d-ec58-4433-af49-3bdc3d3fe9c0"
PROCESS_ID = "149c1818-9c69-40d8-a34b-4659f7cbb276"
METHOD_ID = "9488e228-f9d7-4921-b616-0cad160d96f7"

TARGET_CATEGORY = (
    "Climate change: total (excl. biogenic CO2) "
    "- Global warming potential (GWP100)"
)

# =====================================
# 1. Check product system
# =====================================

system = client.get(o.ProductSystem, SYSTEM_ID)

if system is None:
    raise RuntimeError("Feed C Product System not found")

if not system.ref_process or system.ref_process.id != PROCESS_ID:
    raise RuntimeError("Incorrect reference process")

print("=== FEED C PRODUCT SYSTEM ===")
print("Name:", system.name)
print("Processes:", len(system.processes or []))
print("Links:", len(system.process_links or []))
print("Target amount:", system.target_amount)

# =====================================
# 2. Calculate LCIA
# =====================================

setup = o.CalculationSetup(
    target=o.Ref(
        ref_type=o.RefType.ProductSystem,
        id=SYSTEM_ID,
    ),
    impact_method=o.Ref(
        ref_type=o.RefType.ImpactMethod,
        id=METHOD_ID,
    ),
    amount=1.0,
    unit=system.target_unit,
    flow_property=system.target_flow_property,
)

print("\nCalculating IPCC 2021 impacts...")

result = client.calculate(setup)

if result is None:
    raise RuntimeError("Calculation could not be started")

try:
    result.wait_until_ready()

    impacts = result.get_total_impacts()

    if not impacts:
        raise RuntimeError("No LCIA results returned")

    rows = []

    for impact in impacts:
        category = impact.impact_category

        rows.append({
            "impact_category": category.name,
            "amount": float(impact.amount),
            "unit": category.ref_unit,
        })

    # Save all IPCC 2021 impact categories
    full_path = OUT / "feed_c_partial_ipcc2021.csv"

    with full_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["impact_category", "amount", "unit"]
        )
        writer.writeheader()
        writer.writerows(rows)

    # =====================================
    # 3. Select GWP100
    # =====================================

    matches = [
        row for row in rows
        if row["impact_category"] == TARGET_CATEGORY
    ]

    if len(matches) != 1:
        print("\nAvailable impact categories:")
        for row in rows:
            print(" -", row["impact_category"])
        raise RuntimeError("GWP100 category not uniquely found")

    gwp = matches[0]["amount"]

    # FCR = 1.5 kg nominal Feed C / kg live shrimp
    fcr = 1.5
    shrimp_feed_gwp = gwp * fcr

    print("\n=== RESULTS ===")
    print(
        f"Partial ingredient GWP per kg nominal Feed C: "
        f"{gwp:.6f} kg CO2-eq"
    )
    print(
        f"Partial feed-related GWP per kg live shrimp: "
        f"{shrimp_feed_gwp:.6f} kg CO2-eq"
    )

    print("\nLimitations:")
    print("- 17% of feed ingredients are missing")
    print("- Feed processing is excluded")
    print("- Feed transportation is excluded")
    print("- Several background processes are proxies")

    summary_path = OUT / "feed_c_partial_gwp_summary.csv"

    summary = [
        {
            "indicator": "Partial GWP per kg nominal Feed C",
            "amount": gwp,
            "unit": "kg CO2-eq/kg nominal feed",
        },
        {
            "indicator": "Partial feed GWP per kg live shrimp",
            "amount": shrimp_feed_gwp,
            "unit": "kg CO2-eq/kg live shrimp",
        },
    ]

    with summary_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["indicator", "amount", "unit"]
        )
        writer.writeheader()
        writer.writerows(summary)

    print("\nSaved:")
    print(full_path)
    print(summary_path)

finally:
    result.dispose()
