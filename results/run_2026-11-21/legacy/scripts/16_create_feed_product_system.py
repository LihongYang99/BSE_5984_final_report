
import sys
import olca_ipc as ipc
import olca_schema as o

client = ipc.Client(8080)

PROCESS_ID = "149c1818-9c69-40d8-a34b-4659f7cbb276"

# Get custom Feed C process
process = client.get(o.Process, PROCESS_ID)

if process is None:
    raise RuntimeError("Feed C Process not found")

inputs = [
    ex for ex in process.exchanges or []
    if ex.is_input
]

if len(inputs) != 4:
    raise RuntimeError("Expected exactly 4 ingredient inputs")

expected = {}

for ex in inputs:
    if not ex.flow or not ex.default_provider:
        raise RuntimeError("Missing input flow or provider")

    expected[ex.flow.id] = ex.default_provider.id

print("Process:", process.name)
print("Inputs verified:", len(inputs))

# Avoid creating duplicate Product Systems
existing = None

for desc in client.get_descriptors(o.ProductSystem):
    system = client.get(o.ProductSystem, desc.id)

    if (
        system
        and system.ref_process
        and system.ref_process.id == PROCESS_ID
    ):
        existing = system
        break

if existing:
    system_ref = o.Ref(
        ref_type=o.RefType.ProductSystem,
        id=existing.id,
        name=existing.name
    )
    print("Existing Product System found.")
else:
    if "--write" not in sys.argv:
        print("\nDRY RUN PASSED")
        print("No database changes made.")
        print("Run with --write to create Product System.")
        sys.exit(0)

    print("\nCreating Product System...")

    config = o.LinkingConfig(
        prefer_unit_processes=True,
        provider_linking=o.ProviderLinking.PREFER_DEFAULTS,
    )

    process_ref = o.Ref(
        ref_type=o.RefType.Process,
        id=process.id,
        name=process.name
    )

    system_ref = client.create_product_system(
        process_ref, config
    )

    if system_ref is None:
        raise RuntimeError("Product System creation failed")

# Verify actual links in the Product System
system = client.get(o.ProductSystem, system_ref.id)

if system is None:
    raise RuntimeError("Cannot read Product System")

links = [
    link for link in (system.process_links or [])
    if link.process and link.process.id == PROCESS_ID
]

linked = {
    link.flow.id: link.provider.id
    for link in links
    if link.flow and link.provider
}

print("\n=== PRODUCT SYSTEM ===")
print("Name:", system.name)
print("UUID:", system.id)
print("Processes:", len(system.processes or []))
print("Total links:", len(system.process_links or []))
print("Direct Feed C links:", len(links))

for ex in inputs:
    actual = linked.get(ex.flow.id)
    required = ex.default_provider.id

    status = "PASS" if actual == required else "CHECK"

    print(
        f"{status}: {ex.flow.name} "
        f"-> {ex.default_provider.name}"
    )

if any(
    linked.get(flow_id) != provider_id
    for flow_id, provider_id in expected.items()
):
    raise RuntimeError(
        "Some Feed C ingredient providers are not linked "
        "correctly. Do not calculate GWP yet."
    )

print("\nPASS: All 4 ingredient links verified.")
