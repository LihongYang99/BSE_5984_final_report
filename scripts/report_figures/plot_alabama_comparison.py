"""Clarify the common-feed scenario caption without changing numerical results."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from figure_fonts import use_calibri

use_calibri()
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'report/report_figures';OUT.mkdir(parents=True,exist_ok=True)
comp=pd.read_csv(ROOT/'results/run_2026-11-21/analysis/alabama_controlled_comparison.csv')
cases=list(comp.case.drop_duplicates())
plt.rcParams.update({'font.family':'Calibri','font.size':8,'axes.spines.top':False,
                     'axes.spines.right':False,'axes.linewidth':.6,'legend.frameon':False,
                     'pdf.fonttype':42,'svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(183/25.4,125/25.4))
fig.subplots_adjust(left=.13,right=.95,top=.81,bottom=.23)
fig.text(.055,.94,'Controlled comparison of feed and electricity',fontsize=11,weight='bold',va='top')
bottom=np.zeros(3)
for label,color,mask in [('Feed supply + delivery','#397A86',comp.component.str.startswith('Feed')),
                         ('Farm electricity','#BE884C',comp.component.eq('Farm electricity'))]:
    vals=comp[mask].groupby('case').gwp.sum().reindex(cases).to_numpy()
    ax.bar(np.arange(3),vals,bottom=bottom,label=label,color=color,width=.52)
    bottom+=vals
assert np.allclose(bottom,[2.3166074637239777,5.558358162604219,6.156037513637365])
for i,v in enumerate(bottom):ax.text(i,v+.12,f'{v:.3f}',ha='center',fontsize=8)
ax.set_xticks(np.arange(3),['Indiana\nFCR 1.50','Alabama counterfactual\nFCR 1.02','Alabama counterfactual\nFixed FCR 1.50'])
ax.set(ylabel='GWP (kg CO₂-eq/kg live shrimp)',ylim=(0,7.8))
ax.legend(loc='upper left',fontsize=7)
ax.set_axisbelow(True);ax.yaxis.grid(True,color='#E7EAED',lw=.5)
fig.text(.055,.055,'Common feed supply, delivery and grid assumptions. Feed + farm electricity only.\nAlabama literature FCR is a scenario input, not verified performance on the modeled feed.',fontsize=7,color='#59636D',va='bottom')
for ext in ('png','pdf','svg'):fig.savefig(OUT/f'alabama_comparison_clarified.{ext}',dpi=600,facecolor='white')
plt.close(fig)
