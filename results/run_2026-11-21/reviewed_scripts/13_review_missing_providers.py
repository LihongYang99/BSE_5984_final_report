
import olca_ipc as ipc
import olca_schema as o

client = ipc.Client(8080)

candidates = {
    "meat_bone_meal_market":
        "36b2c661-ad03-3c43-b53f-9c5980d44d34",

    "meat_bone_meal_rendering_1":
        "bd6c7154-3418-3df2-a24a-bf596fb6e58b",

    "meat_bone_meal_rendering_2":
        "7399b1cc-d129-3408-82cf-101f9b46d060",

    "sodium_bicarbonate_market_1":
        "e93a63af-e80f-31c8-b9e9-c49d2a3c5e5d",

    "sodium_bicarbonate_market_2":
        "af96af92-ca95-3aef-8bac-c01a1161a7d3",

    "sodium_bicarbonate_production_1":
        "512c2ce2-08bd-3f31-858f-18b0994f8a44",

    "sodium_bicarbonate_production_2":
        "c986bbb2-88fb-354e-ab6f-b40761ddd9bd",
}

print("=== BACKGROUND PROCESS REVIEW ===")

for label, uid in candidates.items():

    process = client.get(o.Process, uid)

    if process is None:
        print(f"\nNOT FOUND: {label}")
        continue

    print(f"\n--- {label} ---")
    print("Process:", process.name)
    print(
        "Location:",
        getattr(process.location, "name", "Unknown")
    )

    refs = [
        ex for ex in (process.exchanges or [])
        if ex.is_quantitative_reference
        and not ex.is_input
    ]

    for ex in refs:
        print("Reference product:", ex.flow.name)
        print("Unit:", ex.unit.name)
        print("Amount:", ex.amount)

print("\n=== SEARCH MISSING PRODUCT FLOWS ===")

flows = client.get_descriptors(o.Flow)

for keyword in ["rice bran", "lecithin", "rice milling"]:

    matches = [
        flow for flow in flows
        if flow.name
        and keyword in flow.name.lower()
    ]

    print(f"\n{keyword}: {len(matches)} flow matches")

    for flow in matches[:15]:
        print(" -", flow.name, "|", flow.id)

print("\nRead-only review completed.")
