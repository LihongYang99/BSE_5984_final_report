# Step 43: Screening estimates for the burdens drawn as "not yet quantified" in Figure C1.
"""Quantify unresolved farm burdens from literature factors and explicit assumptions.

Offline: reads the expanded subtotals and the audited electricity factor, writes
results/unresolved_2026-11-24/. Each item has low, central and high values in
kg CO2-eq per kg live-weight shrimp. These are deterministic screening ranges, not
confidence intervals, and they are not added to the reviewed subtotals.

GWP100 values follow IPCC AR6 as used by IPCC 2021 GWP100 in openLCA:
biogenic CH4 27.0, N2O 273.
"""
from pathlib import Path
import csv, json

ROOT = Path(__file__).resolve().parents[1]
EXPANDED = ROOT / 'results/completeness_2026-11-23/expanded_summary.json'
FACTORS = ROOT / 'results/run_2026-11-21/background_factors.csv'
OUT = ROOT / 'results/unresolved_2026-11-24'

GWP_CH4_BIO, GWP_N2O = 27.0, 273.0
N2O_PER_N2O_N = 44 / 28
HOURS_PER_WEEK = 168

# Farm inventory (Al Eissa et al. 2022, Table 2, per kg live shrimp).
FCR = {'Indiana': 1.5, 'Alabama': 1.02}
ALABAMA_POND_AREA = 1.456      # m2 per kg shrimp (1456 m2 per t)
ALABAMA_WATER = 1.456          # m3 per kg shrimp, one pond fill
ALABAMA_UREA = 0.0017          # kg urea per kg shrimp
ALABAMA_N_DISCHARGE = 0.001    # kg N per kg shrimp (1 kg per t)

# Yang et al. (2023) J. Hydrology 617:128876, aerated Penaeus vannamei ponds, salinity ~4 ppt.
CH4_FLUX = (4.50 - 1.73, 4.50, 4.50 + 1.73)   # mg m-2 h-1, aerated mean +- SD (AP I/AP II)
N2O_FLUX = (11.72, (11.72 + 15.96) / 2, 15.96)  # ug m-2 h-1, AP II, mean, AP I
YANG_SEASON_H = 214 * 24      # May-November single crop (~214 days)
YANG_FEED = 9044              # kg feed ha-1 per crop, authors' estimate (FCR 1.33)

# IPCC 2013 Wetlands Supplement, Table 4.15 and Annex 4A.5: N retained in product and
# 1.8 +- 0.7 % of N released to water emitted as N2O-N (wastewater-plant analogy).
N2O_CONVERSION = (0.011, 0.018, 0.025)
PRODUCT_N = 0.0284            # kg N per kg live product (IPCC default for fish biomass)
FEED_CP = (0.35, 0.36, 0.40)  # assumed crude protein of Feed C (not reported)


def lch(low, central, high):
    return dict(low=low, central=central, high=high)


def main():
    if OUT.exists():
        raise SystemExit(f'{OUT} exists; remove it or choose a new directory before rerunning.')
    ex = json.loads(EXPANDED.read_text())
    with FACTORS.open() as f:
        grid = next(float(x['ef']) for x in csv.DictReader(f) if x['label'] == 'electricity')
    covered = {'Indiana': ex['indiana'], 'Alabama': ex['alabama']}
    rows = []

    def add(case, item, values, method, sources, assumptions, confidence):
        rows.append(dict(case=case, item=item, **{k: round(v, 4) for k, v in values.items()},
                         method=method, sources=sources, assumptions=assumptions, confidence=confidence))

    # Hatchery production: external benchmarks (already documented in the evidence review).
    for case in covered:
        add(case, 'Hatchery production', lch(0.0708, (0.0708 + 0.188) / 2, 0.188),
            'Published hatchery GWP per kg harvested shrimp; central is the midpoint',
            'Cao et al. 2011, Table 2', 'Chinese semi-intensive and intensive hatcheries transfer to Florida hatcheries', 'Low')

    # Direct N2O, nitrogen balance (IPCC Tier 1 logic with project FCR and assumed feed protein).
    def n2o_balance(case, cp, conv):
        n_in = FCR[case] * cp / 6.25 + (ALABAMA_UREA * 0.46 if case == 'Alabama' else 0)
        return max(n_in - PRODUCT_N, 0) * conv * N2O_PER_N2O_N * GWP_N2O
    ind = lch(*(n2o_balance('Indiana', cp, c) for cp, c in zip(FEED_CP, N2O_CONVERSION)))
    add('Indiana', 'Direct N2O (biofloc tanks)', ind,
        'N balance: feed N minus product N, times N2O-N conversion',
        'IPCC 2013 Wetlands Supplement Table 4.15 and Annex 4A.5; Hu et al. 2012',
        'Feed crude protein 35-40%; conversion 1.1-2.5% (1.8 +- 0.7%); aerated biofloc behaves like activated sludge', 'Low to medium')

    # Pond N2O: measured fluxes scaled by area and time (low, central) and N balance (high).
    weeks = 13
    pond_n2o_low = N2O_FLUX[0] * 1e-9 * weeks * HOURS_PER_WEEK * ALABAMA_POND_AREA * GWP_N2O
    pond_n2o_mid = N2O_FLUX[1] * 1e-9 * weeks * HOURS_PER_WEEK * ALABAMA_POND_AREA * GWP_N2O
    add('Alabama', 'Direct N2O (pond)', lch(pond_n2o_low, pond_n2o_mid, n2o_balance('Alabama', FEED_CP[2], N2O_CONVERSION[2])),
        'Low and central: measured pond flux x 1.456 m2 x 13-week grow-out. High: N balance as for Indiana',
        'Yang et al. 2023; IPCC 2013 Wetlands Supplement; Davis et al. 2018 (13-week trials, Claude Peteet Mariculture Center)',
        'Chinese estuarine pond fluxes transfer to lined Gulf Shores ponds; 13-week grow-out', 'Medium')

    # Pond CH4: two normalizations of Yang's aerated-pond flux.
    by_time = [f * 1e-6 * weeks * HOURS_PER_WEEK * ALABAMA_POND_AREA for f in CH4_FLUX]
    ch4_per_feed = CH4_FLUX[1] * 1e-6 * 1e4 * YANG_SEASON_H / YANG_FEED   # kg CH4 per kg feed
    by_feed = ch4_per_feed * FCR['Alabama']
    ch4_high = CH4_FLUX[2] * 1e-6 * 1e4 * YANG_SEASON_H / YANG_FEED * FCR['Alabama']
    add('Alabama', 'Pond CH4 (biogenic)',
        lch(by_time[0] * GWP_CH4_BIO, (by_time[1] + by_feed) / 2 * GWP_CH4_BIO, ch4_high * GWP_CH4_BIO),
        'Low: low flux x area x 13 weeks. Central: mean of area-time and feed-normalized estimates. High: high flux per kg feed',
        'Yang et al. 2023 (CH4 4.50 +- 1.73 mg m-2 h-1; feed ~9044 kg ha-1)',
        'Ebullition-dominated CH4 from unlined Chinese ponds; HDPE-lined Alabama ponds likely emit less; 13-week grow-out (Davis et al. 2018)', 'Low to medium')

    # Infrastructure.
    add('Indiana', 'Infrastructure', lch(0, 0.002, 0.004),
        'Upper value is 0.1% of the source total GWP (4025 kg CO2-eq per t, Feed C)',
        'Al Eissa et al. 2022, Section 2.2.3 and Table 3', 'Source preliminary screening transfers to this model', 'Medium')
    add('Alabama', 'Infrastructure', lch(0.0205, (0.0205 + 0.0645) / 2, 0.0645),
        'Published grow-out infrastructure GWP per kg shrimp', 'Cao et al. 2011, Table 2',
        'Chinese pond infrastructure transfers to lined Gulf Shores ponds', 'Low')

    # Land-use change: none within the 20-year IPCC amortization window.
    for case, note in [('Indiana', 'Indoor facility; no recent land conversion documented (assumption)'),
                       ('Alabama', 'Claude Peteet Mariculture Center ponds built in 1973, beyond 20-year amortization')]:
        add(case, 'Land-use change', lch(0, 0, 0), 'No conversion within 20 years', 'Alabama Gulf Seafood 2020 (ponds built 1973, HDPE liners 1986); 20-year amortization convention', note, 'Medium')

    # Alabama pond filling: low-head pumping from the Intracoastal Waterway.
    pump = [ALABAMA_WATER * 1000 * 9.81 * h / eff / 3.6e6 * grid for h, eff in [(3, 0.7), (5, 0.6), (10, 0.5)]]
    add('Alabama', 'Pond-fill pumping', lch(*pump), 'rho g h V / efficiency x US grid factor',
        'Al Eissa et al. 2022 Table 2 (water volume); site description', 'Head 3-10 m, efficiency 0.5-0.7; may already be in farm electricity', 'Medium')

    # Small Alabama terms: effluent N and urea hydrolysis.
    eff = [ALABAMA_N_DISCHARGE * ef * N2O_PER_N2O_N * GWP_N2O for ef in (0.0005, 0.0075, 0.025)]
    add('Alabama', 'Indirect N2O from discharged N', lch(*eff), 'N discharged x EF5 (leaching and runoff)',
        'Al Eissa et al. 2022 Table 2; IPCC 2006 Vol. 4 Ch. 11 Table 11.3 (EF5 0.0075, range 0.0005-0.025)',
        'Pond discharge treated like agricultural runoff', 'Medium')
    urea = ALABAMA_UREA * 0.20 * 44 / 12
    add('Alabama', 'Urea hydrolysis CO2', lch(urea, urea, urea), 'Urea x 0.20 kg C per kg x 44/12',
        'IPCC 2006 Vol. 4 Ch. 11, Section 11.4 (EF 0.20)', 'All urea C released as CO2', 'High')

    # Not quantified: Indiana tank CH4 and sludge fate need site data.
    for item, need in [('Tank CH4 and sludge fate', 'Sludge mass, solids removal and disposal route (sewer, landfill or land application)')]:
        rows.append(dict(case='Indiana', item=item, low='', central='', high='', method='Not quantified',
                         sources='Al Eissa et al. 2022 mentions landfill of separated sludge as an option', assumptions=need, confidence='None'))

    OUT.mkdir(parents=True)
    with (OUT / 'unresolved_estimates.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

    summary = {}
    for case in covered:
        q = [r for r in rows if r['case'] == case and r['central'] != '']
        add_u = {k: sum(r[k] for r in q) for k in ('low', 'central', 'high')}
        summary[case] = dict(covered=covered[case], unresolved=add_u,
                             total={k: covered[case] + v for k, v in add_u.items()},
                             increase_pct={k: 100 * v / covered[case] for k, v in add_u.items()})
    gap = covered['Alabama'] - covered['Indiana']
    worst = summary['Indiana']['unresolved']['high'] - summary['Alabama']['unresolved']['low']
    summary['ranking'] = dict(covered_gap=gap, worst_case_U_Indiana_minus_U_Alabama=worst, reverses=worst > gap,
                              note='Indiana sludge/tank CH4 not quantified; it would need to exceed the remaining margin to reverse the ranking',
                              remaining_margin=gap - worst)
    (OUT / 'unresolved_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    for r in rows: print(f"{r['case']:8} {r['item']:32} {r['low']!s:>8} {r['central']!s:>8} {r['high']!s:>8}")
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
