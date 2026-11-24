"""Offline deterministic sensitivity and controlled Alabama scenario, not field predictions.
All new outputs go in the selected reviewed run. Existing figures remain intact.
"""
from pathlib import Path
import argparse, importlib.util, json, math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

spec=importlib.util.spec_from_file_location('farming',Path(__file__).with_name('31_calculate_indiana_farming_gwp.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True)
    p.add_argument('--controlled-alabama',action='store_true',help='Same Feed C; literature FCR/electricity; shared delivery distance; incomplete farming subtotal')
    a=p.parse_args();out=a.run/'analysis';fig=a.run/'figures';fig.mkdir(exist_ok=False)
    ef=pd.read_csv(a.run/'background_factors.csv').set_index('label').ef.to_dict()
    base=sum(m.components(ef).values())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    def save(name):
        plt.tight_layout();plt.savefig(fig/(name+'.png'),dpi=300,bbox_inches='tight');plt.savefig(fig/(name+'.pdf'),bbox_inches='tight');plt.close()
    hot=pd.read_csv(out/'indiana_hotspots.csv');hot=hot[hot.gwp>0].sort_values('gwp')
    _,ax=plt.subplots(figsize=(8,4.2));bars=ax.barh(hot.component,hot.gwp,color='#346888')
    ax.bar_label(bars,labels=[f'{v:.3f} ({s:.1f}%)' for v,s in zip(hot.gwp,hot.share_pct)],padding=4,fontsize=9)
    ax.set_xlim(0,hot.gwp.max()*1.4);ax.set_xlabel('kg CO₂-eq per kg live-weight shrimp');ax.set_title('Indiana: corrected screening GWP contributions')
    save('fig08_indiana_hotspots')
    rows=[]
    for parameter,baseline,key in [('Farm electricity (kWh/kg)',.921,'electricity'),('Farm grid (kg CO₂-eq/kWh)',ef['electricity'],'grid'),('FCR (kg feed/kg shrimp)',1.5,'fcr')]:
        for multiplier in np.linspace(.75,1.25,21):
            value=baseline*multiplier;gwp=sum(m.components(ef,**{key:value}).values())
            rows.append(dict(parameter=parameter,multiplier=multiplier,value=value,gwp=gwp,change_pct=100*(gwp/base-1),type='Hypothetical one-at-a-time; others fixed'))
    sens=pd.DataFrame(rows);sens.to_csv(out/'sensitivity_oat.csv',index=False)
    figobj,axes=plt.subplots(1,2,figsize=(9.4,3.7))
    for param,g in sens.groupby('parameter',sort=False):axes[0].plot((g.multiplier-1)*100,g.change_pct,label=param.split(' (')[0],linewidth=2)
    axes[0].set(xlabel='Change in input (%)',ylabel='Change in Indiana GWP (%)',title='A. One-at-a-time sensitivity');axes[0].axhline(0,color='gray',lw=.5);axes[0].legend(frameon=False,fontsize=8)
    grids=np.linspace(.05,.8,76);gridrows=[]
    for x in grids:
        gridrows.append(dict(grid=x,farm_only=sum(m.components(ef,grid=x).values()),farm_and_mill=sum(m.components(ef,grid=x,mill_grid=x).values()),type='Hypothetical grid; ingredient supply chain fixed'))
    gd=pd.DataFrame(gridrows);gd.to_csv(out/'grid_sensitivity.csv',index=False)
    axes[1].plot(gd.grid,gd.farm_only,label='Farm only',color='#346888',lw=2)
    axes[1].plot(gd.grid,gd.farm_and_mill,label='Farm + feed mill',color='#b96a34',ls='--',lw=2)
    axes[1].scatter([ef['electricity']],[base],color='black',s=20,zorder=5)
    axes[1].set(xlabel='Grid factor (kg CO₂-eq/kWh)',ylabel='kg CO₂-eq/kg live shrimp',title='B. Grid scenarios');axes[1].legend(frameon=False,fontsize=8)
    save('fig09_sensitivity')
    fcrs=np.linspace(1,2,51);xx,yy=np.meshgrid(grids,fcrs)
    zz=np.array([[sum(m.components(ef,grid=g,fcr=f).values()) for g in grids] for f in fcrs])
    pd.DataFrame(dict(grid=xx.ravel(),fcr=yy.ravel(),gwp=zz.ravel())).to_csv(out/'grid_fcr_surface.csv',index=False)
    _,ax=plt.subplots(figsize=(7,4.4));im=ax.contourf(xx,yy,zz,levels=15,cmap='viridis');cs=ax.contour(xx,yy,zz,levels=6,colors='white',linewidths=.6);ax.clabel(cs,fmt='%.1f',fontsize=8)
    ax.scatter([ef['electricity']],[1.5],color='tomato',edgecolor='white',label='Corrected baseline');ax.legend(frameon=True,fontsize=8)
    ax.set(xlabel='Farm grid factor (kg CO₂-eq/kWh)',ylabel='FCR (kg feed/kg live shrimp)',title='Indiana: joint grid and FCR scenarios')
    plt.colorbar(im,ax=ax,label='kg CO₂-eq/kg live shrimp');save('fig10_grid_fcr_surface')
    checks=[dict(check='Hotspot sum and shares',status='PASS' if math.isclose(hot.gwp.sum(),base) and math.isclose(hot.share_pct.sum(),100) else 'FAIL')]
    for _,g in sens.groupby('parameter'):
        assert np.all(np.diff(g.gwp)>0)
        assert math.isclose(float(g.iloc[10].gwp),base)
    assert np.all(np.diff(zz,axis=0)>0) and np.all(np.diff(zz,axis=1)>0)
    checks.append(dict(check='Sensitivity baseline identities and monotonicity',status='PASS'))
    summary={'indiana':base,'grid_ef':ef['electricity'],'oat_fcr_low':float(sens[sens.parameter.str.startswith('FCR')].iloc[0].gwp),'oat_fcr_high':float(sens[sens.parameter.str.startswith('FCR')].iloc[-1].gwp)}
    if a.controlled_alabama:
        # Common inventory scope: feed supply/delivery and farming electricity only.
        cases={'Indiana (common scope)':m.components(ef,bicarbonate=0),
               'Alabama (counterfactual; literature FCR)':m.components(ef,fcr=1.020,electricity=8.799,bicarbonate=0),
               'Alabama (counterfactual; fixed FCR 1.5)':m.components(ef,fcr=1.5,electricity=8.799,bicarbonate=0)}
        cr=[]
        for case,values in cases.items():
            for k,v in values.items():
                cr.append(dict(case=case,component=k,gwp=v,scope='Feed production/delivery + farm electricity only; not complete farm GWP'))
        cd=pd.DataFrame(cr);cd.to_csv(out/'alabama_controlled_comparison.csv',index=False)
        totals=cd.groupby('case',sort=False).gwp.sum()
        summary.update(indiana_common=float(totals.iloc[0]),alabama_common=float(totals.iloc[1]),alabama_fixed_fcr=float(totals.iloc[2]))
        _,ax=plt.subplots(figsize=(8,4));labels=['Indiana\nFCR 1.50','Alabama counterfactual\nFCR 1.02','Alabama counterfactual\nFixed FCR 1.50'];bottom=np.zeros(3)
        for cat,color in [('Feed supply + delivery','#346888'),('Farm electricity','#ca853b')]:
            vals=[sum(v for k,v in d.items() if k.startswith('Feed')) if cat.startswith('Feed') else d['Farm electricity'] for d in cases.values()]
            ax.bar(labels,vals,bottom=bottom,label=cat,color=color,width=.55);bottom+=vals
        for i,v in enumerate(bottom):ax.text(i,v+.07,f'{v:.3f}',ha='center')
        ax.set_ylim(0,max(bottom)*1.3);ax.set_ylabel('kg CO₂-eq per kg live shrimp');ax.set_title('Controlled comparison: feed and electricity subtotal');ax.legend(frameon=False,fontsize=8)
        save('fig11_alabama_comparison')
        # Break-even assumes common grid for farms; feed mill grid stays at baseline.
        c0=sum(m.components(ef,bicarbonate=0,grid=0).values())
        a0=sum(m.components(ef,fcr=1.02,electricity=8.799,bicarbonate=0,grid=0).values())
        crossover=(c0-a0)/(8.799-.921);summary['common_scope_grid_crossover']=crossover
        assert crossover>0
        summary['alabama_longer_delivery_sensitivity']=sum(m.components(ef,fcr=1.02,electricity=8.799,distance_km=1677,bicarbonate=0).values())
        summary['electricity_effect_fixed_fcr']=float(totals.iloc[2]-totals.iloc[0])
        summary['fcr_effect_fixed_electricity']=float(totals.iloc[1]-totals.iloc[2])
        assert math.isclose(summary['electricity_effect_fixed_fcr'],(8.799-.921)*ef['electricity'])
        checks.append(dict(check='Fixed-FCR electricity effect isolated',status='PASS'))
        checks.append(dict(check='Common-scope crossover reconstructed',status='PASS' if math.isclose(c0+.921*crossover,a0+8.799*crossover) else 'FAIL'))
    assert all(x['status']=='PASS' for x in checks)
    pd.DataFrame(checks).to_csv(out/'analysis_validation.csv',index=False)
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
