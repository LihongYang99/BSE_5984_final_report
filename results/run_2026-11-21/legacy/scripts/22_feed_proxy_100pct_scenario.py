"""Step 22: Proxy-completed Feed C ingredient GWP screening (VS Code + openLCA).

Uses published Feed C mass shares (Al Eissa et al., 2022) without changing recipe.
Unchanged V1 covers 83%; adds explicitly labeled proxies for the remaining 17%:
 - poultry by-product meal -> RoW meat and bone meal (ecoinvent)
 - rice bran -> RoW wheat bran (ecoinvent, milling coproduct proxy)
 - soybean lecithin -> US refined soybean oil (ecoinvent, lipid proxy)
 - supplements -> 1.33 kg CO2e/kg vitamin-mineral mix from SINTEF (2020),
                  used as a crude literature assumption for an unknown blend.

This is a HYBRID, PROXY-ASSISTED SCREENING estimate, not a harmonized full LCA.
No existing Feed C V1 process is modified.

By default: read-only dry run.  With --calculate: may create two new Product
Systems for background providers in the ACTIVE database (use your database
copy Shrimp_LCA_US_2026). It saves derived CSVs and a diagnostic figure.
"""

from pathlib import Path
import argparse
import csv

import matplotlib.pyplot as plt
import pandas as pd
import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
DATA = ROOT / "data"
for d in (OUT, FIG, DATA):
    d.mkdir(exist_ok=True)

IPCC_METHOD_ID = "9488e228-f9d7-4921-b616-0cad160d96f7"
IPCC_CATEGORY = (
    "Climate change: total (excl. biogenic CO2) "
    "- Global warming potential (GWP100)"
)

# Al Eissa et al. (2022) Feed C ingredient fractions; 1 kg nominal feed basis.
MBM_SHARE = 0.05
BRAN_SHARE = 0.05
LECITHIN_SHARE = 0.03
SUPPLEMENTS_SHARE = 0.04
FCR = 1.5

# Campos et al. (2020): economic allocation, Portugal, CML method.
# Methodologically different from ecoinvent/IPCC; sensitivity scenario only.
CAMPOS_PBM_EF = 0.726

# SINTEF Ocean 2020 report, p. 51: vitamins/minerals delivered to Norway feed mill.
# An assumption for the full, undisclosed 4% supplements is imperfect.
SINTEF_PREMIX_EF = 1.33


def read_v1_partial() -> float:
    path = OUT / "feed_c_partial_gwp_summary.csv"
    if not path.exists():
        raise FileNotFoundError(f"Run Step 17 first: missing {path}")
    df = pd.read_csv(path)
    row = df.loc[
        df["indicator"] == "Partial GWP per kg nominal Feed C", "amount"
    ]
    if len(row) != 1:
        raise ValueError(f"Cannot uniquely read V1 partial GWP from {path}")
    return float(row.iloc[0])


def read_mbm_ef() -> float:
    path = OUT / "poultry_proxy_scenario.csv"
    if not path.exists():
        raise FileNotFoundError(f"Run Step 18 first: missing {path}")
    df = pd.read_csv(path)
    if len(df) != 1:
        raise ValueError("Expected exactly one MBM proxy row")
    return float(df.loc[0, "ef_kg_co2eq_per_kg"])


def reference_info(process):
    refs = [
        ex for ex in (process.exchanges or [])
        if ex.is_quantitative_reference and not ex.is_input
    ]
    if len(refs) != 1:
        return None
    ex = refs[0]
    return (ex.flow.name if ex.flow else "", ex.unit.name if ex.unit else "")


def locate_proxy(client, *, product, desired, alt, place):
    """Identify supply proxy by exact reference product and preferred geography."""
    candidates = []
    for desc in client.get_descriptors(o.Process):
        name = (desc.name or "").lower()
        if product not in name:
            continue
        proc = client.get(o.Process, desc.id)
        if proc is None:
            continue
        ref = reference_info(proc)
        if ref is None:
            continue
        flow_name, unit_name = ref
        if flow_name.lower() != product or unit_name != "kg":
            continue
        location = getattr(proc.location, "name", "") or ""
        candidates.append((proc, location))
    print(f"\nFound {len(candidates)} valid provider processes for {product!r}:")
    for proc, geo in candidates[:30]:
        print(f"  {geo:36} | {proc.name} | {proc.id}")

    # Strict match to avoid silently using a wrong country or co-product.
    matches = [
        proc for proc, geo in candidates
        if place.lower() in geo.lower() and desired in proc.name.lower()
    ]
    if len(matches) != 1:
        matches = [
            proc for proc, geo in candidates
            if place.lower() in geo.lower() and alt in proc.name.lower()
        ]
    if len(matches) != 1:
        # If there is exactly one candidate of the correct product and geography,
        # we can use it even if the database names the process differently.
        same_region = [
            proc for proc, geo in candidates
            if place.lower() in geo.lower()
        ]
        matches = same_region if len(same_region) == 1 else matches
    if len(matches) != 1:
        raise RuntimeError(
            f"Cannot pick a unique {product} provider in {place}. "
            "Review printed candidates and adjust selection explicitly."
        )
    print(f"SELECTED: {matches[0].name} ({matches[0].id})")
    return matches[0]


def calculate_provider_gwp(client, process):
    system_ref = None
    for desc in client.get_descriptors(o.ProductSystem):
        sys = client.get(o.ProductSystem, desc.id)
        if sys and sys.ref_process and sys.ref_process.id == process.id:
            system_ref = o.Ref(ref_type=o.RefType.ProductSystem, id=sys.id)
            print(f"Reusing existing Product System for {process.name}")
            break
    if system_ref is None:
        print(f"Creating background Product System for {process.name}")
        cfg = o.LinkingConfig(
            prefer_unit_processes=True,
            provider_linking=o.ProviderLinking.PREFER_DEFAULTS,
        )
        system_ref = client.create_product_system(
            o.Ref(ref_type=o.RefType.Process, id=process.id), cfg
        )
        if system_ref is None:
            raise RuntimeError("Could not create Product System")
    result = client.calculate(
        o.CalculationSetup(
            target=system_ref,
            impact_method=o.Ref(
                ref_type=o.RefType.ImpactMethod, id=IPCC_METHOD_ID
            ),
            amount=1.0,
        )
    )
    if result is None:
        raise RuntimeError("LCIA calculation failed to start")
    try:
        result.wait_until_ready()
        matched = [
            item for item in result.get_total_impacts()
            if item.impact_category and item.impact_category.name == IPCC_CATEGORY
        ]
        if len(matched) != 1:
            raise RuntimeError("IPCC 2021 GWP100 category not found uniquely")
        return float(matched[0].amount)
    finally:
        result.dispose()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calculate", action="store_true", help="Run LCIA and save figures; may create Product Systems")
    args = parser.parse_args()

    baseline = read_v1_partial()
    mbm_ef = read_mbm_ef()
    print("Base V1 partial GWP:", f"{baseline:.6f} kg CO2-eq/kg nominal feed")
    print("RoW meat-and-bone-meal EF:", f"{mbm_ef:.6f} kg CO2-eq/kg")

    client = ipc.Client(8080)
    bran = locate_proxy(
        client, product="wheat bran",
        desired="market for wheat bran",
        alt="wheat grain processing, dry milling",
        place="Rest of World",
    )
    soyoil = locate_proxy(
        client, product="soybean oil, refined",
        desired="market for soybean oil, refined",
        alt="soybean oil refining",
        place="United States",
    )

    if not args.calculate:
        print("\nDRY RUN ONLY: no Product Systems created, no calculation.")
        print("Use --calculate ONLY when Shrimp_LCA_US_2026 is open.")
        return

    bran_ef = calculate_provider_gwp(client, bran)
    soyoil_ef = calculate_provider_gwp(client, soyoil)

    contributions = [
        dict(component="Original 83% ingredients (V1)", fraction=0.83,
             ef=None, contribution=baseline,
             dataset="Step 17; ecoinvent 3.11/IPCC 2021", process_uuid=""),
        dict(component="Poultry meal -> RoW meat and bone meal", fraction=MBM_SHARE,
             ef=mbm_ef, contribution=MBM_SHARE * mbm_ef,
             dataset="Step 18; ecoinvent 3.11/IPCC 2021; proxy", process_uuid="36b2c661-ad03-3c43-b53f-9c5980d44d34"),
        dict(component="Rice bran -> RoW wheat bran", fraction=BRAN_SHARE,
             ef=bran_ef, contribution=BRAN_SHARE * bran_ef,
             dataset="ecoinvent 3.11/IPCC 2021; proxy", process_uuid=bran.id),
        dict(component="Soy lecithin -> US refined soybean oil", fraction=LECITHIN_SHARE,
             ef=soyoil_ef, contribution=LECITHIN_SHARE * soyoil_ef,
             dataset="ecoinvent 3.11/IPCC 2021; proxy", process_uuid=soyoil.id),
        dict(component="Supplements -> SINTEF vit/min mix", fraction=SUPPLEMENTS_SHARE,
             ef=SINTEF_PREMIX_EF, contribution=SUPPLEMENTS_SHARE * SINTEF_PREMIX_EF,
             dataset="SINTEF (2020), p.51, Norway incl. transport; literature EF", process_uuid=""),
    ]
    df = pd.DataFrame(contributions)
    if abs(df.fraction.sum() - 1.0) > 1e-9:
        raise AssertionError("Ingredient shares must sum to 100%")

    hybrid_gwp = float(df.contribution.sum())
    campos_gwp = hybrid_gwp + MBM_SHARE * (CAMPOS_PBM_EF - mbm_ef)
    summary = pd.DataFrame([
        dict(scenario="V1 83% partial ingredient supply", gwp_per_kg_nominal_feed=baseline,
             gwp_per_kg_live_shrimp=baseline * FCR,
             notes="Unmodeled 17%; processing/transport excluded"),
        dict(scenario="V2 100%-mass proxy hybrid", gwp_per_kg_nominal_feed=hybrid_gwp,
             gwp_per_kg_live_shrimp=hybrid_gwp * FCR,
             notes="ecoinvent proxies + SINTEF premix literature EF; processing/transport excluded"),
        dict(scenario="V2 sensitivity: Campos PBM factor", gwp_per_kg_nominal_feed=campos_gwp,
             gwp_per_kg_live_shrimp=campos_gwp * FCR,
             notes="Substitutes 0.726 kg CO2e/kg PBM, Campos 2020 CML economic allocation; methods mixed"),
    ])
    df.to_csv(OUT / "feed_c_v2_proxy_contributions.csv", index=False)
    summary.to_csv(OUT / "feed_c_v2_proxy_summary.csv", index=False)
    print("\n=== PROXY SCREENING RESULTS ===")
    print(df[["component", "fraction", "ef", "contribution"]].to_string(index=False))
    print("\n", summary.to_string(index=False))
    print("\nWARNING: Hybrid method; mass represented 100%, but proxies and LCIA bases are not fully harmonized.")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    sorted_df = df.sort_values("contribution")
    bars = ax.barh(sorted_df.component, sorted_df.contribution)
    ax.bar_label(bars, fmt="%.3f", padding=3)
    ax.set_xlabel("GWP contribution (kg CO2-eq/kg nominal Feed C)")
    ax.set_title("Feed C V2: proxy-assisted ingredient supply (screening)")
    ax.set_xlim(right=max(df.contribution) * 1.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "fig06_feed_c_proxy_contributions.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "fig06_feed_c_proxy_contributions.pdf", bbox_inches="tight")
    plt.close(fig)
    print("Saved CSVs in outputs/ and diagnostic figures in figures/")


if __name__ == "__main__":
    main()
