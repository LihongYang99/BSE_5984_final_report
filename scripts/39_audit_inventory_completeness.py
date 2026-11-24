"""Calculate missing known inputs read-only; preserve the November 21 run.

Unknown hatchery and farm-emission burdens remain unresolved, not zero.
Run with the project Python while the standard openLCA IPC server is active.
"""
from pathlib import Path
import argparse
import csv
import importlib.util
import json
import math

import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'results/run_2026-11-21'
METHOD = '9488e228-f9d7-4921-b616-0cad160d96f7'
CATEGORY = 'Climate change: total (excl. biogenic CO2) - Global warming potential (GWP100)'
PROVIDERS = {
    'air_generic': ('e17442cb-88c0-333a-b12e-c7eacf17e67f', 't*km'),
    'air_short': ('87539f6a-8474-3d4f-a652-5bcec41c02bd', 't*km'),
    'air_medium': ('b0311243-94ba-3864-a0d5-66da9bd29ea1', 't*km'),
    'urea': ('04d4d042-54c2-3c06-a0a9-572ba0f3a5fc', 'kg'),
    'triple_superphosphate': ('ce1c647d-1dba-38af-a72c-cab2189fd107', 'kg'),
    # Independent target-mode check against the reviewed product-system calculation.
    'electricity_check': ('483cde5f-7ae5-379e-ae10-54bb8fbbe6a2', 'kWh'),
}


def read_csv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'results/completeness_2026-11-23')
    parser.add_argument('--offline', action='store_true', help='Reuse saved factors for document/plot regeneration')
    args = parser.parse_args()
    out = args.out
    out.mkdir(exist_ok=True, parents=True)
    target = out/'added_background_factors.csv'
    ef = {r['label']:float(r['ef']) for r in read_csv(OLD/'background_factors.csv')}
    if not args.offline:
        if target.exists():
            raise FileExistsError('Use a new output directory or --offline; existing factors are preserved')
        c = ipc.Client(8080)
        before = sorted(x.id for x in c.get_descriptors(o.ProductSystem))
        rows = []
        for key,(uid,unit) in PROVIDERS.items():
            proc = c.get(o.Process,uid)
            ref = next(e for e in proc.exchanges if e.is_quantitative_reference and not e.is_input)
            assert ref.unit.name == unit
            (out/f'{key}_provider.json').write_text(json.dumps(proc.to_dict(),indent=2))
            setup = o.CalculationSetup(target=o.Ref(ref_type=o.RefType.Process,id=uid),
                impact_method=o.Ref(ref_type=o.RefType.ImpactMethod,id=METHOD),
                amount=1,unit=ref.unit,flow_property=ref.flow_property)
            result = c.calculate(setup)
            try:
                result.wait_until_ready()
                state = result.get_state()
                if state.error:
                    raise RuntimeError(state.error)
                impacts = result.get_total_impacts()
                match = [x for x in impacts if x.impact_category.name == CATEGORY]
                assert len(match)==1
                gwp = match[0].amount
                contrib = result.get_impact_contributions_of(match[0].impact_category)
                assert math.isclose(sum(x.amount for x in contrib),gwp,abs_tol=1e-8)
                demand = result.get_demand()
                assert math.isclose(demand.amount,3.6 if unit=='kWh' else 1.0)
                # A market has little direct impact: require linked upstream contributors.
                assert sum(abs(x.amount)>1e-12 for x in contrib)>10
                rows.append(dict(label=key,ef=gwp,unit=unit,provider_uuid=uid,
                    process_name=proc.name,location=proc.location.name,
                    reference_product=ref.flow.name,demand=demand.amount,
                    demand_unit=demand.tech_flow.flow.ref_unit,contribution_sum=sum(x.amount for x in contrib)))
                (out/f'{key}_impacts.json').write_text(json.dumps([x.to_dict() for x in impacts],indent=2))
                print(f'{key}: {gwp:.9f} kg CO2-eq/{unit}',flush=True)
            finally:
                result.dispose()
        after = sorted(x.id for x in c.get_descriptors(o.ProductSystem))
        assert before==after
        write_csv(target,rows)
        (out/'ipc_checks.json').write_text(json.dumps({'systems_before':before,'systems_after':after,
            'database_writes':False,'target':'Process; transient calculation',
            'method':METHOD,'category':CATEGORY,'all_contribution_sums_pass':True},indent=2))
    factors = {r['label']:float(r['ef']) for r in read_csv(target)}
    assert math.isclose(factors['electricity_check'],ef['electricity'],rel_tol=1e-8)

    spec = importlib.util.spec_from_file_location('indiana',ROOT/'scripts/31_calculate_indiana_farming_gwp.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    inv = {r['flow']:r for r in read_csv(OLD/'source_inventory_verified.csv')}
    results=[];hotspots=[]
    for case,fcr,electricity,bicarbonate in [('Indiana',1.5,.921,.110),('Alabama',1.02,8.799,0)]:
        contributions=model.components(ef,fcr=fcr,electricity=electricity,bicarbonate=bicarbonate)
        original=sum(contributions.values())
        additions={
            'Larval airfreight':float(inv['larvae_airfreight'][case])*factors['air_generic'],
            'Urea supply':float(inv['urea'][case])*factors['urea'],
            'Triple superphosphate supply':float(inv['triple_superphosphate'][case])*factors['triple_superphosphate'],
        }
        contributions.update(additions)
        total=sum(contributions.values())
        results.append(dict(case=case,previous_covered_subtotal=original,added_gwp=sum(additions.values()),
            updated_covered_subtotal=total,airfreight=additions['Larval airfreight'],
            fertilizer_supply=additions['Urea supply']+additions['Triple superphosphate supply'],
            status='Expanded covered inventory; hatchery and direct farm GHGs unresolved'))
        for component,gwp in contributions.items():
            hotspots.append(dict(case=case,component=component,gwp=gwp,share_pct=100*gwp/total))
    write_csv(out/'expanded_results.csv',results)
    write_csv(out/'expanded_hotspots.csv',hotspots)
    # Alternative air-service markets are provider scenarios, not statistical bounds.
    air=[]
    for case in ['Indiana','Alabama']:
        amount=float(inv['larvae_airfreight'][case])
        for key in ['air_generic','air_short','air_medium']:
            air.append(dict(case=case,provider_scenario=key,tkm=amount,ef=factors[key],gwp=amount*factors[key]))
    write_csv(out/'air_provider_scenarios.csv',air)
    # Published Chinese hatchery burdens are external comparators only, not US factors.
    benchmarks=[]
    for case in ['Indiana','Alabama']:
        base=next(x['updated_covered_subtotal'] for x in results if x['case']==case)
        for source,value in [('Cao 2011 semi-intensive hatchery',70.8/1000),('Cao 2011 intensive hatchery',188/1000)]:
            benchmarks.append(dict(case=case,source=source,external_addon=value,
                conditional_total=base+value,percent_of_covered_total=100*value/base,
                status='External China benchmark; not US baseline or uncertainty bound'))
    write_csv(out/'hatchery_external_benchmarks.csv',benchmarks)
    print(json.dumps(results,indent=2))


if __name__=='__main__':
    main()
