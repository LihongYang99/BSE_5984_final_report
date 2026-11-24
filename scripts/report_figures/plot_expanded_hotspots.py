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
from figure_fonts import use_calibri

use_calibri()

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/completeness_2026-11-23'
FIG=ROOT/'report/report_figures';FIG.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('model',ROOT/'scripts/31_calculate_indiana_farming_gwp.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ef=pd.read_csv(ROOT/'results/run_2026-11-21/background_factors.csv').set_index('label').ef.to_dict()
results=pd.read_csv(OUT/'expanded_results.csv').set_index('case')
offset=float(results.loc['Indiana','added_gwp']);base=float(results.loc['Indiana','updated_covered_subtotal'])
plt.rcParams.update({'font.family':'Calibri','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
def save(name):
    for ext in ['png','pdf','svg']:plt.savefig(FIG/f'{name}.{ext}',dpi=600,bbox_inches='tight')
    plt.close()
hot=pd.read_csv(OUT/'expanded_hotspots.csv');h=hot[(hot['case']=='Indiana') & (hot.gwp>0)].sort_values('gwp')
assert np.isclose(h.gwp.sum(),base) and np.isclose(h.share_pct.sum(),100)
fig,ax=plt.subplots(figsize=(7.2,4.3));fig.subplots_adjust(left=.29,bottom=.16,right=.98,top=.91)
colors=['#397A86' if x.startswith('Feed') else '#BE884C' if x=='Farm electricity' else '#85739B' if x=='Larval airfreight' else '#87939E' for x in h.component]
bars=ax.barh(h.component,h.gwp,color=colors,height=.62)
ax.bar_label(bars,labels=[f'{v:.3f} ({p:.1f}%)' for v,p in zip(h.gwp,h.share_pct)],padding=4,fontsize=8)
ax.set_xlim(0,1.9);ax.set_xlabel('GWP (kg CO₂-eq/kg live shrimp)');ax.set_title('Indiana expanded covered inventory',loc='left',weight='bold')
ax.xaxis.grid(True,color='#E7EAED');ax.set_axisbelow(True);save('expanded_hotspots')
