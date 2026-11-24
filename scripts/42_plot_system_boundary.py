"""Export the editable draw.io boundary diagram for Appendix C.

Edit report/report_figures/cradle_to_farm_gate.drawio in draw.io first.
This script exports that source without replacing manual diagram edits.
Requires draw.io Desktop and installed Calibri fonts on this Mac.
"""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report/report_figures'
SOURCE = OUT / 'cradle_to_farm_gate.drawio'
DRAWIO = Path('/Applications/draw.io.app/Contents/MacOS/draw.io')


def main():
    if not DRAWIO.is_file():
        raise FileNotFoundError('Install draw.io Desktop in /Applications first')

    # Check native editable objects, label fonts, and connector references.
    cells = ET.parse(SOURCE).findall('.//mxCell')
    ids = {cell.get('id') for cell in cells}
    labels = [cell for cell in cells if cell.get('value')]
    assert labels and not any('image=' in cell.get('style', '') for cell in cells)
    for cell in labels:
        assert 'fontFamily=Calibri;' in cell.get('style', '')
        assert not set(cell.get('value')) & set(';:；：|｜¦')
    for cell in cells:
        if cell.get('edge') == '1':
            assert cell.get('source') in ids and cell.get('target') in ids

    # A fresh renderer profile avoids font caches in an already-open draw.io window.
    with tempfile.TemporaryDirectory(prefix='shrimp-drawio-export-') as folder:
        work = Path(folder)
        for extension in ('pdf', 'svg', 'png'):
            target = work / f'{SOURCE.stem}.{extension}'
            options = ['--crop'] if extension == 'pdf' else (
                ['--width', '3840'] if extension == 'png' else ['--embed-svg-fonts', 'false'])
            subprocess.run([
                str(DRAWIO), f'--user-data-dir={work / "profile"}', '--export',
                '--disable-update', '--theme', 'light', '--format', extension,
                '--output', str(target), *options, str(SOURCE),
            ], check=True, timeout=90)
            assert target.is_file() and target.stat().st_size > 1000

        # Stop before publishing if draw.io silently substitutes another PDF font.
        pdf = work / f'{SOURCE.stem}.pdf'
        pages = PdfReader(pdf).pages
        assert len(pages) == 1
        fonts = [font.get_object() for font in pages[0]['/Resources']['/Font'].values()]
        assert fonts and all('Calibri' in font.get('/BaseFont', '') for font in fonts)
        for font in fonts:
            descriptor = font['/DescendantFonts'][0].get_object()['/FontDescriptor']
            assert '/FontFile2' in descriptor, 'Calibri must be embedded in the PDF'
        png = work / f'{SOURCE.stem}.png'
        with Image.open(png) as source_image:
            assert source_image.width == 3840
            source_image.save(png, dpi=(600, 600))
        for extension in ('pdf', 'svg', 'png'):
            shutil.copy2(work / f'{SOURCE.stem}.{extension}', OUT / f'{SOURCE.stem}.{extension}')

    # Record coverage without making new measurements or impact calculations.
    caption = (
        'Intended cradle-to-farm-gate boundary and inventory coverage.\n\n'
        'Blue boxes show inputs, green boxes show production processes, and purple '
        'boxes show outputs. Solid outlines indicate included coverage, dash-dot '
        'outlines indicate an optional scenario, and dashed outlines indicate burdens '
        'not yet quantified. These burdens are not assumed to be zero.\n\n'
        'The reference product is 1 kg live-weight shrimp at the farm gate. '
        'Upstream factors include supply-chain GHG emissions. Hatchery production, '
        'infrastructure, land-related burdens, direct farm gases, and effluent/sludge '
        'impacts are not yet quantified. Only the optional Indiana water-treatment '
        'proxy is characterized for farm water. The diagram describes the expanded '
        'inventory. The separate controlled comparison includes feed supply and farm '
        'electricity only. Arrows show connections and are not scaled to quantities.\n\n'
        'Farm inputs follow Al Eissa et al. (2022) and Appendix A. '
        'The coverage treatment is documented in Appendix B.\n'
    )
    (OUT / 'cradle_to_farm_gate_caption.txt').write_text(caption)
    (OUT / 'figure_contract.json').write_text(json.dumps({
        'claim': 'The intended farm-gate scope is broader than the currently quantified inventory',
        'backend': 'draw.io Desktop', 'editable_source': str(SOURCE.relative_to(ROOT)),
        'font': 'Calibri', 'png_width_px': 3840, 'raster_dpi_at_6_4_inches': 600,
        'color_encoding': {'blue': 'Inputs', 'green': 'Processes', 'purple': 'Outputs'},
        'coverage_encoding': {'solid': 'Included', 'dash-dot': 'Optional scenario',
                              'dashed': 'Not yet quantified'},
        'sources': ['results/run_2026-11-21/source_inventory_verified.csv',
                    'results/completeness_2026-11-23/EVIDENCE_REVIEW.md'],
        'new_calculations': False, 'flow_widths_quantitative': False,
        'automated_checks': ['Native objects', 'Calibri labels and PDF fonts',
                             'Punctuation', 'Connector references', 'PNG width'],
    }, indent=2) + '\n')
    print(f'Exported draw.io boundary figure to {OUT}')


if __name__ == '__main__':
    main()
