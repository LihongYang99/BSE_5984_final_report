# Step 32: Audit existing background systems without writing database entities.
"""Read-only IPC audit: existing systems only; explicit functional units.
No create/put/delete calls. New run directories preserve every earlier result.
"""
from pathlib import Path
from datetime import datetime
import argparse, csv, hashlib, json, math, shutil
import olca_ipc as ipc
import olca_schema as o

ROOT = Path(__file__).resolve().parents[1]
METHOD = '9488e228-f9d7-4921-b616-0cad160d96f7'
CATEGORY = 'Climate change: total (excl. biogenic CO2) - Global warming potential (GWP100)'
# Pin the reviewed system UUIDs and expected units for a reproducible audit.
SYSTEMS = {
    'electricity': ('931b7343-5d8e-4f14-ab2e-2fd147a3191d', 'kWh'),
    'feed_partial': ('ae397b2d-ec58-4433-af49-3bdc3d3fe9c0', 'kg'),
    'meat_bone_meal': ('96009269-15a4-4226-871e-31c76ad85b6f', 'kg'),
    'wheat_bran': ('e294d97c-57c6-43c9-99c3-265d19b2632a', 'kg'),
    'soybean_oil': ('443f64eb-d020-46d2-acb1-31fbec182c75', 'kg'),
    'steam': ('402629e8-7399-4f5d-84ec-9f2c869a01d7', 'kg'),
    'tap_water': ('7ed83f57-7198-4300-80f0-8992c6474720', 'kg'),
    'truck_transport': ('6c1efb11-3aa2-4454-8376-4218cdcc8c6e', 't*km'),
    'sodium_bicarbonate': ('b050ff76-933b-4d4d-8e4f-c2d3f548ea62', 'kg'),
}

# Write derived audit tables; this helper does not interact with openLCA.
def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    out = args.out or ROOT / 'results' / datetime.now().astimezone().strftime('run_%Y%m%d_%H%M%S')
    # Create a new run and archive earlier files before any calculations.
    out.mkdir(parents=True, exist_ok=False)
    archive = out / 'legacy'; archive.mkdir()
    hashes = {}
    for name in ['README.md', 'data', 'outputs', 'scripts', 'figures']:
        source = ROOT / name
        if source.is_dir(): shutil.copytree(source, archive / name)
        else: shutil.copy2(source, archive / name)
    for p in archive.rglob('*'):
        if p.is_file(): hashes[str(p.relative_to(archive))] = hashlib.sha256(p.read_bytes()).hexdigest()
    (out / 'legacy_sha256.json').write_text(json.dumps(hashes, indent=2))
    # Use the active JSON-RPC server only to read and calculate existing systems.
    client = ipc.Client(8080)
    rows, checks = [], []
    before = sorted(d.id for d in client.get_descriptors(o.ProductSystem))
    # Check the reference unit and direct default-provider links for each background system.
    for label, (uid, expected_unit) in SYSTEMS.items():
        system = client.get(o.ProductSystem, uid)
        if system is None: raise RuntimeError(f'Missing existing system: {label}; no system will be created')
        proc = client.get(o.Process, system.ref_process.id)
        refs = [e for e in proc.exchanges or [] if e.is_quantitative_reference and not e.is_input]
        assert len(refs) == 1
        ref = refs[0]
        assert ref.unit.name == expected_unit, (label, ref.unit.name)
        root_links = {l.exchange.internal_id: l.provider.id for l in system.process_links or [] if l.process.id == proc.id}
        for e in proc.exchanges or []:
            if e.is_input and e.default_provider:
                assert root_links.get(e.internal_id) == e.default_provider.id, (label, e.internal_id)
        # Specify unit and flow property explicitly to prevent the previous MJ/kWh error.
        setup = o.CalculationSetup(target=o.Ref(ref_type=o.RefType.ProductSystem, id=uid),
            impact_method=o.Ref(ref_type=o.RefType.ImpactMethod, id=METHOD),
            amount=1.0, unit=ref.unit, flow_property=ref.flow_property)
        result = client.calculate(setup)
        try:
            result.wait_until_ready()
            match = [x for x in result.get_total_impacts() if x.impact_category.name == CATEGORY]
            assert len(match) == 1
            gwp = float(match[0].amount)
            # Reconcile direct process contributions with the reported total GWP.
            contributions = result.get_impact_contributions_of(match[0].impact_category)
            total = sum(x.amount for x in contributions)
            assert math.isclose(total, gwp, abs_tol=1e-8, rel_tol=1e-8)
            demand = result.get_demand()
            rows.append(dict(label=label,ef=gwp,unit=expected_unit,system_uuid=uid,provider_uuid=proc.id,
                process_name=proc.name,location=getattr(proc.location,'name',''),reference_product=ref.flow.name,
                demand_reference_amount=demand.amount,demand_reference_unit=demand.tech_flow.flow.ref_unit,
                processes=len(system.processes),links=len(system.process_links),contribution_sum=total))
            # For electricity, verify both the 3.6 conversion and returned demand in MJ.
            if label == 'electricity':
                write_csv(out / 'electricity_contributions_corrected.csv', [dict(provider=x.tech_flow.provider.name,
                    provider_uuid=x.tech_flow.provider.id,contribution=x.amount) for x in contributions])
                assert math.isclose(gwp,0.1353780587964153*3.6,rel_tol=1e-8)
                assert math.isclose(demand.amount,3.6)
            checks.append(dict(check=f'{label}: explicit unit, root default links, contribution reconciliation',status='PASS'))
            print(f'{label}: {gwp:.9f} kg CO2-eq/{expected_unit}', flush=True)
        finally: result.dispose()
        write_csv(out / 'background_factors.csv', rows)
    # Confirm the system list is unchanged and record the audit scope and limitations.
    assert sorted(d.id for d in client.get_descriptors(o.ProductSystem)) == before
    checks.append(dict(check='No product systems created or removed',status='PASS'))
    write_csv(out / 'ipc_validation.csv', checks)
    (out / 'provenance.json').write_text(json.dumps(dict(timestamp=datetime.now().astimezone().isoformat(),
        method_uuid=METHOD,category=CATEGORY,ipc_port=8080,database_access='read-only; existing systems',
        database_name='Not verified through IPC; no database writes performed',
        limitation='Root links checked; not an exhaustive audit of all upstream exchanges'),indent=2))
    print('RUN_DIRECTORY='+str(out))

if __name__ == '__main__': main()
