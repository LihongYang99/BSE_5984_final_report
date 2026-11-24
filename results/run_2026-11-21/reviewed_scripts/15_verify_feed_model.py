
import olca_ipc as ipc
import olca_schema as o

client = ipc.Client(8080)

PROCESS_ID = "149c1818-9c69-40d8-a34b-4659f7cbb276"

process = client.get(o.Process, PROCESS_ID)

if process is None:
    raise RuntimeError("Feed C process not found")

print("Process:", process.name)
print("UUID:", process.id)

inputs = []
outputs = []

for ex in process.exchanges or []:
    flow_name = ex.flow.name if ex.flow else "UNKNOWN"
    unit_name = ex.unit.name if ex.unit else "UNKNOWN"

    if ex.is_input:
        inputs.append(ex)
        provider = (
            ex.default_provider.name
            if ex.default_provider else "NOT LINKED"
        )
        print(
            f"INPUT: {flow_name} | "
            f"{ex.amount} {unit_name} | "
            f"Provider: {provider}"
        )
    else:
        outputs.append(ex)
        print(
            f"OUTPUT: {flow_name} | "
            f"{ex.amount} {unit_name} | "
            f"Reference: {ex.is_quantitative_reference}"
        )

assert len(inputs) == 4, "Expected 4 inputs"
assert len(outputs) == 1, "Expected 1 output"
assert outputs[0].is_quantitative_reference
assert abs(outputs[0].amount - 1.0) < 1e-9
assert all(ex.default_provider is not None for ex in inputs)

print("\nPASS: Feed C process structure verified.")
print("Note: Product System linking is not yet verified.")
