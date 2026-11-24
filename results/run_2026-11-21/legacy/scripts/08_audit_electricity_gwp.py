
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = ROOT / "figures"

OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

client = ipc.Client(8080)

SYSTEM_ID = "931b7343-5d8e-4f14-ab2e-2fd147a3191d"
METHOD_ID = "9488e228-f9d7-4921-b616-0cad160d96f7"

# olca-schema 2.7: CalculationSetup has no calculation_type
setup = o.CalculationSetup(
    target=o.Ref(
        ref_type=o.RefType.ProductSystem,
        id=SYSTEM_ID
    ),
    impact_method=o.Ref(
        ref_type=o.RefType.ImpactMethod,
        id=METHOD_ID
    ),
    amount=1.0
)

print("Running openLCA calculation...")

result = client.calculate(setup)

if result is None:
    raise RuntimeError("openLCA calculation failed")

try:
    result.wait_until_ready()

    impacts = result.get_total_impacts()

    target_name = (
        "Climate change: total (excl. biogenic CO2) "
        "- Global warming potential (GWP100)"
    )

    target = next(
        (
            x for x in impacts
            if x.impact_category
            and x.impact_category.name == target_name
        ),
        None
    )

    if target is None:
        print("Available impact categories:")
        for impact in impacts:
            print(" -", impact.impact_category.name)
        raise RuntimeError("Target GWP100 category not found")

    total_gwp = float(target.amount)

    print(f"\nTotal GWP100: {total_gwp:.6f} kg CO2-eq/kWh")

    # Official olca-ipc 2.7 method
    contributions = result.get_impact_contributions_of(
        target.impact_category
    )

    rows = []

    for item in contributions:
        tech = item.tech_flow
        provider = getattr(tech, "provider", None)

        rows.append({
            "process": getattr(provider, "name", "Unknown"),
            "provider_id": getattr(provider, "id", ""),
            "gwp_kg_co2eq": float(item.amount or 0)
        })

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError(
            "No contributions returned by openLCA"
        )

    output_path = OUT / "electricity_gwp_contributions.csv"
    df.to_csv(output_path, index=False)

    sum_contributions = df["gwp_kg_co2eq"].sum()
    difference = sum_contributions - total_gwp

    print(f"Number of contributions: {len(df)}")
    print(f"Sum of contributions: {sum_contributions:.6f}")
    print(f"Difference: {difference:.6e}")

    # Plot largest absolute direct contributions
    top = (
        df.assign(abs_gwp=df["gwp_kg_co2eq"].abs())
        .sort_values("abs_gwp", ascending=False)
        .head(12)
        .sort_values("gwp_kg_co2eq")
    )

    print("\nTop 12 absolute contributors:")
    print(
        top[["process", "gwp_kg_co2eq"]]
        .to_string(index=False)
    )

    fig, ax = plt.subplots(figsize=(10, 7))

    labels = [
        str(name)[:65]
        for name in top["process"]
    ]

    ax.barh(labels, top["gwp_kg_co2eq"])
    ax.axvline(0, color="gray", linewidth=0.8)

    ax.set_xlabel(
        "Direct GWP contribution (kg CO2-eq/kWh)"
    )
    ax.set_title(
        "US Electricity: Largest GWP Contributors"
    )

    fig.tight_layout()

    fig_path = FIG / "fig03_electricity_gwp_audit.png"
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"\nSaved CSV: {output_path}")
    print(f"Saved figure: {fig_path}")

finally:
    result.dispose()
