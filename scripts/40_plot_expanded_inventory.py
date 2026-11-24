"""Update the covered-inventory figures; unknown farm burdens are not plotted as zero.

Figure contract: show the added known inputs and conditional sensitivities.
Python/Matplotlib; editable PDF/SVG and 600-dpi PNG; deterministic scenarios.
"""
from pathlib import Path
import importlib.util
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/completeness_2026-11-23'
FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('model',ROOT/'scripts/31_calculate_indiana_farming_gwp.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ef=pd.read_csv(ROOT/'results/run_2026-11-21/background_factors.csv').set_index('label').ef.to_dict()
results=pd.read_csv(OUT/'expanded_results.csv').set_index('case')
offset=float(results.loc['Indiana','added_gwp']);base=float(results.loc['Indiana','updated_covered_subtotal'])
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
def save(name):
    for ext in ['png','pdf','svg']:plt.savefig(FIG/f'{name}.{ext}',dpi=600,bbox_inches='tight')
    plt.close()
hot=pd.read_csv(OUT/'expanded_hotspots.csv');h=hot[(hot['case']=='Indiana') & (hot.gwp>0)].sort_values('gwp')
assert np.isclose(h.gwp.sum(),base) and np.isclose(h.share_pct.sum(),100)
fig,ax=plt.subplots(figsize=(7.2,4.3));fig.subplots_adjust(left=.29,bottom=.16,right=.98,top=.91)
colors=['#397A86' if x.startswith('Feed') else '#BE884C' if x=='Farm electricity' else '#85739B' if x=='Larval airfreight' else '#87939E' for x in h.component]
bars=ax.barh(h.component,h.gwp,color=colors,height=.62)
ax.bar_label(bars,labels=[f'{v:.3f} ({p:.1f}%)' for v,p in zip(h.gwp,h.share_pct)],padding=4,fontsize=8)
ax.set_xlim(0,1.9);ax.set_xlabel('GWP (kg CO₂-eq/kg live shrimp)');ax.set_title('Indiana: expanded covered inventory',loc='left',weight='bold')
ax.xaxis.grid(True,color='#E7EAED');ax.set_axisbelow(True);save('expanded_hotspots')

rows=[]
for name,key,baseline in [('Farm electricity','electricity',.921),('Farm grid','grid',ef['electricity']),('FCR','fcr',1.5)]:
    for multiplier in np.linspace(.75,1.25,21):
        value=sum(m.components(ef,**{key:baseline*multiplier}).values())+offset
        rows.append(dict(parameter=name,multiplier=multiplier,gwp=value,change_pct=100*(value/base-1)))
sens=pd.DataFrame(rows);sens.to_csv(OUT/'sensitivity_oat.csv',index=False)
grid=pd.DataFrame([dict(grid=g,farm_only=sum(m.components(ef,grid=g).values())+offset,farm_and_mill=sum(m.components(ef,grid=g,mill_grid=g).values())+offset) for g in np.linspace(.05,.8,76)])
grid.to_csv(OUT/'grid_sensitivity.csv',index=False)
fig,axs=plt.subplots(1,2,figsize=(8.2,4));fig.subplots_adjust(wspace=.35,bottom=.18,top=.85)
for name,color in [('Farm electricity','#397A86'),('FCR','#BE884C')]:
    t=sens[sens.parameter==name];axs[0].plot((t.multiplier-1)*100,t.change_pct,color=color,label='Farm electricity / grid' if name.startswith('Farm') else name)
axs[0].set(xlabel='Change in input (%)',ylabel='Change in covered GWP (%)',title='a  One input at a time');axs[0].legend(frameon=False,fontsize=8)
axs[1].plot(grid.grid,grid.farm_only,color='#397A86',label='Farm only');axs[1].plot(grid.grid,grid.farm_and_mill,color='#BE884C',ls='--',label='Farm + mill')
axs[1].scatter([ef['electricity']],[base],s=20,color='black',zorder=4)
axs[1].set(xlabel='Grid factor (kg CO₂-eq/kWh)',ylabel='GWP (kg CO₂-eq/kg shrimp)',title='b  Grid scenarios');axs[1].legend(frameon=False,fontsize=8)
save('expanded_sensitivity')
surface=pd.DataFrame([dict(grid=g,fcr=f,gwp=sum(m.components(ef,grid=g,fcr=f).values())+offset) for f in np.linspace(1,2,51) for g in grid.grid])
surface.to_csv(OUT/'grid_fcr_surface.csv',index=False)
fig,ax=plt.subplots(figsize=(6.5,4));z=surface.gwp.values.reshape(51,76)
im=ax.contourf(grid.grid,np.linspace(1,2,51),z,levels=14,cmap='cividis');fig.colorbar(im,ax=ax,label='Covered GWP (kg CO₂-eq/kg shrimp)');ax.scatter([ef['electricity']],[1.5],color='white',edgecolor='black');ax.set(xlabel='Farm grid factor (kg CO₂-eq/kWh)',ylabel='FCR (kg feed/kg shrimp)');save('expanded_grid_fcr')

fig,ax=plt.subplots(figsize=(6.7,3.2));x=np.arange(2)
ax.bar(x,results.previous_covered_subtotal,color='#397A86',label='Previously covered inputs')
ax.bar(x,results.added_gwp,bottom=results.previous_covered_subtotal,color='#85739B',label='Added airfreight and fertilizer supply')
for i,v in enumerate(results.updated_covered_subtotal):ax.text(i,v+.07,f'{v:.3f}',ha='center')
ax.set_xticks(x,['Indiana','Alabama counterfactual']);ax.set_ylim(0,7);ax.set_ylabel('Covered GWP (kg CO₂-eq/kg shrimp)');ax.legend(frameon=False,fontsize=8);save('coverage_correction')

summary=dict(indiana=base,alabama=float(results.loc['Alabama','updated_covered_subtotal']),indiana_addition=offset,
    fcr_low=float(sens[sens.parameter=='FCR'].iloc[0].gwp),fcr_high=float(sens[sens.parameter=='FCR'].iloc[-1].gwp),
    fcr_pct=float(sens[sens.parameter=='FCR'].iloc[-1].change_pct),electricity_pct=float(sens[sens.parameter=='Farm electricity'].iloc[-1].change_pct),
    farm_grid_low=float(grid.farm_only.min()),farm_grid_high=float(grid.farm_only.max()),mill_grid_low=float(grid.farm_and_mill.min()),mill_grid_high=float(grid.farm_and_mill.max()),
    feed_pct=float(h[h.component.str.startswith('Feed')].share_pct.sum()),electricity_pct_share=float(h[h.component=='Farm electricity'].share_pct.iloc[0]),
    bicarbonate_pct=float(h[h.component=='Sodium bicarbonate'].share_pct.iloc[0]),air_pct=float(h[h.component=='Larval airfreight'].share_pct.iloc[0]),
    unresolved_difference_to_reverse_ranking=float(results.loc['Alabama','updated_covered_subtotal']-base),
    five_percent_reference=base*.05,optional_water=base+75*ef['tap_water'])
(OUT/'expanded_summary.json').write_text(json.dumps(summary,indent=2))
assert all(np.isclose(t.iloc[10].gwp,base) for _,t in sens.groupby('parameter'))
assert np.all(np.diff(z,axis=0)>0) and np.all(np.diff(z,axis=1)>0)
print(json.dumps(summary,indent=2))
