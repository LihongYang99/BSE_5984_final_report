
import sys
import olca_ipc as ipc
import olca_schema as o

# ==========================================
# STEP 14 - Feed C Screening LCA Model
# Source: Al Eissa et al. (2022), Table 1
# openLCA 2.x + olca-ipc 2.7
# ==========================================

client = ipc.Client(8080)

PROCESS_NAME = "Feed C ingredient supply - 83pct screening"
FLOW_NAME = "Feed C ingredient supply - partial inventory"

# Quantities per 1 kg nominal Feed C
# Candidate background providers from ecoinvent 3.11
INGREDIENTS = {
    "fish_meal": {
        "amount": 0.30,
        "uuid": "e65f571f-8fcc-3aff-8893-6433e9b2795a",
        "expected_product": "fishmeal",
    },
    "soybean_meal": {
        "amount": 0.20,
        "uuid": "355ad6bb-9864-3a8b-a369-39d41b991538",
        "expected_product": "soybean meal",
    },
    "wheat_flour": {
        "amount": 0.30,
        "uuid": "ff154541-8003-3e3c-b66b-1bc7e4a05fc3",
        "expected_product": "wheat flour",
    },
    "fish_oil": {
        "amount": 0.03,
        "uuid": "95d9cfd1-c860-3bb4-8100-b74b77ca78ae",
        "expected_product": "fish oil",
    },
}

# ==========================================
# 1. Validate background processes
# ==========================================

print("\n=== STEP 14: PROVIDER VALIDATION ===")

validated = []

for ingredient, info in INGREDIENTS.items():

    provider = client.get(o.Process, info["uuid"])

    if provider is None:
        raise RuntimeError(
            f"Provider not found: {ingredient}"
        )

    references = [
        ex for ex in (provider.exchanges or [])
        if ex.is_quantitative_reference
        and not ex.is_input
    ]

    if len(references) != 1:
        raise RuntimeError(
            f"Invalid reference output: {ingredient}"
        )

    ref = references[0]

    if ref.flow is None or ref.flow.id is None:
        raise RuntimeError(
            f"Missing reference flow: {ingredient}"
        )

    if ref.unit is None or ref.unit.name != "kg":
        raise RuntimeError(
            f"Unit mismatch: {ingredient}"
        )

    if info["expected_product"] not in ref.flow.name.lower():
        raise RuntimeError(
            f"Unexpected product for {ingredient}: "
            f"{ref.flow.name}"
        )

    product_flow = client.get(o.Flow, ref.flow.id)

    if product_flow is None:
        raise RuntimeError(
            f"Product flow not found: {ingredient}"
        )

    validated.append(
        (ingredient, info["amount"], provider, ref, product_flow)
    )

    print(f"\nIngredient: {ingredient}")
    print(f"Amount: {info['amount']} kg")
    print(f"Provider: {provider.name}")
    print(f"Reference product: {ref.flow.name}")
    print(f"Unit: {ref.unit.name}")
    print(
        "Location:",
        getattr(provider.location, "name", "Unknown")
    )

# ==========================================
# 2. Inventory coverage
# ==========================================

coverage = sum(item[1] for item in validated)
missing = 1.0 - coverage

print("\n=== INVENTORY COVERAGE ===")
print(f"Modeled mass fraction: {coverage:.0%}")
print(f"Unmodeled mass fraction: {missing:.0%}")

if abs(coverage - 0.83) > 1e-9:
    raise RuntimeError("Unexpected ingredient mass fraction")

# ==========================================
# 3. Dry run by default
# ==========================================

if "--write" not in sys.argv:
    print("\nVALIDATION ONLY")
    print("No database changes were made.")
    print(
        "Run with --write only after opening "
        "the Shrimp_LCA_US_2026 database copy."
    )
    sys.exit(0)

# ==========================================
# 4. Write to openLCA database copy
# ==========================================

print("\n=== DATABASE WRITE ===")
print("Make sure Shrimp_LCA_US_2026 is open!")

existing_process = client.get(
    o.Process, name=PROCESS_NAME
)

existing_flow = client.get(
    o.Flow, name=FLOW_NAME
)

if existing_process is not None or existing_flow is not None:
    raise RuntimeError(
        "Feed C screening model already exists. "
        "Database was not modified."
    )

mass = client.get(o.FlowProperty, name="Mass")

if mass is None:
    raise RuntimeError("Mass flow property not found")

# Create reference product flow
feed_flow = o.new_product(FLOW_NAME, mass)

feed_flow.description = (
    "Nominal 1 kg Feed C basis. "
    "Only 83% of ingredient mass is represented. "
    "The remaining 17%, feed processing, and "
    "transportation are excluded."
)

flow_result = client.put(feed_flow)

if flow_result is None:
    raise RuntimeError("Failed to create Feed C flow")

# Create custom production process
process = o.new_process(PROCESS_NAME)

process.description = (
    "Partial screening LCI based on Al Eissa "
    "et al. (2022), Table 1. "
    "Not a complete commercial feed LCA. "
    "Selected ecoinvent providers are provisional."
)

# Output: 1 kg nominal Feed C
output = o.new_output(process, feed_flow, 1.0)
output.is_quantitative_reference = True

# Add ingredient inputs
for ingredient, amount, provider, ref, product_flow in validated:

    exchange = o.new_input(
        process,
        product_flow,
        amount
    )

    exchange.unit = ref.unit
    exchange.flow_property = ref.flow_property

    exchange.default_provider = o.Ref(
        ref_type=o.RefType.Process,
        id=provider.id,
        name=provider.name
    )

    exchange.description = (
        f"Feed C ingredient: {ingredient}; "
        "provisional background provider"
    )

process_result = client.put(process)

if process_result is None:
    raise RuntimeError(
        "Failed to create process. "
        "The reference flow may already have been created."
    )

print("\n=== SUCCESS ===")
print("Created:", process.name)
print("Process UUID:", process_result.id)
print("Reference output: 1 kg nominal Feed C")
print("Ingredient mass coverage: 83%")
print("Remaining mass unmodeled: 17%")
print("Feed processing and transport excluded.")
