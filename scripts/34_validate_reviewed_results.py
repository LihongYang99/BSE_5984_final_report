# Step 34: Independently verify reviewed numerical results and preserved files.
"""Independent arithmetic and preservation checks; no IPC and no database writes."""
from pathlib import Path
import argparse, hashlib, json, math
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);a=p.parse_args();run=a.run
    # Reconstruct feed and farm totals independently of the Step 31 function.
    ef=pd.read_csv(run/'background_factors.csv').set_index('label').ef
    ingredients=ef.feed_partial+.05*ef.meat_bone_meal+.05*ef.wheat_bran+.03*ef.soybean_oil+.04*1.33
    feed=ingredients+.32*ef.steam+.13*ef.electricity+(2000/1500)*ef.tap_water+1.006*ef.truck_transport
    summary=json.loads((run/'analysis/summary.json').read_text()); checks=[]
    # Record each check and stop immediately if an expected identity fails.
    def check(name,ok):
        checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})
        if not ok:raise AssertionError(name)
    close=lambda a,b:math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9)
    # Check unit conversion, feed fractions, and both counterfactual contrasts.
    check('Explicit kWh equals legacy MJ times 3.6',close(ef.electricity,.1353780587964153*3.6))
    check('Feed fractions sum to one',close(.30+.05+.20+.30+.05+.03+.03+.04,1))
    check('Independent Indiana reconstruction',close(summary['indiana'],1.5*feed+.921*ef.electricity+.11*ef.sodium_bicarbonate))
    check('Common scope omits bicarbonate in both cases',close(summary['indiana_common'],1.5*feed+.921*ef.electricity))
    check('Alabama counterfactual reconstruction',close(summary['alabama_common'],1.02*feed+8.799*ef.electricity))
    check('Fixed-FCR electricity contrast',close(summary['alabama_fixed_fcr']-summary['indiana_common'],(8.799-.921)*ef.electricity))
    check('Energy and FCR contrast adds to total difference',close(summary['electricity_effect_fixed_fcr']+summary['fcr_effect_fixed_electricity'],summary['alabama_common']-summary['indiana_common']))
    # Compare archive hashes and confirm the original inventories, outputs, and figures are intact.
    for name,digest in json.loads((run/'legacy_sha256.json').read_text()).items():
        check('Archive hash: '+name,hashlib.sha256((run/'legacy'/name).read_bytes()).hexdigest()==digest)
        if name.split('/')[0] in ['data','outputs','figures']:
            check('Original preserved: '+name,hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest)
    # Check numeric CSV values for missing or infinite results.
    for path in (run/'analysis').glob('*.csv'):
        df=pd.read_csv(path)
        nums=df.select_dtypes(include='number')
        check('Finite numeric CSV: '+path.name,not nums.isna().any().any() and not nums.isin([float('inf'),float('-inf')]).any().any())
    # Refresh the validation CSV after every check has passed.
    pd.DataFrame(checks).to_csv(run/'validation.csv',index=False)
    print(f'{len(checks)} checks passed; feed={feed:.9f}; ingredients={ingredients:.9f}')
if __name__=='__main__':main()
