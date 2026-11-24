# Step 31: Assemble reviewed Indiana GWP from explicitly unit-audited background factors.
"""Step 31, reviewed: reproduce Indiana screening from explicitly unit-audited factors.
Run Step 32 first. Offline: no database writes and no legacy CSV overwrites.
"""
from pathlib import Path
import argparse
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Return stage contributions per kg live shrimp; optional grid changes are scenario inputs.
def components(ef, fcr=1.5, electricity=0.921, grid=None, distance_km=1006,
               bicarbonate=0.110, treated_water_kg=0.0, mill_grid=None):
    # Default farm and mill electricity to the audited factor unless a scenario overrides them.
    grid = ef['electricity'] if grid is None else grid
    mill_grid = ef['electricity'] if mill_grid is None else mill_grid
    # Scale feed inputs by FCR; farm electricity, bicarbonate, and water use their own quantities.
    return {
        'Feed ingredients': fcr * (ef['feed_partial'] + .05*ef['meat_bone_meal'] + .05*ef['wheat_bran'] + .03*ef['soybean_oil'] + .04*1.33),
        'Feed steam': fcr * .32 * ef['steam'],
        'Feed mill electricity': fcr * .13 * mill_grid,
        'Feed mill water proxy': fcr * (2000/1500) * ef['tap_water'],
        'Feed delivery': fcr * distance_km/1000 * ef['truck_transport'],
        'Farm electricity': electricity * grid,
        'Sodium bicarbonate': bicarbonate * ef['sodium_bicarbonate'],
        'Farm tap-water proxy': treated_water_kg * ef['tap_water'],
    }

def main():
    # Choose an audited run and create a fresh analysis directory.
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True, help='Step 32 run directory')
    a = p.parse_args(); out=a.run/'analysis'; out.mkdir(exist_ok=False)
    # Verify the explicit kWh basis and finite factors before assembling farm results.
    factors=pd.read_csv(a.run/'background_factors.csv').set_index('label')
    ef=factors.ef.to_dict()
    assert factors.loc['electricity','unit']=='kWh'
    assert math.isclose(factors.loc['electricity','demand_reference_amount'],3.6)
    assert all(math.isfinite(x) and x>=0 for x in ef.values())
    # Reconstruct Feed C and reconcile the unit correction with the preserved legacy result.
    base=components(ef); total=sum(base.values())
    feed=sum(v for k,v in base.items() if k.startswith('Feed'))/1.5
    legacy=pd.read_csv(a.run/'legacy/outputs/feed_c_hotspot_analysis.csv').gwp_per_kg_feed.sum()
    expected=legacy+.13*(ef['electricity']-.1353780587964153)+(2000/1500-1.333333)*ef['tap_water']
    assert math.isclose(feed,expected,abs_tol=1e-8), (feed,expected)
    # Export hotspot shares and keep the optional farm-water proxy as a separate case.
    pd.DataFrame([dict(component=k,gwp=v,share_pct=100*v/total) for k,v in base.items()]).to_csv(out/'indiana_hotspots.csv',index=False)
    pd.DataFrame([
        dict(scenario='Legacy retained',feed_gwp=legacy,shrimp_gwp=2.066366013241343,status='Superseded: MJ mislabeled kWh'),
        dict(scenario='Corrected screening; no farm water treatment',feed_gwp=feed,shrimp_gwp=total,status='Proxy-assisted; incomplete boundary'),
        dict(scenario='Corrected screening; 75 kg tap-water proxy',feed_gwp=feed,shrimp_gwp=sum(components(ef,treated_water_kg=75).values()),status='Optional proxy; water source unverified'),
    ]).to_csv(out/'indiana_results.csv',index=False)
    print(f'Corrected Feed C: {feed:.9f}; Indiana: {total:.9f}; optional water: {total+75*ef["tap_water"]:.9f}')

if __name__=='__main__':main()
