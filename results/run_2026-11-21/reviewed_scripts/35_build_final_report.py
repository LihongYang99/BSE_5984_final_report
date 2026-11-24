"""Build the English course report from reviewed CSV/JSON results.
Use the Codex document runtime (python-docx); render with documents/render_docx.py.
"""
from pathlib import Path
import argparse, csv, json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

TITLE='Scenario-Based Life Cycle Assessment of U.S. Shrimp Aquaculture: Energy Demand, Feed Efficiency, and Environmental Trade-offs'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);a=p.parse_args()
    run=a.run;dest=run/'report';dest.mkdir(exist_ok=True)
    s=json.loads((run/'analysis/summary.json').read_text())
    with (run/'analysis/indiana_results.csv').open() as f:r=list(csv.DictReader(f))
    feed=float(r[1]['feed_gwp']);water=float(r[2]['shrimp_gwp'])
    doc=Document();sec=doc.sections[0]
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Inches(1)
    sec.header_distance=sec.footer_distance=Inches(.45)
    for sty in ['Normal','Title','Subtitle','Heading 1','Heading 2','Caption']:
        st=doc.styles[sty];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
    normal=doc.styles['Normal'];normal.font.size=Pt(11);normal.paragraph_format.line_spacing=1
    normal.paragraph_format.space_after=Pt(6)
    for name in ['Heading 1','Heading 2']:
        doc.styles[name].font.size=Pt(11);doc.styles[name].font.bold=True
        doc.styles[name].paragraph_format.space_before=Pt(8);doc.styles[name].paragraph_format.space_after=Pt(5)
    header=sec.header.paragraphs[0];header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    rr=header.add_run('SHRIMP AQUACULTURE SCENARIOS   ');rr.font.size=Pt(9)
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');header._p.append(fld)
    textlog=[]
    def para(text,style=None):
        q=doc.add_paragraph(text,style);q.paragraph_format.widow_control=True;textlog.append(text);return q
    def heading(text):para(text,'Heading 1')
    def page():doc.add_page_break();textlog.append('\n---\n')
    def figure(number,title,name,note,width=6.4):
        q=para('');q.add_run(f'Figure {number}').bold=True;q.paragraph_format.keep_with_next=True
        q=para('');q.add_run(title).italic=True;q.paragraph_format.keep_with_next=True
        q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.add_run().add_picture(str(run/'figures'/name),width=Inches(width));q.paragraph_format.space_after=Pt(3)
        q=para('Note. '+note);q.runs[0].font.size=Pt(10)
        textlog.append(f'[Figure {number}: {name}]')
    q=para(TITLE);q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for x in q.runs:x.bold=True;x.font.size=Pt(13)
    q=para('Lihong Yang | BSE 5984 Sustainable Agroecosystems\nNovember 21, 2026');q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    heading('Abstract')
    para(f'This study develops a reproducible greenhouse-gas screening model for 1 kg of live-weight shrimp at the farm gate, using Indiana biofloc as the main case and an Alabama pond counterfactual. Literature inventories are combined with ecoinvent backgrounds and explicit feed proxies. An IPC unit audit corrected electricity from 0.135378 per MJ to {s["grid_ef"]:.6f} kg CO₂-eq/kWh. The revised Indiana estimate is {s["indiana"]:.3f} kg CO₂-eq/kg shrimp. Feed supply is the largest contributor. Controlled comparisons separate electricity demand from feed conversion ratio (FCR), while sensitivity analysis identifies priorities for data collection. Results are conditional screening estimates, not measurements or complete comparative LCAs.')
    heading('Goal, scope, and inventory')
    para('The research question is how electricity demand, grid intensity, and feed efficiency influence shrimp production GWP under a consistent accounting framework. Al Eissa et al. (2022) provide the foreground inventory. Their Indiana data were collected from a farm manager in 2019; Alabama data were drawn from an earlier pond study. These are literature-derived inputs in the present project. No new farm measurements, IoT records, or Virginia-specific data are required or claimed.')
    q=para('Table 1');q.runs[0].bold=True;q.paragraph_format.keep_with_next=True
    q=para('Selected foreground inputs per kilogram of live-weight shrimp');q.runs[0].italic=True;q.paragraph_format.keep_with_next=True
    table=doc.add_table(rows=1, cols=3);table.autofit=False
    widths=[3.7,1.4,1.4]
    for cell,txt,w in zip(table.rows[0].cells,['Input','Indiana','Alabama'],widths):cell.text=txt;cell.width=Inches(w)
    for values in [('Farm electricity (kWh)','0.921','8.799'),('FCR (kg feed/kg shrimp)','1.500','1.020'),('Sodium bicarbonate (kg)','0.110','0'),('Reported feed formulation','Feed C','Feed S')]:
        cells=table.add_row().cells
        for i,(cell,txt) in enumerate(zip(cells,values)):cell.text=txt;cell.width=Inches(widths[i])
    for i,row in enumerate(table.rows):
        for j,cell in enumerate(row.cells):
            pr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
            pr.append(borders)
            if i==0:
                shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E7E6E6');pr.append(shade)
            for q in cell.paragraphs:
                q.paragraph_format.space_before=Pt(3);q.paragraph_format.space_after=Pt(3)
                if j:q.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for z in q.runs:z.font.size=Pt(10);z.bold=i==0
    para('Note. Inputs are from Al Eissa et al. (2022, Tables 1–2). The counterfactual replaces Alabama Feed S with the same Feed C supply chain used for Indiana; it does not reproduce the original Feed S system.').runs[0].font.size=Pt(10)
    para('The intended boundary is cradle-to-farm-gate. The implemented inventory includes feed ingredients, processing and delivery, farm electricity, and Indiana bicarbonate. Farm water treatment is optional. Larval transport, farm infrastructure, wastewater treatment, and direct farm GHG emissions remain unmodeled. Post-farm packaging, ice, processing, and market transport are outside the selected boundary. Consequently, the reported total is a partial boundary screening estimate.')

    page();heading('Background model and electricity verification')
    para('The workflow uses Python 3.12, openLCA 2.7 via IPC port 8080, and the supplied ecoinvent 3.11 Cut-off database. Nine existing product systems were recalculated read-only with explicit reference units and flow properties. The impact category is IPCC 2021 GWP100, total excluding biogenic CO₂. Root provider links and contribution sums were checked; every upstream exchange was not individually audited. No database entities were changed.')
    para(f'The previous electricity result of 0.135378 was reproducible, but its returned demand was 1 MJ. Explicitly requesting 1 kWh produced a demand of 3.6 MJ and {s["grid_ef"]:.6f} kg CO₂-eq/kWh. The factor-of-3.6 difference explains the error. CalculationSetup exposes unit and flow-property fields (GreenDelta, n.d.). For context, the U.S. Energy Information Administration (EIA, n.d.) reports about 0.367 kg direct CO₂/kWh of U.S. generation in 2023. The corrected life-cycle, low-voltage factor is plausible in magnitude, but differences in boundaries and years prevent treating that benchmark as exact validation. The national market is a proxy for the farm grid.')
    para('Feed C represents 83% of ingredient mass with the existing background model and fills the remaining 17% with meat-and-bone meal, wheat bran, refined soybean oil, and a vitamin/mineral mixture proxy. The mixture factor is 1.33 kg CO₂-eq/kg delivered to a Norwegian feed mill (Winther et al., 2020, p. 51); its application to an undisclosed shrimp supplement blend is uncertain. Ingredient supply totals 0.912134 kg CO₂-eq/kg feed. Adding steam, electricity, water supply, and 1006 km delivery raises corrected Feed C GWP to '+f'{feed:.6f}. The previous 1.199407 value is retained as superseded history.')
    figure(1,'Indiana GWP hotspots after correcting the electricity unit','fig08_indiana_hotspots.png','All contributions are per functional unit. The main case excludes farm water treatment; feed-mill water is included.',6.0)
    para(f'Indiana totals {s["indiana"]:.3f} kg CO₂-eq/kg shrimp. Feed supply and delivery contribute 75.95%, farm electricity 18.25%, and bicarbonate 5.80%. Feed ingredients alone account for 55.64%. Applying a treated tap-water proxy to the reported 0.075 m³/kg adds 0.090, giving {water:.3f}; the actual water source and treatment are unverified.')

    page();heading('Electricity, grid, and FCR sensitivity')
    para('The main screening equation is G = F × C + E × g + B, where F is FCR, C is delivered Feed C GWP, E is farm electricity demand, g is the farm grid factor, and B is the bicarbonate contribution. C includes feed-mill electricity. One-at-a-time tests vary F, E, or g by ±25% while holding the other inputs fixed. These are deterministic scenarios, not confidence intervals or claims about achievable farm improvements.')
    figure(2,'Indiana sensitivity to feed efficiency and electricity assumptions','fig09_sensitivity.png','Panel A: farm electricity and farm-grid responses coincide because each scales the same E × g term. Panel B: the black point is the corrected baseline. Feed ingredient backgrounds remain fixed.',6.4)
    para(f'Varying FCR from 1.125 to 1.875 produces {s["oat_fcr_low"]:.3f}–{s["oat_fcr_high"]:.3f} kg CO₂-eq/kg shrimp, approximately ±19.0% around the baseline. A ±25% change in farm electricity or its grid factor changes the total by only ±4.56%. Thus, for this particular inventory, an equal proportional change in feed use has a larger modeled effect than farm electricity. This ranking depends on the inventory and does not establish the technical feasibility or cost of either intervention.')
    para('Broader grid scenarios span 0.05–0.80 kg CO₂-eq/kWh without assigning them to measured states or specific renewable technologies. Changing only the farm grid gives approximately 2.056–2.747 kg CO₂-eq/kg shrimp. Changing both the farm and feed-mill grids gives approximately 1.971–2.808. The latter is a supply-chain scenario because the mill and farm need not purchase the same electricity. A separate exported contour figure evaluates FCR 1–2 jointly with the grid range; it illustrates conditional combinations rather than probabilistic uncertainty.')
    heading('Environmental trade-offs beyond GWP')
    para('Feed substitution may shift burdens between climate, nutrient discharge, land use, and marine resources. Al Eissa et al. (2022) found that replacing animal proteins with plant ingredients did not improve every impact category. The present model does not calculate eutrophication, water scarcity, biodiversity, or economic performance. Reported water volumes and land areas therefore remain inventory descriptors, not comparative impact scores. FCR improvements could alter survival, growth, feed composition, or aeration requirements; the one-at-a-time model holds those responses fixed.')

    page();heading('Alabama counterfactual and fixed-FCR comparison')
    para('The comparison uses a common scope of feed production/delivery and farm electricity. Both cases share Feed C, processing, 1006 km delivery, and the grid factor. Bicarbonate, fertilizers, and other farm inputs are excluded from both subtotals. One contrast retains literature FCR and electricity; the other fixes FCR at 1.5 to isolate electricity demand. Neither reconstructs Alabama Feed S.')
    figure(3,'Separating farm electricity demand from feed efficiency','fig11_alabama_comparison.png','These are counterfactual subtotals, not full farm footprints. The Indiana value differs from Figure 1 because bicarbonate is excluded to maintain the common scope.',5.9)
    para(f'The common-scope subtotal is {s["indiana_common"]:.3f} for Indiana and {s["alabama_common"]:.3f} kg CO₂-eq/kg shrimp for the Alabama counterfactual. Holding FCR at 1.5 gives {s["alabama_fixed_fcr"]:.3f} for Alabama electricity demand. Relative to Indiana, the isolated electricity effect is +{s["electricity_effect_fixed_fcr"]:.3f}; the lower literature FCR offsets {abs(s["fcr_effect_fixed_electricity"]):.3f}. These are arithmetic effects of prescribed inputs. Differences in scale, climate, operating practice, data collection, and biological performance prevent attributing the whole contrast to farming technology.')
    para(f'Under a shared farm-grid sensitivity, the two literature-FCR subtotals cross near {s["common_scope_grid_crossover"]:.3f} kg CO₂-eq/kWh, with feed-mill electricity held at baseline. This illustrates dependence of the ranking on assumptions. Using the source’s 1677 km Alabama delivery route instead of the standardized route raises its counterfactual subtotal to {s["alabama_longer_delivery_sensitivity"]:.3f}.')
    heading('Limitations and conclusion')
    para('Limitations include incomplete farm coverage, mismatched geographies, allocation choices, and feed proxies. Complete feed mass representation does not ensure methodological harmonization. The low meat-and-bone-meal factor cannot establish poultry meal’s actual footprint. Published cradle-to-market totals are not directly comparable. Within these limits, feed efficiency is the dominant proportional sensitivity for Indiana, and the fixed-FCR contrast reveals the strong effect of the reported Alabama electricity demand. Better farm energy records, actual feed specifications, and regional electricity data would strengthen the next assessment.')
    para('AI disclosure. OpenAI Codex assisted with code review, unit debugging, literature extraction, scenario calculations, figures, and report drafting. Calculations were executed and checked against saved outputs and cited sources. No primary measurements were generated.').runs[0].font.size=Pt(10)

    page();heading('References')
    refs=[
      'Al Eissa, A., Chen, P., Brown, P. B., & Huang, J.-Y. (2022). Effects of feed formula and farming system on the environmental performance of shrimp production chain from a life cycle perspective. Journal of Industrial Ecology, 26(6), 2006–2019. https://doi.org/10.1111/jiec.13370',
      'GreenDelta. (n.d.). CalculationSetup. openLCA schema. Retrieved November 21, 2026, from https://greendelta.github.io/olca-schema/classes/CalculationSetup.html',
      'U.S. Energy Information Administration. (n.d.). How much carbon dioxide is produced per kilowatthour of U.S. electricity generation? Retrieved November 21, 2026, from https://www.eia.gov/tools/faqs/faq.php?id=74&t=11',
      'Winther, U., Hognes, E. S., Jafarzadeh, S., & Ziegler, F. (2020). Greenhouse gas emissions of Norwegian seafood products in 2017 (Report No. 2019:01505). SINTEF Ocean. https://www.sintef.no/contentassets/0ec2594f7dea45b8b1dec0c44a0133b4/report-carbon-footprint-norwegian-seafood-products-2017_final_040620.pdf',
    ]
    italics=['Journal of Industrial Ecology, 26','CalculationSetup.','How much carbon dioxide is produced per kilowatthour of U.S. electricity generation?','Greenhouse gas emissions of Norwegian seafood products in 2017']
    for txt,ital in zip(refs,italics):
        q=doc.add_paragraph();q.paragraph_format.left_indent=Inches(.5);q.paragraph_format.first_line_indent=Inches(-.5);q.paragraph_format.space_after=Pt(12)
        first,rest=txt.split(ital,1);q.add_run(first);q.add_run(ital).italic=True;q.add_run(rest);textlog.append(txt)
    doc.core_properties.title=TITLE;doc.core_properties.author='Lihong Yang';doc.core_properties.subject='BSE 5984 course report; screening and counterfactual analysis'
    target=dest/'BSE5984_Final_Report.docx';doc.save(target)
    (dest/'BSE5984_Final_Report_text.md').write_text('\n\n'.join(textlog))
    print(target)

if __name__=='__main__':main()
