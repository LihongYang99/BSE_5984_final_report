"""Redraw the reviewed sensitivity panels in Calibri using saved scenario results.

Keep the evidence and layout unchanged. Panel a compares input sensitivities, and
panel b shows the two grid scenarios. Export editable PDF/SVG and a 600-dpi PNG.
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from figure_fonts import use_calibri

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'results/completeness_2026-11-23'
OUT = ROOT / 'report/report_figures'
OUT.mkdir(parents=True, exist_ok=True)
use_calibri()
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})

# Read the existing calculated values so this font edit does not rerun the model.
sens = pd.read_csv(SOURCE / 'sensitivity_oat.csv')
grid = pd.read_csv(SOURCE / 'grid_sensitivity.csv')
factors = pd.read_csv(ROOT / 'results/run_2026-11-21/background_factors.csv').set_index('label').ef
results = pd.read_csv(SOURCE / 'expanded_results.csv').set_index('case')
base = float(results.loc['Indiana', 'updated_covered_subtotal'])

fig, axs = plt.subplots(1, 2, figsize=(8.2, 4))
fig.subplots_adjust(wspace=.35, bottom=.18, top=.85)
for name, color in [('Farm electricity', '#397A86'), ('FCR', '#BE884C')]:
    selected = sens[sens.parameter == name]
    axs[0].plot((selected.multiplier - 1) * 100, selected.change_pct, color=color,
                label='Farm electricity / grid' if name.startswith('Farm') else name)
axs[0].set(xlabel='Change in input (%)', ylabel='Change in covered GWP (%)', title='a  One input at a time')
axs[0].legend(frameon=False, fontsize=8)
axs[1].plot(grid.grid, grid.farm_only, color='#397A86', label='Farm only')
axs[1].plot(grid.grid, grid.farm_and_mill, color='#BE884C', ls='--', label='Farm + mill')
axs[1].scatter([factors['electricity']], [base], s=20, color='black', zorder=4)
axs[1].set(xlabel='Grid factor (kg CO₂-eq/kWh)', ylabel='GWP (kg CO₂-eq/kg shrimp)', title='b  Grid scenarios')
axs[1].legend(frameon=False, fontsize=8)
for ext in ('png', 'pdf', 'svg'):
    fig.savefig(OUT / f'expanded_sensitivity.{ext}', dpi=600, bbox_inches='tight')
plt.close(fig)
