
from pathlib import Path
import csv
import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

client = ipc.Client(8080)

PROVIDER_ID = "36b2c661-ad03-3c43-b53f-9c5980d44d34"
METHOD_ID = "9488e228-f9d7-4921-b616-0cad160d96f7"

# Published Feed C formulation
PROXY_KG_PER_KG_FEED = 0.05
FCR = 1.5

TARGET = (
    "Climate change: total (excl. biogenic CO2) "
    "- Global warming potential (GWP100)"
)

provider = client.get(o.Process, PROVIDER_ID)
if provider is None:
    raise RuntimeError("Meat and bone meal provider not found")

print("Provider:", provider.name)
print("Location:", getattr(provider.location, "name", "Unknown"))

# Reuse an existing product system if available
system_ref = None

for desc in client.get_descriptors(o.ProductSystem):
    ps = client.get(o.ProductSystem, desc.id)
    if ps and ps.ref_process and ps.ref_process.id == PROVIDER_ID:
        system_ref = o.Ref(
            ref_type=o.RefType.ProductSystem,
            id=ps.id
        )
        break

if system_ref is None:
    print("Creating proxy product system in database copy...")

    config = o.LinkingConfig(
        prefer_unit_processes=True,
        provider_linking=o.ProviderLinking.PREFER_DEFAULTS,
    )

    system_ref = client.create_product_system(
        o.Ref(ref_type=o.RefType.Process, id=PROVIDER_ID),
        config
    )

if system_ref is None:
    raise RuntimeError("Product system unavailable")

reference = next(e for e in provider.exchanges if e.is_quantitative_reference and not e.is_input)
setup = o.CalculationSetup(
    target=system_ref,
    impact_method=o.Ref(
        ref_type=o.RefType.ImpactMethod,
        id=METHOD_ID
    ),
    amount=1.0,
    unit=reference.unit,
    flow_property=reference.flow_property,
)

result = client.calculate(setup)

try:
    result.wait_until_ready()
    impacts = result.get_total_impacts()

    match = next(
        (
            x for x in impacts
            if x.impact_category
            and x.impact_category.name == TARGET
        ),
        None
    )

    if match is None:
        raise RuntimeError("GWP100 category not found")

    ef = float(match.amount)

finally:
    result.dispose()

contribution_feed = ef * PROXY_KG_PER_KG_FEED
contribution_shrimp = contribution_feed * FCR

print("\n=== PROXY SCENARIO ===")
print(f"Meat and bone meal EF: {ef:.6f} kg CO2-eq/kg")
print(f"Contribution per kg feed: {contribution_feed:.6f}")
print(f"Contribution per kg shrimp: {contribution_shrimp:.6f}")

print("\nThis is a proxy, not verified poultry by-product meal.")

path = OUT / "poultry_proxy_scenario.csv"

with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "proxy", "ef_kg_co2eq_per_kg",
            "contribution_per_kg_feed",
            "contribution_per_kg_shrimp"
        ]
    )
    writer.writeheader()
    writer.writerow({
        "proxy": "RoW meat and bone meal",
        "ef_kg_co2eq_per_kg": ef,
        "contribution_per_kg_feed": contribution_feed,
        "contribution_per_kg_shrimp": contribution_shrimp,
    })

print(f"\nSaved: {path}")
