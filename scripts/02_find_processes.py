# Step 02: Export background-process candidates and available impact methods.
"""Read-only candidate search. No providers are selected or database objects changed."""

import argparse
import csv
from pathlib import Path

import olca_ipc as ipc
import olca_schema as o


# Use broad keywords for discovery; matches are not approved providers.
SEARCH_TERMS = {
    "electricity": ("market for electricity, low voltage", "market group for electricity, low voltage"),
    "pellet_feed": ("shrimp feed", "fish feed", "aquafeed", "feed pellet"),
    "fishmeal": ("fish meal", "fishmeal"),
    "soybean_meal": ("soybean meal", "soybean, meal", "soybean oilcake", "soybean oil cake"),
    "wheat_flour": ("wheat flour", "wheat milling"),
    "rapeseed_meal": ("rapeseed meal", "rape meal", "rape seed meal", "rape oilcake", "rapeseed oilcake"),
    "fish_oil": ("fish oil",),
    "sugar": ("sugar",),
    "quicklime": ("quicklime", "quick lime", "lime production", "market for lime"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--limit", type=int, default=12,
                        help="Maximum candidates displayed per group (default: 12); all matches are exported.")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be at least 1")

    # Read descriptors through JSON-RPC without modifying the database.
    client = ipc.Client(args.port)
    processes = client.get_descriptors(o.Process)
    if not processes:
        raise SystemExit("No processes returned. Check the active database and JSON-RPC IPC server.")
    output = Path(__file__).resolve().parents[1] / "outputs"
    output.mkdir(exist_ok=True)
    all_rows = []
    print(f"Read {len(processes)} process descriptors. No database writes will be made.")
    for group, terms in SEARCH_TERMS.items():
        matches = [p for p in processes if any(t in (p.name or "").lower() for t in terms)]
        # Display Chinese locations first, without selecting them as providers.
        matches.sort(key=lambda p: (not (p.location or "").upper().startswith("CN"),
                                   p.name or "", p.location or "", p.id or ""))
        print(f"\n{group}: {len(matches)} name matches; displaying up to {args.limit}")
        for ref in matches:
            all_rows.append({"group": group, "name": ref.name, "location": ref.location,
                             "unit": ref.ref_unit, "uuid": ref.id, "category": ref.category})
        for ref in matches[:args.limit]:
            print(f"  {ref.name}\n    Location: {ref.location or 'not reported'}; "
                  f"unit: {ref.ref_unit or 'not reported'}; UUID: {ref.id}")
    # List impact methods separately from the background-process candidates.
    methods = client.get_descriptors(o.ImpactMethod)
    method_rows = [{"name": m.name, "uuid": m.id, "category": m.category}
                   for m in sorted(methods, key=lambda m: m.name or "")]
    print(f"\nLCIA methods: {len(methods)}")
    for row in method_rows:
        if not any(term in (row["name"] or "").lower() for term in ("ipcc", "cml", "recipe", "ef ")):
            continue
        print(f"  {row['name']} | {row['uuid']}")
    # Export all matches; the display limit only controls terminal output.
    for filename, rows, fields in [
        ("process_name_matches.csv", all_rows, ["group", "name", "location", "unit", "uuid", "category"]),
        ("lcia_methods.csv", method_rows, ["name", "uuid", "category"]),
    ]:
        path = output / filename
        with path.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved {len(rows)} rows: {path}")
    print("\nName matches are candidates, not validated substitutes. Check product, geography, technology and allocation.")
    print("Generic feed, sugar and lime results require review; missing matches do not prove absence.")
    print("Database version is not verified by process names. Keep these metadata exports private.")


if __name__ == "__main__":
    main()
