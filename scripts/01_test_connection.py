# Step 01: Test the Python connection to the active openLCA database.
# Test Connection to openLCA IPC Server 

import olca_ipc as ipc
import olca_schema as o

# Connect to the openLCA IPC server
client = ipc.Client(8080)

# Read available processes from the active database
processes = client.get_descriptors(o.Process)

print(f"Connected! Found {len(processes)} processes.")

# Print a small sample to confirm that process names are readable.
for process in processes[:10]:
    print(process.name)
