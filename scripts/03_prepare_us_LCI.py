# Step 03: Prepare the literature-based US inventory per kg of live shrimp.

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Published foreground inventory, per kg live shrimp.
# Source: Al Eissa et al. (2022), Table 2.
# Indiana was primary data in the source paper; both cases are secondary data here.
records = [
    {
        "system": "Indiana Biofloc",
        "country": "USA",
        "state": "Indiana",
        "data_type": "Primary farm data",
        "electricity_kwh_per_kg": 0.921,
        "feed_kg_per_kg": 1.500,
        "source": "Al Eissa et al. (2022), Table 2"
    },
    {
        "system": "Alabama Pond",
        "country": "USA",
        "state": "Alabama",
        "data_type": "Literature-derived",
        "electricity_kwh_per_kg": 8.799,
        "feed_kg_per_kg": 1.020,
        "source": "Al Eissa et al. (2022), Table 2"
    }
]

# Collect the already-normalized quantities in a common inventory table.
df = pd.DataFrame(records)

# Save the foreground inventory for later calculations and plots.
output = DATA_DIR / "us_lci_baseline.csv"
df.to_csv(output, index=False)

print("\nUS Shrimp LCI")
print(df.to_string(index=False))
print(f"\nSaved to: {output}")
