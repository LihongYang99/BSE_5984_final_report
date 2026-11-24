"""Draw the four LCA phases and their application to the shrimp screening study.
Run offline; export a report-ready PNG, PDF, SVG, and figure caption.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figure_fonts import use_calibri

use_calibri()
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "report/report_figures"


def main():
    # Contract: a methods schematic, 183 × 140 mm; no statistical claims or synthetic data.
    # Use vector text in the PDF/SVG and a high-resolution raster preview.
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Calibri"],
                         "pdf.fonttype": 42, "svg.fonttype": "none"})
    fig, ax = plt.subplots(figsize=(183 / 25.4, 140 / 25.4))
    fig.subplots_adjust(left=0.03, right=0.97, bottom=0.03, top=0.97)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    navy, teal, muted = "#242B33", "#397A86", "#59636D"

    # Give each phase a short definition followed by project-specific content.
    ax.text(0.02, 0.977, "Life cycle assessment workflow", fontsize=8.5,
            weight="bold", color=navy, va="top")
    ax.text(0.02, 0.930, "Scenario-based GWP screening of U.S. shrimp aquaculture",
            fontsize=8, color=muted, va="top")
    phases = [
        (0.665, "01", "Goal and scope definition",
         "Functional unit of 1 kg live-weight shrimp\n"
         "Intended cradle-to-farm-gate boundary\n"
         "Indiana main case and Alabama counterfactual"),
        (0.395, "02", "Life cycle inventory (LCI)",
         "Literature inputs of feed, farm electricity and bicarbonate\n"
         "Background from ecoinvent 3.11 Cut-off\n"
         "Explicit feed proxies, processing and delivery"),
        (0.125, "03", "Life cycle impact assessment (LCIA)",
         "openLCA + Python with explicit unit validation\n"
         "IPCC 2021 GWP100, excluding biogenic CO₂\n"
         "Output in kg CO₂-eq per kg live shrimp"),
    ]
    panel_left, panel_width, panel_height = 0.02, 0.60, 0.215
    for y, number, title, body in phases:
        ax.add_patch(Rectangle((panel_left, y), panel_width, panel_height,
                     linewidth=0.65, edgecolor="#C9D2D8", facecolor="#F7F9FA"))
        ax.plot([panel_left, panel_left], [y, y + panel_height],
                color=teal, linewidth=2, solid_capstyle="butt")
        ax.text(0.04, y + 0.176, number, fontsize=9, weight="bold", color=teal)
        ax.text(0.09, y + 0.176, title, fontsize=9, weight="bold", color=navy)
        ax.text(0.04, y + 0.132, body, fontsize=8, color="#263944",
                va="top", linespacing=1.55)

    # Interpretation checks each phase; two-way arrows show iterative refinement.
    ax.add_patch(Rectangle((0.71, 0.125), 0.28, 0.755,
                 linewidth=0.65, edgecolor="#9DB8BE", facecolor="#EDF3F5"))
    ax.text(0.74, 0.842, "04", fontsize=9, weight="bold", color=teal)
    ax.text(0.74, 0.797, "Interpretation", fontsize=10, weight="bold", color=navy)
    sections = [
        (0.715, "Identify hotspots", "Feed and farm-stage\nGWP contributions"),
        (0.555, "Test scenarios", "Electricity, grid and FCR\nAlabama counterfactual\nFixed-FCR comparison"),
        (0.350, "Evaluate findings", "Consistency checks\nProxy and boundary limits\nConditional conclusions"),
    ]
    for y, title, body in sections:
        ax.text(0.74, y, title, fontsize=8.5, weight="bold", color=teal, va="top")
        ax.text(0.74, y - 0.044, body, fontsize=8, color="#263944",
                va="top", linespacing=1.5)
    for y, _, _, _ in phases:
        ax.add_patch(FancyArrowPatch((0.63, y + panel_height / 2),
                     (0.70, y + panel_height / 2), arrowstyle="<->",
                     mutation_scale=8, linewidth=0.8, color=teal))
    for upper_y, lower_y in [(0.665, 0.395), (0.395, 0.125)]:
        ax.add_patch(FancyArrowPatch((0.325, upper_y - 0.004),
                     (0.325, lower_y + panel_height + 0.004), arrowstyle="<->",
                     mutation_scale=8, linewidth=0.8, color=navy))

    # State the implementation limit separately from the general LCA framework.
    ax.text(0.02, 0.064, "Partial GWP screening with explicit proxies and no new farm measurements.",
            fontsize=7.5, color=muted)
    ax.text(0.02, 0.027, "Four-phase framework from ISO 14040 (2006). Arrows indicate iteration and feedback.",
            fontsize=7, color=muted)

    # Check text bounds before export; final appearance is also inspected visually.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for label in ax.texts:
        extent = label.get_window_extent(renderer)
        assert extent.x0 >= 0 and extent.y0 >= 0
        assert extent.x1 <= fig.bbox.x1 and extent.y1 <= fig.bbox.y1, label.get_text()
    for panel in (patch for patch in ax.patches if isinstance(patch, Rectangle)):
        box = panel.get_window_extent(renderer)
        for label in ax.texts:
            anchor = ax.transData.transform(label.get_position())
            if box.contains(*anchor):
                extent = label.get_window_extent(renderer)
                assert box.contains(extent.x0, extent.y0), label.get_text()
                assert box.contains(extent.x1, extent.y1), label.get_text()
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"lca_workflow_nature.{suffix}", dpi=600, facecolor="white")
    plt.close(fig)
    caption = (
        "Figure. LCA framework and its application to the U.S. shrimp aquaculture screening study.\n\n"
        "The four phases are goal and scope definition, life cycle inventory analysis, life cycle "
        "impact assessment, and interpretation. Bidirectional arrows represent iteration and feedback. "
        "The project implements a partial GWP screening inventory with explicit proxies. Alabama uses "
        "the common Feed C supply chain as a counterfactual. The fixed-FCR comparison separates the "
        "electricity-demand contrast from feed efficiency. This diagram does not assert ISO conformity "
        "or complete life-cycle inventory coverage.\n\n"
        "Framework source. International Organization for Standardization. (2006). "
        "Environmental management—Life cycle assessment—Principles and framework (ISO 14040, 2006). "
        "https://www.iso.org/standard/37456.html\n"
        "Project content in results/run_2026-11-21/METHOD_NOTES.md.\n"
    )
    (OUT / "lca_workflow_nature_caption.txt").write_text(caption, encoding="utf-8")
    print(f"Saved LCA workflow figure and caption to {OUT}")


if __name__ == "__main__":
    main()
