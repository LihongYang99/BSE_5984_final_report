# Scenario-Based Life Cycle Screening of U.S. Shrimp Aquaculture

Energy Demand, Feed Efficiency, and Environmental Trade-offs  
BSE 5984 Sustainable Agroecosystems  
Updated November 24, 2026 · Expanded inventory calculations: November 23, 2026

This project estimates global warming potential (GWP) for Indiana biofloc shrimp production and compares it with an Alabama pond counterfactual. Both cases use the same Feed C supply chain and their literature-reported electricity demand and feed conversion ratio (FCR). The functional unit is 1 kg live-weight shrimp at the farm gate. The intended boundary is cradle-to-farm-gate, but inventory gaps and feed proxies limit the analysis to partial GWP screening. It cannot provide a complete comparative LCA or reproduce Alabama’s original production system.

All foreground inputs come from literature. The project uses no new farm measurements, IoT records, or Virginia-specific data. Differences between scenarios cannot be attributed entirely to farming technology.

Feed C is the estimated Indiana commercial-feed recipe reported by Al Eissa et al. (2022). The manufacturer did not disclose the full formula. It is the only recipe modeled here: 30% fishmeal, 5% poultry by-product meal, 20% soybean meal, 30% wheat flour, 5% rice bran, 3% fish oil, 3% soybean lecithin, and 4% supplements by mass. Both cases use this supply chain. Alabama retains its literature FCR as a counterfactual input; performance after changing feed has not been verified.

## Current status and where to start

Steps 01 to 30 document the original model development. Steps 31 to 34 produced the unit-audited GWP screening and controlled Alabama comparison. Step 38 builds the report. Steps 35 to 37 built an earlier report and figure collection. They were deleted on November 24, 2026. Steps 39 to 41 restore known omitted inputs, update the sensitivities, and independently validate the expanded results. Step 42 exports the editable draw.io input-output boundary diagram for Appendix C. Step 43 gives literature-based screening estimates for the burdens that diagram marks as not yet measured.

- Read the [Final Report PDF](report/BSE5984_Final_Report.pdf): six body pages, one reference page, and six appendix pages.
- For current numerical results, use [expanded_summary.json](results/completeness_2026-11-23/expanded_summary.json) and [expanded_results.csv](results/completeness_2026-11-23/expanded_results.csv).
- To reproduce the work, follow the [run instructions](#recommended-run-order) with the existing project `.venv`.
- Read the [completeness evidence review](results/completeness_2026-11-23/EVIDENCE_REVIEW.md) for restored inputs, unresolved burdens, and source applicability. The earlier [METHOD_NOTES.md](results/run_2026-11-21/METHOD_NOTES.md) records the November 21 scope.

The November 23 correction adds larval airfreight and Alabama fertilizer supply using literature quantities and new read-only openLCA calculations. These inputs had been omitted without an adequate completeness assessment. Unknown burdens are now documented and assessed separately; they are not assumed to be zero. The approved common Feed C scenario is retained. No database entities were created or modified.

## Relationship to previous research

The report now synthesizes four closely related shrimp LCAs. [Cao et al. (2011)](https://doi.org/10.1021/es104058z) already evaluated feed, electricity, and grid/FCR scenarios. [Al Eissa et al. (2022)](https://doi.org/10.1111/jiec.13370) is the closest precedent and supplies the US foreground inventories. [Sun et al. (2023)](https://doi.org/10.1016/j.aquaculture.2023.739625) shows the importance of electricity in Chinese RAS, BFT, and higher-place pond comparisons. [Arbour et al. (2024)](https://doi.org/10.1016/j.biortech.2024.130578) evaluates wastewater-treatment trade-offs using the same Indiana farm background as Al Eissa, so the two papers are not independent farm observations.

The project's contribution is a reproducible, case-specific reanalysis under common feed, delivery, grid, and comparison-scope assumptions. The fixed-FCR case isolates the modeled electricity-demand effect, while the literature-FCR case shows the feed-efficiency offset. Farm-only and farm-plus-mill scenarios separate where electricity changes occur. The completeness audit shows how unresolved burdens limit the ranking. These are analytical contributions using secondary data. Feed/electricity hotspots and sensitivity analysis are established methods, and correcting the internal electricity-unit error is quality control.

The [literature synthesis and contribution audit](docs/literature/LITERATURE_REVIEW_NOTES.md) records claim locations, source relationships, search terms, and limits. This is a targeted narrative review and makes no claim of exhaustive coverage or methodological priority. No new literature values were substituted into the calculations.

## Reviewed results

Use [`results/completeness_2026-11-23/`](results/completeness_2026-11-23/) for the expanded covered inventory. The original [`results/run_2026-11-21/`](results/run_2026-11-21/), `outputs/`, `data/`, and `figures/` are preserved. Expanded subtotals still do not represent complete farm footprints.

| Indicator | Reviewed result | Unit / scope |
| --- | ---: | --- |
| US electricity market factor | 0.487361 | kg CO₂-eq/kWh; national low-voltage background proxy |
| Feed C ingredient supply | 0.912134 | kg CO₂-eq/kg feed; proxy hybrid |
| Feed C including processing and delivery | 1.245165 | kg CO₂-eq/kg feed; 1006 km delivery |
| Indiana expanded covered subtotal | 2.576773 | kg CO₂-eq/kg live shrimp; feed, electricity, bicarbonate, larval airfreight |
| Indiana with optional farm tap-water proxy | 2.666711 | Same, plus 75 kg treated water |
| Alabama expanded counterfactual, FCR 1.02 | 5.613092 | Common Feed C; farm electricity, larval airfreight, and fertilizer supply |
| Indiana common-scope comparison | 2.316607 | Feed supply/delivery + farm electricity only |
| Alabama counterfactual, literature FCR 1.02 | 5.558358 | Same common scope and Feed C supply chain |
| Alabama counterfactual, fixed FCR 1.50 | 6.156038 | Changes only farm electricity relative to Indiana common scope |

The electricity audit found a unit error: `0.135378` was calculated for 1 MJ but labeled per kWh. Requesting 1 kWh explicitly returns a demand of 3.6 MJ and `0.487361 kg CO₂-eq/kWh`. The correction applies to both feed-mill and farm electricity, replacing the old Feed C total of `1.199407` and Indiana total of `2.066366`. It changes the units, not the electricity scenario. See the [method notes](results/run_2026-11-21/METHOD_NOTES.md), [paired unit test](results/run_2026-11-21/electricity_unit_test.json), and [audited factors](results/run_2026-11-21/background_factors.csv).

For the original controlled feed-and-electricity contrast, compare Alabama's `5.558358` with Indiana's `2.316607`; the fixed-FCR comparison isolates electricity demand. For the expanded covered inventory, compare `5.613092` with `2.576773`. The latter includes farm-specific bicarbonate, larval transport, and fertilizer quantities and therefore does not isolate a single cause. Neither comparison establishes a farming-technology advantage.

Indiana airfreight adds `0.117594` to its previous `2.459179` subtotal. Alabama airfreight adds `0.052077` and fertilizer supply adds `0.002656`. Fertilizer factors are per kg product, not per kg nitrogen or phosphorus; application emissions remain unresolved. The [added factors](results/completeness_2026-11-23/added_background_factors.csv) retain process names, UUIDs, units, locations, and contribution sums.

The EIA's 2023 benchmark is about 0.367 kg direct CO₂ per kWh generated. It provides an order-of-magnitude check, but its generation-only CO₂ boundary differs from the model's life-cycle CO₂-equivalent factor for delivered low-voltage electricity. The national grid factor is also a proxy for Indiana, not a farm measurement. [EIA source](https://www.eia.gov/tools/faqs/faq.php?id=74&t=11)

## Deliverables

- [English Final Report: Word](report/BSE5984_Final_Report.docx)
- [English Final Report: PDF](report/BSE5984_Final_Report.pdf)
- [Completeness evidence and remaining data needs](results/completeness_2026-11-23/EVIDENCE_REVIEW.md)
- [Original methods, assumptions, and source verification](results/run_2026-11-21/METHOD_NOTES.md)
- [Verified literature inventory](results/run_2026-11-21/source_inventory_verified.csv)
- [Expanded farm results](results/completeness_2026-11-23/expanded_results.csv) and [hotspots](results/completeness_2026-11-23/expanded_hotspots.csv)
- [Updated sensitivity](results/completeness_2026-11-23/sensitivity_oat.csv), [grid scenarios](results/completeness_2026-11-23/grid_sensitivity.csv), and [joint grid/FCR surface](results/completeness_2026-11-23/grid_fcr_surface.csv)
- [External hatchery benchmark scenarios](results/completeness_2026-11-23/hatchery_external_benchmarks.csv) and [airfreight provider scenarios](results/completeness_2026-11-23/air_provider_scenarios.csv)
- [Alabama counterfactual and fixed-FCR comparison](results/run_2026-11-21/analysis/alabama_controlled_comparison.csv)
- [Expanded summary](results/completeness_2026-11-23/expanded_summary.json), [new IPC checks](results/completeness_2026-11-23/ipc_checks.json), and [independent validation](results/completeness_2026-11-23/validation.csv)
- [Updated scientific figures](results/completeness_2026-11-23/figures/): expanded hotspots, sensitivity, grid/FCR contours, and coverage correction; 600-dpi PNG, vector PDF, and editable SVG. The [original figures](results/run_2026-11-21/figures/) remain archived.

The report uses APA author-date citations and references. Body text is single-spaced or near-single-spaced, with figures and a table in the main text and references on a separate page. It includes an AI-use disclosure.

## LCA workflow diagram (Figure 1)

The methods diagram follows four LCA phases: goal and scope definition, life cycle inventory (LCI), life cycle impact assessment (LCIA), and interpretation. Bidirectional arrows show feedback between phases. Labels identify the partial GWP boundary and Alabama counterfactual. ISO conformity and a complete comparative LCA have not been established.

- [PNG, 600 dpi](report/report_figures/lca_workflow_nature.png), [vector PDF](report/report_figures/lca_workflow_nature.pdf), [editable SVG](report/report_figures/lca_workflow_nature.svg), and [caption](report/report_figures/lca_workflow_nature_caption.txt)

The helper draws the diagram in Matplotlib, checks that labels fit, and runs offline without numerical inputs or IPC calls. To regenerate it for Step 38:

```bash
.venv/bin/python scripts/report_figures/plot_lca_workflow.py
```

The community [nature-figure skill](https://github.com/lex8777/nature-skill/tree/main/skills/nature-figure) informed the restrained colors, consistent sans-serif type, white background, and editable vector text. The skill is independent of journal approval.

The earlier Step 36 workflow script, the Step 37 styled figure collection (`report/figures/nature_2026-11-23/`), and the Step 35 report exporter were removed on November 24, 2026. Their farm hotspot and sensitivity figures had been superseded by the [Step 40 figures](results/completeness_2026-11-23/figures/) and the current report figures.

## Revised final report (Step 38)

The current report has six body pages, one APA reference page, and six appendix pages. Sections 1.1 and 1.2 synthesize previous research and define the study contribution. Four main-text figures cover the LCA workflow, expanded Indiana hotspots, updated sensitivity analysis, and the original controlled feed-and-electricity comparison. Appendix A contains Tables A1 to A5: farm inputs, feed composition, processing and delivery, GWP factors, and scenario settings. Appendix B documents restored contributions and the evidence for unresolved processes, and Table B3 on its own page gives the Step 43 screening estimates. Appendix C adds Figure C1, a cradle-to-farm-gate input-output diagram referenced in Methods Section 2.1. Methods also includes an assumptions subsection. References and appendices are outside the six-page main-text count.

`38_update_final_report.py` reads the November 21 reviewed run and November 23 expanded results, then writes `report/BSE5984_Final_Report.docx` and `report/BSE5984_Final_Report_text.txt` in place. Commit each new version in git instead of creating versioned output directories. Run it after Steps 39 to 42. It reads all five figures from [`report/report_figures/`](report/report_figures/): four drawn by the helpers in `scripts/report_figures/` and the draw.io boundary figure exported by Step 42. All five use Calibri, vector SVG/PDF exports, and PNG images with at least 600 dpi at their report width. The `plot_lca_workflow.py`, `plot_expanded_hotspots.py`, `plot_expanded_sensitivity.py`, and `plot_alabama_comparison.py` helpers in `scripts/report_figures/` regenerate the four main-text figures from saved results. Run each with the project `.venv` before Step 38 if those figures need regeneration. Their shared `figure_fonts.py` registers the installed Microsoft Word Calibri fonts and fixes SVG IDs and PDF/SVG dates so unchanged Matplotlib figures remain byte-identical. Step 42 uses draw.io Desktop instead and checks the exported PDF for Calibri. No font files are copied into the project.

Body text and figure labels contain no semicolons, colons, or vertical bars. The reference list is exempt so that it follows APA 7: full `https://` URLs, colons before subtitles, and ISO standard numbers such as `14040:2006`. The builder checks the body rule and leaves the reference list out of that check. It needs `python-docx`, which is listed in [requirements.txt](requirements.txt), and makes no database calls. The report date is the `REPORT_DATE` constant at the top of the script. Its paths and prose are specific to these versioned inputs; `--run` alone does not redirect the expanded dataset. Render the PDF and inspect the changed pages before committing.

The [report QA record](report/report_qa.json) documents the latest change, pagination, visual inspection, and hashes. The meat-and-bone meal allocation note remains in Section 2.1 and Appendix A.

## Cradle-to-farm-gate boundary diagram (Step 42)

Edit [`cradle_to_farm_gate.drawio`](report/report_figures/cradle_to_farm_gate.drawio) in draw.io Desktop. Its boxes, labels, and attached arrows are native editable objects. Inputs appear in a blue column, production processes in green, and outputs in purple. Coverage is encoded separately with solid outlines for included items, dash-dot outlines for the optional water scenario, dotted outlines (thicker, pattern 2 2) for Step 43 screening estimates, and dashed outlines for burdens not yet quantified. Gray identifies post-farm stages outside scope. Hatchery production, infrastructure and land, and direct farm gases show their Table B3 ranges in kg CO₂-eq per kg shrimp. Indiana effluent and sludge remain not yet quantified. Upstream GHGs are represented in supply factors. Arrow widths do not represent quantities.

`42_plot_system_boundary.py` exports the saved draw.io source to PNG, PDF, and SVG without rebuilding or overwriting manual diagram edits. It needs draw.io Desktop at `/Applications/draw.io.app` and Calibri available to macOS. On this Mac, `~/Library/Fonts/Calibri.ttf` and `Calibrib.ttf` link to the installed Microsoft Word fonts. The exporter uses a fresh temporary draw.io profile and refuses to publish a PDF with substituted fonts. Its 3840-pixel PNG is 600 dpi at the 6.4-inch width used in Appendix C. The SVG keeps text editable and requires Calibri on the viewing computer. Draw.io export metadata may change between runs.

The diagram describes the expanded inventory. The controlled feed-and-electricity comparison has narrower coverage. It makes no new measurements or impact calculations and does not assert complete cradle-to-farm-gate coverage.

- [Editable draw.io source](report/report_figures/cradle_to_farm_gate.drawio)
- [Boundary PNG, 600 dpi](report/report_figures/cradle_to_farm_gate.png)
- [Boundary vector PDF](report/report_figures/cradle_to_farm_gate.pdf) and [editable SVG](report/report_figures/cradle_to_farm_gate.svg)
- [Caption and scope notes](report/report_figures/cradle_to_farm_gate_caption.txt)

Save diagram edits in draw.io, then export the figure before rebuilding the report with Step 38.

```bash
.venv/bin/python scripts/42_plot_system_boundary.py
```

## Screening estimates for unresolved burdens (Step 43)

`43_quantify_unresolved_burdens.py` gives low, central, and high values in kg CO₂-eq per kg live-weight shrimp for hatchery production, direct N₂O, pond CH₄, infrastructure, land-use change, Alabama pond-fill pumping, discharged N, and urea CO₂. It runs offline from the expanded subtotals, the audited electricity factor, and literature values, and writes [`results/unresolved_2026-11-24/`](results/unresolved_2026-11-24/). It refuses to overwrite that directory.

| Case | Added by screening estimates | Covered subtotal plus screening |
| --- | ---: | ---: |
| Indiana | 0.33–0.92 (central 0.58) | 2.91–3.49 |
| Alabama | 0.35–1.68 (central 0.75) | 5.96–7.29 |

Direct N₂O dominates the Indiana additions. It uses the IPCC aquaculture nitrogen balance (1.8 ± 0.7% of N released to water emitted as N₂O-N) with an assumed 35–40% feed crude protein. Pond CH₄ dominates the Alabama additions. It uses measured aerated-pond fluxes from subtropical China (Yang et al., 2023) over the 13-week Gulf Shores grow-out. Within these ranges U_Indiana − U_Alabama is at most 0.57, so the ranking does not reverse. Indiana tank CH₄ and sludge fate are not quantified; they would need to exceed 2.47 to reverse it.

These are deterministic screening ranges, not confidence intervals or farm measurements, and they are not added to the reported subtotals. The [evidence notes](results/unresolved_2026-11-24/EVIDENCE_NOTES.md) list every value with its source page and how it was checked, the assumptions, and a source that could not be used (Naegel, 2010).

```bash
rm -rf results/unresolved_2026-11-24   # only when deliberately regenerating
.venv/bin/python scripts/43_quantify_unresolved_burdens.py
```

## Inventory completeness correction (Steps 39 to 41)

The source provides larval airfreight of 0.140 t·km/kg shrimp for Indiana and 0.062 for Alabama, plus Alabama urea of 0.0017 kg and triple superphosphate of 0.0003 kg. Step 39 restores these supplies. The generic global airfreight market is a proxy; short- and medium-haul alternatives are separate provider scenarios. Urea uses a North American market and triple superphosphate a RoW descriptor; the latter's description says global, a discrepancy retained in the evidence record. No US-specific representativeness is claimed for that dataset.

| Script | Purpose | Inputs and outputs | Database behavior |
| --- | --- | --- | --- |
| `39_audit_inventory_completeness.py` | Calculate omitted supplies with explicit units; add them to the saved farm model; assemble external hatchery benchmarks. | Literature quantities, reviewed factors, provider UUIDs → added factors, provider records, expanded subtotals/hotspots, and scenario CSVs. | Read-only transient Process-target calculations; no product-system creation. `--offline` reuses saved factors. |
| `40_plot_expanded_inventory.py` | Recalculate Indiana sensitivity with restored airfreight held fixed and export four updated figures. | Expanded subtotals and reviewed factors → OAT/grid/FCR tables, summary JSON, PNG/PDF/SVG figures. | Offline; no IPC. |
| `41_validate_expanded_results.py` | Independently reconstruct totals and scenarios, verify explicit demand and contribution sums, and check old file hashes. | Saved factors and CSVs → `validation.csv`. No calculation-model imports. | Offline; no IPC. |

To reproduce the expanded results from saved factors:

```bash
cd ~/Desktop/final_project
.venv/bin/python scripts/39_audit_inventory_completeness.py --offline
.venv/bin/python scripts/40_plot_expanded_inventory.py
.venv/bin/python scripts/41_validate_expanded_results.py
```

These commands refresh derived outputs in `results/completeness_2026-11-23/` while preserving the saved factors and November 21 run. For a new background calculation, start standard openLCA IPC on port 8080 and give Step 39 a fresh directory:

```bash
.venv/bin/python scripts/39_audit_inventory_completeness.py --out results/completeness_new_audit
```

Step 39 refuses to overwrite existing factors in online mode. Steps 40, 41, and 38 currently read the versioned November 23 directory; review a new audit before changing their input paths. The calculation checks reproduce the reviewed electricity result through a Process target and confirm that all nine existing product systems remain unchanged.

Hatchery production, direct farm CH₄/N₂O, infrastructure, wastewater fate, and land-related burdens are assessed in the [evidence review](results/completeness_2026-11-23/EVIDENCE_REVIEW.md) and Appendix B. Cao et al. (2011) provides Chinese hatchery benchmarks of 0.0708 and 0.188 kg CO₂-eq/kg harvested shrimp; their conditional addition is tested separately, not adopted as US data or uncertainty bounds. These checks do not close the inventory.

## Project layout

```text
final_project/
├── .venv/                        # Python 3.12 analysis environment
├── README.md                     # Current project guide
├── requirements.txt              # Pinned Python packages for the project .venv
├── .gitignore                    # Excludes .venv, caches, and lock files
├── docs/
│   ├── STEPS_01-30.md            # Historical Steps 01–30
│   └── literature/               # Literature synthesis notes, Crossref records, editorial sources
├── scripts/                      # Steps 01–42
│   └── report_figures/           # Helpers that draw report Figures 1–4, plus the shared Calibri setup
├── report/
│   ├── BSE5984_Final_Report.*    # Current Word, PDF, and text export (built by Step 38)
│   ├── report_qa.json            # QA record for the latest report change
│   └── report_figures/           # The five figures embedded in the report
├── data/                         # Original prepared inventories
├── outputs/                      # Legacy candidates, mappings, and calculations
├── figures/                      # Legacy figures; current expanded plots are under results
└── results/
    ├── review_2026-11-21/         # Literature extraction and initial diagnostic evidence
    ├── completeness_2026-11-23/   # Current expanded results, evidence review, and figures
    ├── unresolved_2026-11-24/     # Step 43 screening estimates and evidence notes
    └── run_2026-11-21/            # Preserved unit-audited calculation package
        ├── background_factors.csv
        ├── analysis/             # Corrected results and scenario tables
        ├── figures/              # Original fig08–fig11, PNG and PDF
        ├── report/               # Original Word/PDF report and render QA
        ├── reviewed_scripts/     # Code snapshot used for the delivered package
        └── legacy/               # Pre-update README, code, data, outputs, and figures
```

The run's `README_snapshot.md` records the November 21 handoff. This root README covers later updates, and `report/BSE5984_Final_Report.pdf` is the current report. Keep the run snapshots and manifests as historical records; the archived November 21 render folders contain intermediate QA files.

## Python environment: macOS / VS Code

Use the project `.venv` (`final_project/.venv`) for all LCA analysis. The recorded environment is Python 3.12.13 on a Mac M4. `pip check` passed on November 24, 2026.

Activate the existing `.venv`:

```bash
cd ~/Desktop/final_project
source .venv/bin/activate
python -c "import sys; print(sys.executable)"
python -m pip check
```

For initial setup on a new machine only:

```bash
cd ~/Desktop/final_project
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

[requirements.txt](requirements.txt) pins the current environment: `olca-ipc==2.7.0`, `olca_schema==2.7.0`, pandas, NumPy, Matplotlib, and python-docx, plus their dependencies. SciPy and openpyxl were removed on November 24, 2026 because no script imports them. All offline steps (34, 38 to 42, and the figure helpers) were rerun afterwards with unchanged results. [environment_requirements.txt](results/run_2026-11-21/environment_requirements.txt) is the historical November 21 record and still lists them.

In VS Code, open `final_project`, run Python: Select Interpreter, and choose `final_project/.venv/bin/python`. Check the interpreter path in a new terminal. Use `deactivate` to leave the environment. A repeated `(.venv)` prompt does not by itself mean two environments exist; check `sys.executable`.

If an import fails, use `.venv/bin/python -m pip ...` to install into the project environment. The command is `python -m pip`; `python -m python -m pip` is invalid.

## openLCA and database safety

The project uses openLCA 2.7, ecoinvent 3.11 Cut-off, and standard JSON-RPC IPC on port 8080. Start the standard IPC server in openLCA’s developer tools. The scripts do not use gRPC; `Unexpected HTTP/1.x request` usually indicates a protocol mismatch.

Only the database copy `Shrimp_LCA_US_2026` may be written. Keep the original ecoinvent database unchanged. Step 32 uses existing product systems and Step 39 calculates existing processes transiently; neither writes database entities. IPC could not independently verify the active database name; `provenance.json` records this limitation.

Steps 06, 14, 16, 18, 22, and 27 can create database objects. Each now refuses unless given an explicit flag: `--write` for 06, 14, 16, and 18 (18 only when its product system is missing), and `--calculate` for 22 and 27. Do not batch-run the numbered scripts. The current Step 31 runs offline; it replaces an earlier version that could create product systems. Step 32 requires existing product-system UUIDs and fails if they are unavailable.

## Recommended run order

For the original November 21 workflow, run the unit audit before Step 31: 32, 31, 33, then 34. Steps 01 to 30 record historical preparation and do not need to be repeated. To reproduce the current correction, use the saved-factor commands for Steps 39 to 41 above, run Step 42 for the Appendix C diagram, then run Step 38 for the current report.

| Execution order | Script | Required input | Main output | openLCA needed? |
| --- | --- | --- | --- | --- |
| 1: Step 32 | `32_audit_units_and_background.py` | Existing product-system UUIDs; new `--out` directory | Explicit-unit factors, IPC checks, and legacy snapshot | Yes; read-only |
| 2: Step 31 | `31_calculate_indiana_farming_gwp.py` | Step 32 `--run` directory | Indiana results and hotspot contributions in `analysis/` | No |
| 3: Step 33 | `33_scenarios_and_figures.py` | Same `--run`; `--controlled-alabama` | Sensitivity tables, counterfactual comparison, summary, and figures | No |
| 4: Step 34 | `34_validate_reviewed_results.py` | Completed Step 33 run with Alabama results | `validation.csv` | No |

Steps 31 to 34 handle the calculation and its validation:

- Step 32 checks the reference demand behind each kWh, kg, or tonne-km and saves the audited background factors.
- Step 31 multiplies inventory quantities by audited factors, totals Indiana feed and farming GWP, and evaluates the optional water proxy. It reads CSV files without calling openLCA.
- Step 33 plots hotspots, varies electricity, grid, and FCR assumptions, and separates the Alabama electricity-demand effect from the FCR effect.
- Step 34 independently reconstructs totals, checks the unit correction and scenario arithmetic, and verifies archived files. These checks establish numerical consistency, not inventory completeness.

Keep `--controlled-alabama` enabled: Steps 34 and 38 require its comparison fields. Run Python without `-O` so assertion checks remain active.

To validate the delivered results offline:

```bash
cd ~/Desktop/final_project
.venv/bin/python scripts/34_validate_reviewed_results.py --run results/run_2026-11-21
```

To recalculate into a new run directory while openLCA IPC is running:

```bash
cd ~/Desktop/final_project
RUN_DIR="results/run_$(date +%Y%m%d_%H%M%S)"
.venv/bin/python scripts/32_audit_units_and_background.py --out "$RUN_DIR" &&
.venv/bin/python scripts/31_calculate_indiana_farming_gwp.py --run "$RUN_DIR" &&
.venv/bin/python scripts/33_scenarios_and_figures.py --run "$RUN_DIR" --controlled-alabama &&
.venv/bin/python scripts/34_validate_reviewed_results.py --run "$RUN_DIR"
```

The `&&` chain stops if a step fails. The scripts refuse to overwrite an existing audit, analysis, or figure directory. Step 32 archives the preceding README, scripts, inventories, outputs, and figures with SHA-256 hashes. Step 34 checks those archives and the original data/outputs/figures, then writes `validation.csv`. Rerunning Step 34 refreshes that file.

Step 38 needs `python-docx`, which `requirements.txt` installs:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

PDF export uses LibreOffice (`brew install --cask libreoffice`), followed by visual inspection of every changed page. After editing, regenerate both Word and PDF and check that pagination is still 6 body pages, 1 reference page, and 5 appendix pages:

```bash
.venv/bin/python scripts/38_update_final_report.py
soffice --headless --convert-to pdf --outdir report report/BSE5984_Final_Report.docx
```

## Version control

The project is a git repository. `.venv/`, `__pycache__/`, `.DS_Store`, and Office lock files are ignored. Commit after each report or analysis change instead of copying directories.

Git history starts on November 24, 2026 with the current project. Earlier report versions and snapshot directories were deleted that day and are not recoverable: the 14 `report/archive_*` and 12 `report/revision_*` directories, `report/figures/`, `results/refactor_2026-11-23/`, and Steps 35 to 37. The November 21 reviewed package in `results/run_2026-11-21/` is kept because Steps 34 and 41 check its hashes.

Some files stay on this computer and are not published in the GitHub repository (see `.gitignore`):

- `results/review_2026-11-21/al_eissa_text.txt` and `table2.png`: full text and a table image of Al Eissa et al. (2022). Use the [DOI](https://doi.org/10.1111/jiec.13370) instead.
- `outputs/electricity_gwp_contributions.csv`, its copy in `results/run_2026-11-21/legacy/outputs/`, and `results/run_2026-11-21/electricity_contributions_corrected.csv`: ecoinvent process-level GWP contributions (17,182 rows), withheld under the ecoinvent licence.

In a clone without these files, Steps 34 and 41 mark their hash checks as `not distributed, skipped` and still pass. On this computer they are checked in full.

## Validation and preservation

The November 21 records contain 133 passing independent checks, 10 passing IPC audit checks, and 4 passing scenario checks. They cover unit conversion, reconstructed totals, feed fractions, the fixed-FCR electricity comparison, contribution sums, scenario behavior, and file preservation. They do not cover every upstream exchange or establish that the inventory is complete.

The expanded inventory passed 174 checks in [Step 41 validation](results/completeness_2026-11-23/validation.csv), including independent reconstruction of totals and all saved scenario values, factor reconciliation, and preservation of the 55 reviewed and 76 archived files. Six new read-only background calculations were performed: three airfreight providers, two fertilizers, and an electricity cross-check. All nine product-system IDs were unchanged. These checks establish numerical consistency, not complete environmental coverage. The original report’s page inspection remains in [report/QA.md](results/run_2026-11-21/report/QA.md).

## Recovered Steps 01 to 30

Steps 01 to 30 record the original model development: inventory preparation, provider searches, supply-chain linking, and the first impact calculations. Several can create database entities, and routine use of the reviewed results does not require rerunning them. The full step table and notes are in [docs/STEPS_01-30.md](docs/STEPS_01-30.md).

## Interpretation and assumptions

Feed production and delivery account for 72.48% of Indiana’s expanded covered subtotal, farm electricity for 17.42%, bicarbonate for 5.53%, and larval airfreight for 4.56%. These are shares of the implemented inventory; unresolved burdens may change them.

Varying FCR by ±25% gives 2.110 to 3.044 kg CO₂-eq/kg shrimp, or ±18.12% of the expanded subtotal. Varying farm electricity or farm-grid intensity by ±25% changes it by ±4.35%. Grid factors of 0.05 to 0.80 give 2.174 to 2.865 when only the farm grid changes, and 2.089 to 2.926 when both farm and feed-mill grids change. The joint grid/FCR surface uses FCR values of 1 to 2. These are deterministic scenarios, not confidence intervals. Ingredient backgrounds and larval airfreight remain fixed; biological responses are not predicted.

The original controlled Alabama comparison holds the Feed C supply chain and delivery distance constant and includes feed and farm electricity only. At fixed FCR, the electricity-demand difference adds 3.839430 kg CO₂-eq/kg shrimp. Reducing FCR from 1.50 to 1.02 at Alabama electricity demand offsets 0.597679. The original 1677 km delivery scenario gives 5.664837 within that restricted scope. These controlled results remain separate from the expanded farm-specific subtotals. The comparison cannot establish a causal advantage of biofloc technology or reproduce Alabama’s original feed system.

Larval airfreight and fertilizer supply are now included. Hatchery production, infrastructure, direct farm GHGs, wastewater fate, and land-related burdens are not measured; Step 43 gives screening ranges for all but Indiana sludge fate. The original paper reports a preliminary infrastructure contribution below 0.1%; this is source-specific evidence, not a verified bound for the present model. Chinese hatchery benchmarks would add 2.75% to 7.30% of Indiana's subtotal, but cannot establish a US range. Direct N₂O production has experimental support, while a suitable annual US farm factor is still missing. Details and primary sources are in [EVIDENCE_REVIEW.md](results/completeness_2026-11-23/EVIDENCE_REVIEW.md).

Write complete farm GWP as the covered subtotal plus unresolved net burden U. The expanded comparison would reverse if U_Indiana − U_Alabama exceeded 3.036 kg CO₂-eq/kg shrimp. The Step 43 screening ranges give at most 0.57, but they are not confidence bounds. Actual water supply, regional grid representativeness, and feed-proxy equivalence also remain unresolved. Post-farm processing and distribution lie outside the chosen boundary. Only GWP is quantified; eutrophication, water scarcity, biodiversity, and economics need separate assessment.

## Sources and traceability

Primary foreground source: Al Eissa, A., Chen, P., Brown, P. B., & Huang, J.-Y. (2022). *Effects of feed formula and farming system on the environmental performance of shrimp production chain from a life cycle perspective*. Journal of Industrial Ecology, 26(6), 2006–2019. https://doi.org/10.1111/jiec.13370

The source PDF in `~/Downloads/` was read and Table 2 checked visually. Its cradle-to-market results use a broader boundary than this farm-gate screening. Sun et al. (2023) and the Chinese-system handoff are separate datasets and are excluded from the US baseline.

[METHOD_NOTES.md](results/run_2026-11-21/METHOD_NOTES.md) records the original proxy provenance and formulas. The current [evidence review](results/completeness_2026-11-23/EVIDENCE_REVIEW.md) documents the added supplies, targeted literature search, and applicability of [Cao et al. (2011)](https://doi.org/10.1021/es104058z) and [Heisterkamp et al. (2016)](https://doi.org/10.1128/AEM.00396-16). The report includes APA references, an AI-use disclosure, and the evidence-review software credit.
