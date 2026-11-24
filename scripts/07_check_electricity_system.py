# Step 07: Inspect the structure and displayed target unit of electricity systems.

import olca_ipc as ipc
import olca_schema as o

client = ipc.Client(8080)

TARGET_PROCESS = "483cde5f-7ae5-379e-ae10-54bb8fbbe6a2"

systems = client.get_descriptors(o.ProductSystem)

print(f"Product systems in database: {len(systems)}")

matching = []

# Find systems whose reference process is the selected US electricity market.
for descriptor in systems:
    name = (descriptor.name or "").lower()

    if "electricity, low voltage" not in name:
        continue

    system = client.get(o.ProductSystem, descriptor.id)

    if system is None:
        continue

    ref = system.ref_process

    if ref is None or ref.id != TARGET_PROCESS:
        continue

    matching.append(system)

print(f"\nMatching US electricity systems: {len(matching)}")

# Display model size and links; the displayed unit alone does not validate demand.
for system in matching:
    processes = system.processes or []
    links = system.process_links or []

    print("\n--------------------------")
    print("System:", system.name)
    print("System UUID:", system.id)
    print("Target amount:", system.target_amount)
    print("Target unit:", getattr(system.target_unit, "name", None))
    print("Processes:", len(processes))
    print("Process links:", len(links))

    print("\nSample upstream processes:")
    for process in processes[:10]:
        print(" -", process.name)

print("\nCheck complete. No database writes.")
