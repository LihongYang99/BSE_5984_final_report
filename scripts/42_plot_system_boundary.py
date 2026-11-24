"""Draw the intended cradle-to-farm-gate boundary and current inventory coverage.

Figure contract: distinguish modeled supply burdens from unresolved farm flows.
Python schematic, 183 by 155 mm, Calibri text, editable PDF/SVG and 600-dpi PNG.
Arrows show process connections, not measured or mass-balanced flow quantities.
"""
from pathlib import Path
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report/report_figures'
sys.path.insert(0, str(ROOT / 'scripts/report_figures'))
from figure_fonts import use_calibri


def main():
    use_calibri()
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(183 / 25.4, 155 / 25.4))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')
    teal, blue, amber, grey = '#397A86', '#657FAD', '#A9773E', '#87939E'
    styles = {
        'included': (teal, '#EDF4F5', '-'),
        'optional': (blue, '#EFF2F8', '-.'),
        'unresolved': (amber, '#FBF6EF', '--'),
        'outside': (grey, '#F3F4F5', '-'),
    }
    boxes = []

    def node(x, y, width, height, title, body, status='included', body_size=8.8):
        color, fill, line = styles[status]
        patch = Rectangle((x, y), width, height, linewidth=.85,
                          edgecolor=color, facecolor=fill, linestyle=line, zorder=2)
        ax.add_patch(patch)
        title_text = ax.text(x + .012, y + height - .022, title, fontsize=9.4,
                             weight='bold', color='#242B33', va='top', linespacing=1.15)
        body_y = y + height - .058 - .025 * title.count('\n')
        body_text = ax.text(x + .012, body_y, body, fontsize=body_size,
                            color='#38434C', va='top', linespacing=1.25)
        boxes.append((patch, [title_text, body_text]))

    def arrow(points, color=teal, dashed=False):
        # Explicit bends keep input arrows in the gaps between process boxes.
        if len(points) > 2:
            ax.plot(*zip(*points[:-1]), color=color, lw=.85,
                    linestyle='--' if dashed else '-', zorder=1)
        ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle='-|>',
                                    mutation_scale=7, linewidth=.85, color=color,
                                    linestyle='--' if dashed else '-', zorder=1))

    # The enclosing line marks intended scope, including processes still unresolved.
    ax.add_patch(Rectangle((.018, .280), .785, .650, facecolor='none',
                           edgecolor='#75808B', linewidth=.8, linestyle=(0, (2, 3))))
    ax.text(.035, .962, 'Intended cradle-to-farm-gate boundary', fontsize=11,
            weight='bold', color='#242B33', va='top')
    ax.text(.035, .909, 'Cradle', fontsize=9.4, weight='bold', color=teal)
    ax.text(.150, .909, 'Raw materials and upstream supply', fontsize=8.8, color='#59636D')
    ax.text(.837, .909, 'Farm gate', fontsize=9.4, weight='bold', color=teal)

    # Common feed supply proceeds through ingredients, milling, and road delivery.
    node(.035, .720, .200, .150, 'Ingredient production',
         'Fishery, crop and\nby-product supply\nIngredient proxies')
    node(.270, .720, .190, .150, 'Feed manufacturing',
         'Common Feed C\nSteam and electricity\nMill water proxy')
    node(.495, .720, .110, .150, 'Delivery', 'Road\nfreight')
    arrow([(.235, .795), (.270, .795)])
    arrow([(.460, .795), (.495, .795)])
    arrow([(.605, .795), (.635, .795)])

    # Two farm inventories share Feed C, with case-specific supplies shown below.
    node(.635, .480, .160, .390, 'Shrimp farming',
         'Indiana biofloc\nor Alabama pond\n\nGrow-out\nand harvest')
    node(.035, .490, .230, .170, 'Farm input supply',
         'Electricity\nBicarbonate in Indiana\nFertilizers in Alabama')
    node(.320, .490, .285, .170, 'Farm water',
         'Optional Indiana treatment proxy\nOther water burdens unresolved', 'optional')
    arrow([(.265, .575), (.290, .575), (.290, .687), (.620, .687), (.635, .687)])
    arrow([(.605, .575), (.635, .575)], blue)

    # Keep unquantified hatchery production distinct from included larval freight.
    node(.035, .315, .230, .120, 'Hatchery production', 'Unresolved', 'unresolved')
    node(.320, .315, .285, .120, 'Larval transport', 'Airfreight included')
    node(.635, .315, .160, .120, 'Infrastructure\nand land', 'Unresolved', 'unresolved')
    arrow([(.265, .375), (.320, .375)], amber, dashed=True)
    arrow([(.605, .375), (.620, .375), (.620, .505), (.635, .505)])
    arrow([(.715, .435), (.715, .480)], amber, dashed=True)

    # The reference product leaves at the farm gate; downstream stages stay outside.
    node(.837, .695, .150, .175, 'Product output',
         '1 kg live-weight\nshrimp\nat the farm gate')
    arrow([(.795, .770), (.837, .770)])
    node(.837, .315, .150, .285, 'Outside scope',
         'Processing\nPackaging\nDistribution\nRetail and use', 'outside')
    arrow([(.912, .695), (.912, .600)], grey)

    # Environmental outputs are separated by coverage, not assigned zero burdens.
    node(.035, .105, .350, .120, 'Upstream GHG emissions',
         'Included in background GWP factors')
    node(.420, .105, .375, .120, 'Direct farm outputs',
         'CH₄, N₂O, effluent and sludge\nImpacts unresolved', 'unresolved')
    arrow([(.210, .280), (.210, .225)])
    arrow([(.608, .280), (.608, .225)], amber, dashed=True)

    # Redundant line styles and labels keep scope readable without relying on color.
    for x, label, status in [(.035, 'Included', 'included'), (.270, 'Optional', 'optional'),
                              (.505, 'Unresolved', 'unresolved'), (.750, 'Outside scope', 'outside')]:
        edge, fill, line = styles[status]
        ax.add_patch(Rectangle((x, .039), .025, .022, edgecolor=edge,
                               facecolor=fill, linestyle=line, linewidth=.85))
        ax.text(x + .035, .050, label, fontsize=8.5, va='center', color='#38434C')

    # Check the requested font, punctuation, and label bounds before exporting.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for label in ax.texts:
        assert not any(c in label.get_text() for c in ';:；：|｜¦'), label.get_text()
        assert label.get_fontfamily() == ['Calibri'], label.get_text()
        extent = label.get_window_extent(renderer)
        assert fig.bbox.contains(extent.x0, extent.y0), label.get_text()
        assert fig.bbox.contains(extent.x1, extent.y1), label.get_text()
    for patch, labels in boxes:
        bounds = patch.get_window_extent(renderer)
        for label in labels:
            extent = label.get_window_extent(renderer)
            assert bounds.contains(extent.x0, extent.y0), label.get_text()
            assert bounds.contains(extent.x1, extent.y1), label.get_text()
    for extension in ('png', 'pdf', 'svg'):
        fig.savefig(OUT / f'cradle_to_farm_gate.{extension}', dpi=600, facecolor='white')
    plt.close(fig)
    caption = (
        'Intended cradle-to-farm-gate boundary and inventory coverage.\n\n'
        'The reference product is 1 kg live-weight shrimp at the farm gate. '
        'Upstream factors include supply-chain GHG emissions. Hatchery production, '
        'infrastructure, land-related burdens, direct farm gases, and effluent/sludge '
        'impacts remain unresolved. Only the optional Indiana water-treatment proxy '
        'is characterized for farm water. The diagram describes the expanded inventory. '
        'The separate controlled comparison includes feed supply and farm electricity only. '
        'Arrows show connections and are not scaled to quantities.\n\n'
        'Farm inputs follow Al Eissa et al. (2022) and Appendix A. '
        'The coverage treatment is documented in Appendix B.\n'
    )
    (OUT / 'cradle_to_farm_gate_caption.txt').write_text(caption)
    (OUT / 'figure_contract.json').write_text(json.dumps({
        'claim': 'The intended farm-gate scope is broader than the currently quantified inventory',
        'archetype': 'schematic-led composite', 'backend': 'Python Matplotlib',
        'size_mm': [183, 155], 'font': 'Calibri', 'raster_dpi': 600,
        'scope': 'Expanded covered inventory, with unresolved processes marked separately',
        'sources': ['results/run_2026-11-21/source_inventory_verified.csv',
                    'results/completeness_2026-11-23/EVIDENCE_REVIEW.md'],
        'new_calculations': False, 'flow_widths_quantitative': False,
        'automated_checks': ['Calibri', 'punctuation', 'canvas bounds', 'text fits boxes'],
    }, indent=2) + '\n')
    print(f'Saved boundary figure to {OUT}')


if __name__ == '__main__':
    main()
