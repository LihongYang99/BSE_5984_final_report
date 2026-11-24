# Step 38: Build the six-page main report with literature synthesis, references, and data appendices.
"""Build the English course report from reviewed CSV/JSON results.
Requires python-docx in the project .venv (see requirements.txt).
Writes report/BSE5984_Final_Report.docx and the text export; render the PDF separately.
Versions are tracked in git, so the outputs are overwritten in place.
"""
from pathlib import Path
import argparse, csv, json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

TITLE='Scenario-Based Life Cycle Screening of U.S. Shrimp Aquaculture\nEnergy Demand, Feed Efficiency, and Environmental Trade-offs'
REPORT_DATE='November 24, 2026'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,default=Path(__file__).resolve().parents[1]/'results/run_2026-11-21');a=p.parse_args()
    run=a.run;root=Path(__file__).resolve().parents[1]
    dest=root/'report'
    figures=root/'report/report_figures'
    # Read calculated values from the run; this script performs no new LCIA.
    s=json.loads((run/'analysis/summary.json').read_text())
    with (run/'analysis/indiana_results.csv').open() as f:r=list(csv.DictReader(f))
    feed=float(r[1]['feed_gwp']);water=float(r[2]['shrimp_gwp'])
    expanded=root/'results/completeness_2026-11-23'
    ex=json.loads((expanded/'expanded_summary.json').read_text())
    # Set the page, font, spacing, and heading styles for the course report.
    doc=Document();sec=doc.sections[0]
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Inches(1)
    sec.header_distance=sec.footer_distance=Inches(.45)
    for sty in ['Normal','Title','Subtitle','Heading 1','Heading 2','Caption']:
        st=doc.styles[sty];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
        # Remove template theme overrides and the default decorative title border.
        for fonts in st.element.iter(qn('w:rFonts')):
            for attr in list(fonts.attrib):
                if 'theme' in attr.lower(): del fonts.attrib[attr]
        for border in list(st.element.iter(qn('w:pBdr'))): border.getparent().remove(border)
    normal=doc.styles['Normal'];normal.font.size=Pt(11);normal.paragraph_format.line_spacing=1.05
    normal.paragraph_format.space_after=Pt(5)
    for name in ['Heading 1','Heading 2']:
        doc.styles[name].font.size=Pt(11);doc.styles[name].font.bold=True
        doc.styles[name].paragraph_format.space_before=Pt(8);doc.styles[name].paragraph_format.space_after=Pt(5)
    # Add the running header and automatic page number.
    header=sec.header.paragraphs[0];header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    rr=header.add_run('SHRIMP AQUACULTURE SCENARIOS   ');rr.font.size=Pt(9)
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');header._p.append(fld)
    textlog=[]
    next_page=False
    # Use small helpers to keep paragraphs, headings, page breaks, and captions consistent.
    def para(text,style=None):
        nonlocal next_page
        q=doc.add_paragraph(text,style);q.paragraph_format.widow_control=True
        if next_page: q.paragraph_format.page_break_before=True;next_page=False
        textlog.append(text);return q
    def heading(text):para(text,'Heading 1')
    def page():
        nonlocal next_page
        next_page=True;textlog.append('\n---\n')
    def figure(number,title,name,note,width=6.4):
        q=para('');q.add_run(f'Figure {number}\n').bold=True;q.add_run(title).italic=True;q.paragraph_format.keep_with_next=True
        q.paragraph_format.space_after=Pt(2)
        for rr in q.runs: rr.font.size=Pt(10)
        q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER;picture=q.add_run().add_picture(str(figures/name),width=Inches(width));picture._inline.docPr.set('descr', title);q.paragraph_format.space_after=Pt(3);q.paragraph_format.keep_with_next=True
        q=para('Note. '+note);q.runs[0].font.size=Pt(9)
        textlog.append(f'[Figure {number} — {Path(name).name}]')
    # Page 1 introduces the result and maps the study onto the four LCA phases.
    q=para(TITLE, 'Title');q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.space_after=Pt(6)
    for x in q.runs:x.bold=True;x.font.size=Pt(13)
    q=para('Lihong Yang, BSE 5984 Sustainable Agroecosystems\n'+REPORT_DATE);q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    heading('Abstract')
    para(f"""This study examines feed and electricity demand in Indiana biofloc shrimp production and an Alabama pond counterfactual. Literature inventories and ecoinvent backgrounds were used to calculate 100-year global warming potential (GWP) per kilogram of live-weight shrimp. An inventory audit restored larval airfreight and Alabama fertilizer supply. Indiana's covered GWP increased to {ex['indiana']:.3f} kg CO₂-eq/kg, with feed contributing {ex['feed_pct']:.2f}%. Varying feed conversion ratio (FCR) by ±25% changed this subtotal by ±{ex['fcr_pct']:.2f}%, compared with ±{ex['electricity_pct']:.2f}% for farm electricity. The Alabama counterfactual reached {ex['alabama']:.3f}. Hatchery production and direct farm emissions remain unresolved. These are expanded inventory subtotals, not complete farm carbon footprints or evidence of a technological advantage.""")
    heading('1 Introduction')
    para('Feed formulation, electricity demand, and inventory coverage can all affect comparisons of shrimp production systems. Al Eissa et al. (2022) examined these factors across shrimp supply chains and supplied the foreground data used here. This study tests farm electricity demand, grid intensity, and FCR while holding feed supply constant. The functional unit is 1 kg live-weight shrimp at the farm gate. The intended boundary is cradle-to-farm-gate, but the available inventory supports only partial GWP screening. Figure 1 follows the LCA framework of the International Organization for Standardization (ISO, 2006).')
    figure(1,'LCA phases and their application to shrimp aquaculture','lca_workflow_nature.png','Arrows show feedback between LCA phases. Inventory coverage remains incomplete, and ISO conformity has not been established.',5.1)

    # Keep the title-page workflow together at the established readable scale.
    for q in doc.paragraphs: q.paragraph_format.line_spacing=1

    # Page 2 synthesizes prior evidence and defines the scope of the contribution.
    page();heading('1.1 Evidence from previous studies')
    para('Feed supply and electricity are established priorities in shrimp LCA. Cao et al. (2011) assessed Chinese intensive and semi-intensive production and identified both as major contributors to GWP. They also evaluated electricity-mix changes and lower FCR. Sun et al. (2023) compared Chinese recirculating aquaculture systems, biofloc technology, and higher-place ponds. Electricity was a major driver, and higher-place ponds had the highest GWP among their cases. Together, these studies show that the magnitude and ranking of impacts depend on operating inputs and background energy supply. Identifying feed and electricity hotspots or applying sensitivity analysis is therefore an established approach.')
    para('The study by Al Eissa et al. (2022) provides the closest precedent and the foreground inventory for this project. Their cradle-to-US-market assessment compared three production chains and eight feed formulations. Feed production was the main GWP contributor for the Indiana chain, while feed substitutions produced trade-offs across impact categories. Their comparison included differences in recipes, delivery distances, farming inputs, and post-harvest operations. It addressed the performance of those supply chains. The present farm-gate analysis asks how selected differences contribute when feed supply and the comparison boundary are held constant.')
    para('Wastewater studies show why climate results need a broader environmental context. Arbour et al. (2024) assessed microalgae treatment using the same Indiana farm background described by Al Eissa et al. (2022), so it is a related extension rather than independent farm evidence. The modeled treatment improved eutrophication outcomes without reducing GWP. Results also depended on electricity supply and the treatment of algal coproducts. These findings support assessing nutrient management alongside energy use, while keeping benefits outside this report’s GWP calculation explicit.')
    para('The studies differ in geography, system boundaries, feed backgrounds, and impact methods. Their absolute footprints cannot be compared directly with the covered subtotals reported here. This targeted narrative synthesis establishes the basis for the scenarios and their interpretation. It does not establish an exhaustive literature gap or priority claim.')
    heading('1.2 Study objective and contribution')
    para('The study asks how much of the modeled Indiana–Alabama difference remains when both cases share Feed C, delivery distance, and a national electricity factor, and how that difference responds to FCR and grid intensity. The contribution is a reproducible, case-specific decomposition of published inventories. A fixed-FCR contrast isolates the electricity-demand effect within the model. Retaining each case’s literature FCR in a separate contrast exposes the feed-efficiency offset. Farm-only and farm-plus-mill grid scenarios then distinguish changes at different supply-chain stages.')
    para('The analysis also separates quantified inputs from unresolved burdens and evaluates when those gaps could overturn the covered-inventory ranking. The electricity-unit correction is internal quality control, not a new LCA method or a criticism of the source studies. This is an analytical extension using secondary data. It provides neither new farm measurements nor causal evidence that one farming technology performs better.')

    # Page 3 presents the methods without compressing the results below them.
    page();heading('2 Materials and methods')
    para('2.1 Inventory and background data', 'Heading 2')
    para('Feed C is the estimated Indiana commercial-feed recipe reported by Al Eissa et al. (2022). The manufacturer did not disclose the full formulation. This is the only recipe modeled here, and both cases use it. Appendix A gives the farm inputs (Table A1), feed recipe (Table A2), and processing inventory (Table A3). Appendix C, Figure C1 maps the intended cradle-to-farm-gate boundary, inputs, product output, and unresolved flows.')
    q=para('Table 1');q.runs[0].bold=True;q.paragraph_format.keep_with_next=True
    q=para('Selected literature inputs per kilogram of live-weight shrimp');q.runs[0].italic=True;q.paragraph_format.keep_with_next=True
    table=doc.add_table(rows=1,cols=3);table.autofit=False
    widths=[3.7,1.4,1.4]
    for column,width in zip(table.columns,widths): column.width=Inches(width)
    rows=[('Input','Indiana','Alabama'),('Farm electricity (kWh)','0.921','8.799'),('FCR (kg feed/kg shrimp)','1.500','1.020')]
    for i,values in enumerate(rows):
        cells=table.rows[0].cells if i==0 else table.add_row().cells
        for j,(cell,txt) in enumerate(zip(cells,values)):
            cell.text=txt;cell.width=Inches(widths[j])
            pr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
            pr.append(borders)
            if i==0:
                shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E7E6E6');pr.append(shade)
            for q in cell.paragraphs:
                q.paragraph_format.space_before=Pt(2);q.paragraph_format.space_after=Pt(2)
                if j:q.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for z in q.runs:z.font.size=Pt(10);z.bold=i==0
    repeat=OxmlElement('w:tblHeader');table.rows[0]._tr.get_or_add_trPr().append(repeat)
    para('Note. Inputs are from Al Eissa et al. (2022, Tables 1 and 2). Both inventories are secondary literature data.').runs[0].font.size=Pt(9)
    para('The recipe contains 30% fishmeal, 5% poultry by-product meal, 20% soybean meal, 30% wheat flour, 5% rice bran, 3% fish oil, 3% soybean lecithin, and 4% supplements by mass (Al Eissa et al., 2022, Table 1).')
    para('Background datasets cover 83% of Feed C ingredient mass. The remaining 17% uses meat-and-bone meal for poultry meal, wheat bran for rice bran, refined soybean oil for lecithin, and Norwegian vitamin/mineral mix for supplements at 1.33 kg CO₂-eq/kg (Winther et al., 2020, p. 51). Feed processing and 1006 km delivery are included. The proxies are not fully harmonized. The meat-and-bone meal factor is especially low because of how its dataset treats a rendering by-product, whereas the source study used mass allocation (Al Eissa et al., 2022, p. 2009). Appendix A evaluates its effect.')
    para('2.2 Life cycle impact assessment', 'Heading 2')
    para('GWP was calculated with openLCA 2.7, Python 3.12, ecoinvent 3.11 Cut-off, and IPCC 2021 GWP100 excluding biogenic CO₂. Units and flow properties were specified (GreenDelta, n.d.). Covered GWP is G = F × C + E × g + B + L + Q. Here, F is FCR, C delivered feed GWP, E farm electricity, g the grid factor, B bicarbonate, L larval airfreight, and Q fertilizer supply. The original feed-and-electricity contrast is retained separately. Factors are in Table A4, and the completeness audit is in Appendix B.')
    para('2.3 Scenario design and consistency checks', 'Heading 2')
    para('One-at-a-time scenarios varied F, E, or g by ±25%. Further scenarios combined grid factors of 0.05 to 0.80 kg CO₂-eq/kWh with FCR values of 1 to 2. Alabama was evaluated at its literature FCR and at fixed FCR 1.50, with other inputs held constant. Checks covered returned reference demands, contribution sums, and baseline identities. These deterministic ranges are not confidence intervals. Appendix A, Table A5 lists the scenario settings.')
    para('2.4 Model assumptions', 'Heading 2')
    para('Both cases share Feed C, processing inputs, 1006 km delivery, and a national electricity proxy. Alabama retains its literature FCR. Performance on this recipe is unverified. Airfreight and fertilizer quantities use literature values and documented background proxies. Unknown farm burdens remain unresolved, not zero. Appendix B distinguishes restored inputs, external benchmarks, and data gaps.')
    page();heading('3 Results and discussion')
    para('3.1 Indiana hotspots and model consistency', 'Heading 2')
    para(f"""The U.S. electricity factor remains {s['grid_ef']:.6f} kg CO₂-eq/kWh and delivered Feed C GWP remains {feed:.6f} kg CO₂-eq/kg feed. Restoring larval airfreight adds {ex['indiana_addition']:.3f} to Indiana's earlier 2.459 subtotal, giving {ex['indiana']:.3f}. Figure 2 shows contributions to this expanded inventory. Unresolved burdens are not represented by zero-valued bars.""")
    figure(2,'Indiana GWP contributions within the implemented inventory',figures/'expanded_hotspots.png',f"Covered GWP is {ex['indiana']:.3f}. Feed contributes {ex['feed_pct']:.2f}%, electricity {ex['electricity_pct_share']:.2f}%, bicarbonate {ex['bicarbonate_pct']:.2f}%, and larval airfreight {ex['air_pct']:.2f}%. Optional farm-water treatment is separate.",6.3)

    para('The electricity audit corrected a per-MJ result to an explicit 1 kWh demand (3.6 MJ). The 2023 U.S. benchmark of about 0.367 kg direct CO₂/kWh provides a scale check, but its generation boundary differs from delivered life-cycle GWP (U.S. Energy Information Administration, n.d.). New process-target calculations reproduced the reviewed electricity factor. Contribution sums reconciled and no database entities were written.')
    para(f"""The optional 75 kg treated-water proxy raises the subtotal to {ex['optional_water']:.3f}. Hatchery production, direct farm GHGs, and wastewater fate still need suitable data. Published hatchery results provide an external sensitivity check, not a US replacement factor (Cao et al., 2011) and are assessed in Appendix B.""")
    para('Feed dominance is consistent with the Indiana result of Al Eissa et al. (2022). Its contribution share is not directly comparable because this model uses different feed proxies and omits post-farm stages and unresolved burdens. The stronger electricity role in Sun et al. (2023) also cautions against transferring a hotspot ranking across farms without checking their inventories and electricity backgrounds.')

    # Page 5 explains sensitivity independently of the baseline hotspot results.
    page();heading('3.2 Sensitivity to feed efficiency and electricity')
    figure(3,'Sensitivity to FCR and electricity assumptions','expanded_sensitivity.png','In panel a, farm electricity and farm-grid responses overlap. Panel b varies the farm grid alone or both farm and feed-mill grids. The black point marks the reviewed baseline.',6.2)
    para(f"""Varying FCR from 1.125 to 1.875 gives {ex['fcr_low']:.3f} to {ex['fcr_high']:.3f} kg CO₂-eq/kg shrimp, or ±{ex['fcr_pct']:.2f}% of the expanded subtotal. A ±25% change in farm electricity or grid intensity changes that subtotal by ±{ex['electricity_pct']:.2f}%. The electricity responses overlap through E × g. Larval transport is fixed in these scenarios. Survival, growth, and operating responses are not predicted, and unresolved emissions could change the percentage sensitivities.""")
    para(f"""Farm-only grid scenarios give {ex['farm_grid_low']:.3f} to {ex['farm_grid_high']:.3f} kg CO₂-eq/kg shrimp. Changing farm and mill grids gives {ex['mill_grid_low']:.3f} to {ex['mill_grid_high']:.3f}. Ingredient backgrounds remain fixed. The second case assumes coordinated electricity changes across farm and mill. The updated joint grid/FCR surface is supplied separately. These deterministic ranges describe the covered inventory, not uncertainty bounds for the whole farm.""")
    # Page 6 separates the counterfactual arithmetic from causal interpretation.
    comparison_start=len(doc.paragraphs)
    page();heading('3.3 Controlled comparison with the Alabama inventory')
    para('Both cases used the same Feed C supply chain, 1006 km delivery, and national grid factor. Alabama retained its literature FCR as a counterfactual input. Performance on this recipe has not been verified. Holding FCR fixed isolated the effect of farm electricity demand (Figure 4).')
    figure(4,'Common-scope comparison with a fixed-FCR electricity contrast',figures/'alabama_comparison_clarified.png','Both cases use the same modeled feed and exclude bicarbonate. The Alabama counterfactual does not reproduce its original production system.',5.4)
    para(f"""With feed supply and farm electricity included, GWP was {s["indiana_common"]:.3f} for Indiana and {s["alabama_common"]:.3f} kg CO₂-eq/kg shrimp for the Alabama counterfactual. Alabama reached {s["alabama_fixed_fcr"]:.3f} at fixed FCR 1.50. Higher electricity demand added {s["electricity_effect_fixed_fcr"]:.3f}, while the lower literature FCR offset {abs(s["fcr_effect_fixed_electricity"]):.3f}. With the mill grid fixed, the literature-FCR ranking reversed near a shared farm-grid factor of {s["common_scope_grid_crossover"]:.3f}. Increasing Alabama delivery to 1677 km raised its subtotal to {s["alabama_longer_delivery_sensitivity"]:.3f}.""")
    para('3.4 Interpretation and limitations', 'Heading 2')
    para(f"""With larval transport and fertilizer supply restored, the expanded subtotals are {ex['indiana']:.3f} for Indiana and {ex['alabama']:.3f} for Alabama (Appendix B). The fixed-FCR contrast above remains restricted to feed and electricity. Climate, management, scale, and data provenance still confound any technology comparison.""")
    para('Direct N₂O production has been demonstrated in shrimp, but available laboratory evidence is not a US farm emission factor (Heisterkamp et al., 2016). Hatchery, infrastructure, and wastewater gaps are assessed in Appendix B. GWP alone cannot establish overall sustainability. Eutrophication, water scarcity, biodiversity, and economics require separate assessment.')
    heading('4 Conclusions')
    para('Feed dominates Indiana’s covered inventory, while electricity dominates the Alabama counterfactual. The common-feed comparison separates modeled electricity and FCR effects. The completeness audit identifies missing evidence that must be resolved before these subtotals can support farming-technology decisions.')

    for q in doc.paragraphs[comparison_start:]: q.paragraph_format.line_spacing=1

    # Format APA references with hanging indents and italicized titles.
    page();heading('References')
    refs=[
      'Al Eissa, A., Chen, P., Brown, P. B., & Huang, J.-Y. (2022). Effects of feed formula and farming system on the environmental performance of shrimp production chain from a life cycle perspective. Journal of Industrial Ecology, 26(6), 2006–2019. https://doi.org/10.1111/jiec.13370',
      'GreenDelta. (n.d.). CalculationSetup. openLCA schema. Retrieved November 21, 2026, from https://greendelta.github.io/olca-schema/classes/CalculationSetup.html',
      'International Organization for Standardization. (2006). Environmental management—Life cycle assessment—Principles and framework (ISO Standard No. 14040:2006). https://www.iso.org/standard/37456.html',
      'U.S. Energy Information Administration. (n.d.). How much carbon dioxide is produced per kilowatthour of U.S. electricity generation? Retrieved November 21, 2026, from https://www.eia.gov/tools/faqs/faq.php?id=74&t=11',
      'Winther, U., Hognes, E. S., Jafarzadeh, S., & Ziegler, F. (2020). Greenhouse gas emissions of Norwegian seafood products in 2017. SINTEF Ocean. https://www.sintef.no/contentassets/0ec2594f7dea45b8b1dec0c44a0133b4/report-carbon-footprint-norwegian-seafood-products-2017_final_040620.pdf',
    ]
    refs.extend([
      'Arbour, A. J., Bhatt, P., Simsek, H., Brown, P. B., & Huang, J.-Y. (2024). Life cycle assessment on environmental feasibility of microalgae-based wastewater treatment for shrimp recirculating aquaculture systems. Bioresource Technology, 399, Article 130578. https://doi.org/10.1016/j.biortech.2024.130578',
      'Cao, L., Diana, J. S., Keoleian, G. A., & Lai, Q. (2011). Life cycle assessment of Chinese shrimp farming systems targeted for export and domestic sales. Environmental Science & Technology, 45(15), 6531–6538. https://doi.org/10.1021/es104058z',
      'Heisterkamp, I. M., Schramm, A., de Beer, D., & Stief, P. (2016). Direct nitrous oxide emission from the aquacultured Pacific white shrimp (Litopenaeus vannamei). Applied and Environmental Microbiology, 82(13), 4028–4034. https://doi.org/10.1128/AEM.00396-16',
      'Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific agent skills: A library of procedural knowledge for research agents. arXiv. https://doi.org/10.48550/arXiv.2609.00065',
      'Sun, Y., Hou, H., Dong, D., Zhang, J., Yang, X., Li, X., & Song, X. (2023). Comparative life cycle assessment of whiteleg shrimp (Penaeus vannamei) cultured in recirculating aquaculture systems (RAS), biofloc technology (BFT) and higher-place ponds (HPP) farming systems in China. Aquaculture, 574, Article 739625. https://doi.org/10.1016/j.aquaculture.2023.739625',
    ])
    ref_paragraphs=[]
    italics=['Journal of Industrial Ecology, 26','CalculationSetup.','Environmental management—Life cycle assessment—Principles and framework','How much carbon dioxide is produced per kilowatthour of U.S. electricity generation?','Greenhouse gas emissions of Norwegian seafood products in 2017']
    italics.extend(['Bioresource Technology, 399','Environmental Science & Technology, 45','Applied and Environmental Microbiology, 82','Scientific agent skills: A library of procedural knowledge for research agents','Aquaculture, 574'])
    for txt,ital in sorted(zip(refs,italics)):
        q=doc.add_paragraph();q.paragraph_format.left_indent=Inches(.5);q.paragraph_format.first_line_indent=Inches(-.5);q.paragraph_format.space_after=Pt(8)
        first,rest=txt.split(ital,1);q.add_run(first);q.add_run(ital).italic=True
        suffix,url=rest.rsplit(' ',1);q.add_run(suffix+' ')
        label=url
        # APA 7 displays the full https:// URL, so references are exempt from the body punctuation rule.
        link=OxmlElement('w:hyperlink')
        link.set(qn('r:id'),q.part.relate_to(url,RT.HYPERLINK,is_external=True))
        link_run=OxmlElement('w:r');props=OxmlElement('w:rPr')
        size=OxmlElement('w:sz');size.set(qn('w:val'),'20');props.append(size)
        link_run.append(props);link_text=OxmlElement('w:t');link_text.text=label
        link_run.append(link_text);link.append(link_run);q._p.append(link)
        textlog.append(txt);ref_paragraphs.append(q._p)
        for rr in q.runs:rr.font.size=Pt(10)
    para('AI disclosure. OpenAI Codex assisted with literature extraction, code and unit review, calculations, figures, and writing. Results were checked against saved outputs and sources. The project collected no primary measurements. Evidence-review skills (Kassis et al., 2026) supported the literature synthesis and completeness audit.').runs[0].font.size=Pt(9)

    # Append supporting inputs after the six-page main text and references.
    def data_table(label, title, headers, rows, widths):
        q=para(label);q.runs[0].bold=True;q.paragraph_format.keep_with_next=True
        q=para(title);q.runs[0].italic=True;q.paragraph_format.keep_with_next=True
        t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
        for col,width in zip(t.columns,widths): col.width=Inches(width)
        for i,values in enumerate([headers]+rows):
            cells=t.rows[0].cells if i==0 else t.add_row().cells
            rowpr=cells[0]._tc.getparent().get_or_add_trPr()
            rowpr.append(OxmlElement('w:cantSplit'))
            for j,(cell,value) in enumerate(zip(cells,values)):
                cell.text=str(value);cell.width=Inches(widths[j])
                pr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
                for edge in ['top','left','bottom','right']:
                    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
                pr.append(borders)
                if i==0:
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E7E6E6');pr.append(shade)
                for q in cell.paragraphs:
                    q.paragraph_format.space_before=Pt(3);q.paragraph_format.space_after=Pt(3)
                    q.paragraph_format.line_spacing=1
                    for rr in q.runs:rr.font.size=Pt(9);rr.bold=i==0
            textlog.append('\t'.join(map(str,values)))
        t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))

    page();heading('Appendix A');para('Core data and modeling assumptions', 'Heading 2')
    para('These tables document the inputs behind the six-page main text. References and appendices are presented separately. Values are literature inputs, background calculations, proxies, or scenario settings. None are new farm measurements.')
    with (run/'source_inventory_verified.csv').open() as f: inventory={x['flow']:x for x in csv.DictReader(f)}
    farm_rows=[]
    farm_labels=[('feed','Feed / FCR','Common Feed C with literature FCR retained'),('farming_electricity','Farm electricity','Included in both cases'),('sodium_bicarbonate','Sodium bicarbonate','Included in Indiana. Omitted from the common comparison'),('freshwater_use','Freshwater','Optional Indiana treatment proxy. Alabama unreported'),('seawater','Seawater','Resource quantity with pumping coverage unresolved'),('land_use','Farm land area','Occupation/land-change data incomplete'),('larvae_airfreight','Larval airfreight','Restored using a generic aircraft freight proxy'),('triple_superphosphate','Triple superphosphate','Supply restored. Application emissions unresolved'),('urea','Urea','Supply restored. Application emissions unresolved'),('feed_delivery','Original feed transport','Replaced by common 1006 km scenario')]
    for key,name,status in farm_labels:
        x=inventory[key];farm_rows.append([name,x['Indiana'] or 'Not reported',x['Alabama'] or 'Not reported',x['unit_per_kg_live_shrimp'],status])
    data_table('Table A1','Literature farm inventory per kilogram of live-weight shrimp',['Input','Indiana','Alabama','Unit','Use in this model'],farm_rows,[1.35,.65,.65,.65,3.2])
    para('Note. Data from Al Eissa et al. (2022), Table 2, p. 2012, checked in source_inventory_verified.csv. The original feed transport totals reflect different recipes and routes. The controlled comparison uses a common supply chain instead. A blank literature cell is not a zero. Restored supply inputs are calculated separately from unresolved farm emissions. Land area lacks a time dimension and is not expressed as m²-year.').runs[0].font.size=Pt(9)
    para('The farm-water scenario converts 0.075 m³ to 75 kg at 1000 kg/m³ and applies a treated tap-water proxy. It does not establish the actual treatment process or quantify water scarcity. Appendix B evaluates unresolved larval rearing, infrastructure, direct farm GHGs, and wastewater burdens. Post-farm processing and distribution lie outside the selected farm-gate boundary.')

    page();heading('Appendix A continued');para('Feed composition and supply', 'Heading 2')
    with (root/'data/feed_c_lci.csv').open() as f: ingredients=list(csv.DictReader(f))
    routes={'fish_meal':'Included in the 83% background model','poultry_byproduct_meal':'Meat-and-bone meal proxy','soybean_meal':'Included in the 83% background model','wheat_flour':'Included in the 83% background model','rice_bran':'Wheat bran proxy','fish_oil':'Included in the 83% background model','soybean_lecithin':'Refined soybean oil proxy','supplements':'Norwegian vitamin/mineral mix proxy'}
    assert abs(sum(float(x['kg_per_kg_feed']) for x in ingredients)-1)<1e-9
    data_table('Table A2','Estimated Feed C recipe and ingredient representation',['Ingredient','kg/kg feed','Representation'],[[x['ingredient'].replace('_',' ').capitalize(),f"{float(x['kg_per_kg_feed']):.3f}",routes[x['ingredient']]] for x in ingredients],[1.7,1,3.8])
    para('Note. Recipe from Al Eissa et al. (2022), Table 1, p. 2009. The commercial formula was estimated and was not fully disclosed by the manufacturer. The four original ingredients cover 83% of recipe mass, and proxies cover the remaining 17%. The 1.33 kg CO₂-eq/kg supplement factor is for vitamin/mineral mix delivered to a Norwegian feed mill (Winther et al., 2020, p. 51), applied here to the undisclosed supplement blend. Proxy geography, allocation, and LCIA are not fully harmonized.').runs[0].font.size=Pt(9)
    with (run/'background_factors.csv').open() as f: ef={x['label']:float(x['ef']) for x in csv.DictReader(f)}
    mbm_share=float(next(x for x in ingredients if x['ingredient']=='poultry_byproduct_meal')['kg_per_kg_feed'])
    ingredient_gwp=ef['feed_partial']+.05*ef['meat_bone_meal']+.05*ef['wheat_bran']+.03*ef['soybean_oil']+.04*1.33
    assert abs(ingredient_gwp-0.912134347)<1e-6 and mbm_share==.05
    mbm_feed=mbm_share*ef['meat_bone_meal'];per_unit_ind=mbm_share*1.5;per_unit_al=mbm_share*1.02
    para(f"The meat-and-bone meal proxy has a factor of only {ef['meat_bone_meal']:.3f} kg CO₂-eq/kg. This low value reflects how the ecoinvent cut-off dataset treats a rendering by-product, which assigns it little of the upstream animal-production burden. Al Eissa et al. (2022, p. 2009) derived ingredient backgrounds by mass allocation instead, so this proxy probably understates poultry by-product meal. In the model it contributes {mbm_feed:.4f} kg CO₂-eq/kg feed, or {100*mbm_feed/ingredient_gwp:.2f}% of ingredient GWP. Each additional 1 kg CO₂-eq/kg assigned to this 5% fraction would add {mbm_share:.3f} kg CO₂-eq/kg feed and {per_unit_ind:.3f} kg CO₂-eq/kg Indiana shrimp, or {100*per_unit_ind/ex['indiana']:.2f}% of its covered subtotal. The Alabama counterfactual would rise by {per_unit_al:.3f}. The baseline factor is retained because no validated US poultry-meal factor is available.")
    data_table('Table A3','Processing and delivery inputs per kilogram of modeled feed',['Input','Quantity','Unit','Treatment'],[
        ['Steam','0.320','kg','Included'],['Mill electricity','0.130','kWh','National electricity proxy'],['Mill freshwater','1.333','kg','Treated tap-water proxy'],['Mill land area','0.0014','m²','Unresolved because occupation duration is unavailable'],['Feed delivery','1.006','t·km','1 kg feed over 1006 km']],[1.4,1.1,.65,3.35])
    para('Note. Inputs from Al Eissa et al. (2022), Table 2, were normalized from 480 kg steam, 195 kWh electricity, 2 m³ water, and 2.1 m² land per 1500 kg feed. Water conversion assumes 1000 kg/m³. The 1006 km route is applied to both cases. The separate Alabama delivery sensitivity uses 1677 km.').runs[0].font.size=Pt(9)
    para('Delivered feed GWP equals ingredient GWP + 0.320 × steam factor + 0.130 × mill grid factor + 1.333 × water factor + 1.006 × truck factor. The same inputs per kilogram of feed are used at each FCR.')

    page();heading('Appendix A continued');para('Impact factors and scenario settings', 'Heading 2')
    with (run/'background_factors.csv').open() as f: factors={x['label']:x for x in csv.DictReader(f)}
    labels={'electricity':'Low-voltage electricity (US)','feed_partial':'83% ingredient model','meat_bone_meal':'Meat-and-bone meal (RoW)','wheat_bran':'Wheat bran (RoW)','soybean_oil':'Refined soybean oil (US)','steam':'Chemical-industry steam (RoW)','tap_water':'Tap water (RoW)','truck_transport':'Diesel freight (global)','sodium_bicarbonate':'Sodium bicarbonate (RoW)'}
    factor_rows=[[labels[k],f"{float(x['ef']):.9f}",x['unit']] for k,x in factors.items()]
    with (expanded/'added_background_factors.csv').open() as f: added={x['label']:x for x in csv.DictReader(f)}
    for key,name in [('air_generic','Aircraft freight (global)'),('urea','Urea (North America)'),('triple_superphosphate','Triple superphosphate (RoW)')]:
        x=added[key];factor_rows.append([name,f"{float(x['ef']):.9f}",x['unit']])
    factor_rows.append(['Vitamin/mineral mix (Norway)','1.330000000','kg'])
    data_table('Table A4','GWP factors used in the calculations',['Input or aggregate','kg CO₂-eq per unit','Unit'],factor_rows,[3.45,1.8,1.25])
    para('Note. RoW = rest of world. Background factors are saved openLCA calculations from background_factors.csv and added_background_factors.csv, using ecoinvent 3.11 Cut-off and IPCC 2021 GWP100 excluding biogenic CO₂. The supplement factor is from Winther et al. (2020). The 83% model factor is per kg nominal feed, already mass-weighted. It must not be multiplied by 0.83 again. Provider names and UUIDs are retained in the CSV. Displayed factors are rounded, and calculations use full precision.').runs[0].font.size=Pt(9)
    data_table('Table A5','Deterministic scenario settings',['Scenario','Settings and fixed inputs'],[
        ['One input at a time','FCR, farm electricity, or farm grid × 0.75 to 1.25 with all other inputs fixed'],['Grid scenarios','0.05 to 0.80 kg CO₂-eq/kWh for the farm only or farm plus mill. Ingredient backgrounds fixed'],['Joint grid and FCR','Same grid range with FCR 1 to 2'],['Alabama counterfactual','8.799 kWh/kg shrimp and FCR 1.02 with common Feed C, grid, and 1006 km delivery'],['Fixed-FCR comparison','FCR 1.50 in both cases. Change only farm electricity from 0.921 to 8.799 kWh/kg'],['Delivery sensitivity','Alabama route of 1677 km with other counterfactual inputs fixed']],[1.6,4.9])
    para('Note. Scenario ranges are prescribed, not confidence intervals or measured operating changes. Alabama FCR on the modeled recipe is unverified. The common comparison includes feed and farm electricity only. Bicarbonate is removed from both subtotals. The national grid factor is not an Indiana farm measurement.').runs[0].font.size=Pt(9)

    page();heading('Appendix B');para('Inventory completeness and unresolved burdens', 'Heading 2')
    para('The completeness audit restores inputs with reported quantities and evaluates the remaining omissions. Expanded subtotals retain the approved common Feed C supply. They do not assume unknown processes are environmentally harmless.')
    with (expanded/'expanded_results.csv').open() as f: restored=list(csv.DictReader(f))
    data_table('Table B1','Restored contributions per kilogram of live-weight shrimp',['Case','Previous subtotal','Airfreight added','Fertilizer added','Expanded subtotal'],[[x['case']]+[f"{float(x[k]):.6f}" for k in ['previous_covered_subtotal','airfreight','fertilizer_supply','updated_covered_subtotal']] for x in restored],[1.1,1.35,1.35,1.35,1.35])
    para('Note. All entries are kg CO₂-eq/kg shrimp. Indiana includes bicarbonate. Alabama has zero bicarbonate in the literature inventory. Fertilizer factors cover supply, not application emissions. Generic aircraft freight is the central background proxy. Short- and medium-haul alternatives give 0.113 to 0.123 for Indiana airfreight and 0.050 to 0.054 for Alabama. These are provider scenarios, not confidence intervals.').runs[0].font.size=Pt(9)
    data_table('Table B2','Evidence and treatment of unresolved processes',['Process','Evidence and current treatment'],[
        ['Hatchery production','Cao et al. (2011), Table 2, reports 0.0708 and 0.188 kg CO₂-eq/kg harvested shrimp in Chinese systems. External benchmarks only. US production, survival and allocation data are needed.'],
        ['Farm infrastructure','Al Eissa et al. (2022), Section 2.2.3 reports <0.1% in its preliminary analysis. Source-specific justification, not a verified bound here. Equipment masses and lifetime output are unavailable.'],
        ['Direct farm GHGs','Heisterkamp et al. (2016) provides experimental evidence of N₂O production. Laboratory incubations do not establish annual US emissions. CH₄ and N₂O remain unresolved.'],
        ['Effluent and water','N/P discharge is not N₂O/CH₄. Water intake does not specify wastewater treatment. Confirm discharge, sludge fate, and whether pumping is already in farm electricity.'],
        ['Land','Area lacks occupation time and transformation history. Do not transfer a mangrove-clearing factor to these US cases.'],
        ['Post-farm stages','Processing, packaging and market distribution are outside the defined farm-gate boundary.']],[1.25,5.25])
    para(f"Applying each external hatchery benchmark to Indiana would add 2.75% to 7.30% of its covered subtotal. This is a transferability check, not a US estimate or uncertainty interval. Cao et al. also reports infrastructure burdens of 0.0205 and 0.0645 kg CO₂-eq/kg. Neither value is adopted as US baseline data.")
    para(f"Write total GWP as covered subtotal + unresolved net burden U. An additional {ex['five_percent_reference']:.3f} kg CO₂-eq/kg is 5% of Indiana's subtotal. The 5% value is an illustrative reference, not a cut-off rule. The expanded ranking reverses if U_Indiana − U_Alabama exceeds {ex['unresolved_difference_to_reverse_ranking']:.3f}. Available evidence does not bound that difference, so a complete-farm ranking remains unverified.")

    # Keep the detailed input-output schematic in the appendix, as requested.
    page();heading('Appendix C');para('System boundary and inventory flows', 'Heading 2')
    para('Figure C1 shows the intended system boundary for the expanded inventory. Inputs, production processes, and outputs appear in separate columns. Line styles distinguish included coverage, optional treatment, and processes not yet quantified.')
    figure('C1','Cradle-to-farm-gate inputs and outputs',figures/'cradle_to_farm_gate.png','GHG means greenhouse gas. Arrows show connections and are not scaled to quantities. Burdens not yet quantified are not assumed to be zero. Farm inputs follow Al Eissa et al. (2022) and Appendix A, with coverage limits assessed in Appendix B.',6.4)
    para('The optional farm-water proxy applies to Indiana only. The separate controlled comparison in Figure 4 includes feed supply and farm electricity only, so it has narrower coverage than this diagram. Processing and distribution after harvest fall outside the farm-gate boundary.').runs[0].font.size=Pt(10)

    # Save Word and text outputs; PDF rendering is a separate step.
    doc.core_properties.title=TITLE;doc.core_properties.author='Lihong Yang';doc.core_properties.subject='BSE 5984 course report on screening and counterfactual analysis'
    assert len(doc.inline_shapes)==5 and len(doc.tables)==8
    assert abs(s['alabama_fixed_fcr']-s['indiana_common']-s['electricity_effect_fixed_fcr'])<1e-9
    ref_ids={id(x) for x in ref_paragraphs}
    body_runs=[node for paragraph in doc.element.iter(qn('w:p')) if id(paragraph) not in ref_ids for node in paragraph.iter(qn('w:t'))]
    visible_text=''.join(node.text or '' for node in body_runs)
    assert len(ref_paragraphs)==10
    assert not any(mark in visible_text for mark in ';:；：|｜¦'), 'Report punctuation preference violated'
    target=dest/'BSE5984_Final_Report.docx';doc.save(target)
    (dest/'BSE5984_Final_Report_text.txt').write_text('\n\n'.join(textlog))
    print(target)

if __name__=='__main__':main()
