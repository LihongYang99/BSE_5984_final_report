"""Read-only search in a running openLCA IPC server on port 8080.
Searches broader names/reference products for missing Feed C ingredients.
No database writes. Inspect all matches manually before approving a proxy.
"""
from pathlib import Path
import csv
import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path.cwd()
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
client = ipc.Client(8080)
processes = client.get_descriptors(o.Process)

keywords = {
    "poultry_byproduct_meal": ["poultry", "chicken meal", "animal meal", "rendering", "meat and bone meal", "feather meal"],
    "rice_bran": ["rice bran", "rice milling", "rice mill", "rice polishing", "rice husk"],
    "soybean_lecithin": ["lecithin", "degumming", "soybean oil refining", "soy oil refining", "soybean oil production"],
    "supplements": ["vitamin premix", "mineral premix", "feed supplement", "choline chloride", "ascorbic acid", "mineral feed"],
    "sodium_bicarbonate_for_farm": ["sodium bicarbonate", "sodium hydrogen carbonate", "baking soda"],
}

rows = []
for key, terms in keywords.items():
    matches = []
    for p in processes:
        name = (p.name or "").lower()
        if any(term in name for term in terms):
            matches.append(p)
    print(f"\n{key}: {len(matches)} process-name matches")
    for p in matches[:15]:
        print(' ',p.name, '|',p.id)
    for p in matches:
        rows.append({"ingredient":key,"process_name":p.name or "", "uuid":p.id,
                     "category":str(getattr(p,'category','') or ''),"status":"REVIEW_ONLY"})

output = OUT / "missing_feed_provider_candidates.csv"
with output.open('w',newline='',encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["ingredient","process_name","uuid","category","status"])
    writer.writeheader()
    writer.writerows(rows)
print(f"\nSaved {len(rows)} candidate rows to {output}")
print("No database changes made.")
