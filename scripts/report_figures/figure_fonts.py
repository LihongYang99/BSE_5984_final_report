"""Use installed Calibri fonts for every report figure without silent substitution."""
import os
from pathlib import Path
from matplotlib import font_manager, rcParams


def use_calibri():
    # Word bundles these fonts outside the directories Matplotlib normally scans.
    word_fonts = Path('/Applications/Microsoft Word.app/Contents/Resources/DFonts')
    if word_fonts.is_dir():
        for path in word_fonts.iterdir():
            if path.name.lower() in {'calibri.ttf', 'calibrib.ttf', 'calibrii.ttf', 'calibriz.ttf'}:
                font_manager.fontManager.addfont(path)
    for weight in ('normal', 'bold'):
        font_manager.findfont(
            font_manager.FontProperties(family='Calibri', weight=weight),
            fallback_to_default=False,
        )
    rcParams.update({'font.family': 'Calibri', 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    # Fixed SVG ids and PDF/SVG dates make reruns byte-identical, so git shows only real changes.
    rcParams['svg.hashsalt'] = 'shrimp-lca-report'
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795651200')
