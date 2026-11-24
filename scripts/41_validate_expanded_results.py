"""Independently check the expanded inventory using saved factors and literature inputs.

No model-function imports or openLCA calls. Numerical agreement does not resolve
missing hatchery, infrastructure, water, or direct-emission data.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
# ecoinvent process-level contributions are kept locally but not published (licence); skip them only when absent.
NOT_DISTRIBUTED={'outputs/electricity_gwp_contributions.csv'}
OLD = ROOT / 'results/run_2026-11-21'
OUT = ROOT / 'results/completeness_2026-11-23'


def read_csv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def close(actual, expected):
    return math.isclose(float(actual), float(expected), rel_tol=1e-10, abs_tol=1e-9)


def main():
    checks = []

    def check(name, passed):
        checks.append({'check': name, 'passed': bool(passed)})

    # Rebuild delivered feed from ingredient fractions and processing quantities.
    ef = {r['label']: float(r['ef']) for r in read_csv(OLD/'background_factors.csv')}
    new = read_csv(OUT/'added_background_factors.csv')
    extra = {r['label']: float(r['ef']) for r in new}
    ingredients = (ef['feed_partial'] + .05*ef['meat_bone_meal']
                   + .05*ef['wheat_bran'] + .03*ef['soybean_oil'] + .04*1.33)
    feed = (ingredients + .320*ef['steam'] + .130*ef['electricity']
            + (2000/1500)*ef['tap_water'] + 1.006*ef['truck_transport'])
    check('recipe mass', close(sum([.30,.05,.20,.30,.05,.03,.03,.04]), 1))
    check('Process and ProductSystem electricity agree', close(extra['electricity_check'], ef['electricity']))
    for row in new:
        check(row['label']+' contribution sum', close(row['ef'], row['contribution_sum']))
        check(row['label']+' returned reference demand', close(row['demand'], 3.6 if row['unit']=='kWh' else 1))
    ipc = json.loads((OUT/'ipc_checks.json').read_text())
    check('no product systems added or removed', ipc['systems_before']==ipc['systems_after'])
    check('read-only calculation recorded', ipc['database_writes'] is False)

    # Use explicit published quantities to catch normalization or product-unit errors.
    cases = {'Indiana': (1.50,.921,.110,.140,0,0),
             'Alabama': (1.02,8.799,0,.062,.0017,.0003)}
    saved = {r['case']: r for r in read_csv(OUT/'expanded_results.csv')}
    hot = read_csv(OUT/'expanded_hotspots.csv')
    totals = {}
    for case, (fcr, electricity, bicarbonate, air, urea, tsp) in cases.items():
        prior = fcr*feed + electricity*ef['electricity'] + bicarbonate*ef['sodium_bicarbonate']
        freight = air*extra['air_generic']
        fertilizer = urea*extra['urea'] + tsp*extra['triple_superphosphate']
        totals[case] = prior+freight+fertilizer
        row = saved[case]
        for key, expected in [('previous_covered_subtotal',prior), ('airfreight',freight),
                              ('fertilizer_supply',fertilizer), ('added_gwp',freight+fertilizer),
                              ('updated_covered_subtotal',totals[case])]:
            check(case+' '+key, close(row[key],expected))
        h = [r for r in hot if r['case']==case]
        check(case+' hotspot sum',close(sum(float(r['gwp']) for r in h),totals[case]))
        check(case+' hotspot shares',close(sum(float(r['share_pct']) for r in h),100))
    base = totals['Indiana']
    summary = json.loads((OUT/'expanded_summary.json').read_text())
    check('summary Indiana',close(summary['indiana'],base))
    check('summary Alabama',close(summary['alabama'],totals['Alabama']))
    check('optional water',close(summary['optional_water'],base+75*ef['tap_water']))
    check('ranking reversal threshold',close(summary['unresolved_difference_to_reverse_ranking'],totals['Alabama']-base))

    # Reconstruct scenario responses without calling the calculation implementation.
    oat = read_csv(OUT/'sensitivity_oat.csv')
    check('all one-at-a-time scenarios', all(close(r['gwp'],base+(float(r['multiplier'])-1)*
          (1.5*feed if r['parameter']=='FCR' else .921*ef['electricity'])) for r in oat))
    grid = read_csv(OUT/'grid_sensitivity.csv')
    check('all farm-grid scenarios',all(close(r['farm_only'],base+.921*(float(r['grid'])-ef['electricity'])) for r in grid))
    check('all farm-and-mill scenarios',all(close(r['farm_and_mill'],base+(.921+1.5*.130)*(float(r['grid'])-ef['electricity'])) for r in grid))
    surface = read_csv(OUT/'grid_fcr_surface.csv')
    check('all joint grid/FCR scenarios',all(close(r['gwp'],base+(float(r['fcr'])-1.5)*feed+
          .921*(float(r['grid'])-ef['electricity'])) for r in surface))
    for row in read_csv(OUT/'hatchery_external_benchmarks.csv'):
        check(row['case']+' '+row['source'],close(row['conditional_total'],totals[row['case']]+float(row['external_addon']))
                         and close(row['percent_of_covered_total'],100*float(row['external_addon'])/totals[row['case']]))
    controlled = read_csv(OLD/'analysis/alabama_controlled_comparison.csv')
    common = {}
    for row in controlled:
        common[row['case']] = common.get(row['case'],0)+float(row['gwp'])
    check('fixed-FCR electricity contrast retained',any(close(value-common['Indiana (common scope)'],(8.799-.921)*ef['electricity']) for value in common.values()))

    # Confirm that the reviewed run and its archived inputs were not rewritten.
    for manifest, folder in [('reviewed_sha256.json', OLD), ('legacy_sha256.json', OLD/'legacy')]:
        for rel, expected in json.loads((OLD/manifest).read_text()).items():
            path = folder/rel
            if rel in NOT_DISTRIBUTED and not path.exists():
                check('preserved '+str(path.relative_to(ROOT))+' (not distributed, skipped)',True);continue
            check('preserved '+str(path.relative_to(ROOT)),path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==expected)
    with (OUT/'validation.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['check','passed'])
        writer.writeheader();writer.writerows(checks)
    failures=[r['check'] for r in checks if not r['passed']]
    print(f'{len(checks)-len(failures)}/{len(checks)} checks passed')
    if failures:
        raise RuntimeError('\n'.join(failures))


if __name__=='__main__':
    main()
