# Scenario-Based Life Cycle Assessment of U.S. Shrimp Aquaculture

**Energy Demand, Feed Efficiency, and Environmental Trade-offs**  
BSE 5984 Sustainable Agroecosystems · Reviewed November 21, 2026

Indiana Biofloc is the main case. Alabama Pond is a **counterfactual comparison using the same Feed C supply chain**, with literature-reported electricity demand and FCR. The functional unit is **1 kg of live-weight shrimp at the farm gate**. The intended boundary is cradle-to-farm-gate; the implemented model is a **partial, proxy-assisted GWP screening assessment**. It is not a complete comparative LCA or a reconstruction of Alabama's original Feed S system.

The foreground data are literature-derived. No new farm measurements, IoT records, or Virginia-specific data are used. Differences between the scenarios must not be attributed entirely to farming technology.

## Reviewed results

The authoritative reviewed run is [`results/run_2026-11-21/`](results/run_2026-11-21/). The earlier `outputs/`, `data/`, and `figures/` remain unchanged.

| Indicator | Reviewed result | Unit / scope |
| --- | ---: | --- |
| US electricity market factor | 0.487361 | kg CO₂-eq/kWh; national low-voltage background proxy |
| Feed C ingredient supply | 0.912134 | kg CO₂-eq/kg feed; proxy hybrid |
| Feed C including processing and delivery | 1.245165 | kg CO₂-eq/kg feed; 1006 km delivery |
| Indiana main screening | 2.459179 | kg CO₂-eq/kg live shrimp; feed, electricity, bicarbonate |
| Indiana with optional farm tap-water proxy | 2.549117 | Same, plus 75 kg treated water |
| Indiana common-scope comparison | 2.316607 | Feed supply/delivery + farm electricity only |
| Alabama counterfactual, literature FCR 1.02 | 5.558358 | Same common scope and Feed C supply chain |
| Alabama counterfactual, fixed FCR 1.50 | 6.156038 | Changes only farm electricity relative to Indiana common scope |

**Electricity unit correction:** the former `0.135378` result was calculated for **1 MJ**, although it was labeled per kWh. Explicitly requesting 1 kWh returns demand = 3.6 MJ and `0.487361 kg CO₂-eq/kWh`. This is a verified unit bug, not a different electricity scenario. Correcting both feed-mill and farm electricity supersedes the old Feed C total of `1.199407` and Indiana total of `2.066366`. See [method notes](results/run_2026-11-21/METHOD_NOTES.md), [paired unit test](results/review_2026-11-21/electricity_unit_test.json), and [audited factors](results/run_2026-11-21/background_factors.csv).

The EIA's historical 2023 benchmark is about 0.367 kg **direct CO₂** per kWh generated. It supports an order-of-magnitude check, not exact validation of a **life-cycle CO₂-equivalent** factor for delivered low-voltage electricity. The model's national grid is not an Indiana-specific measurement. [EIA source](https://www.eia.gov/tools/faqs/faq.php?id=74&t=11)

## Deliverables

- [English Final Report — Word](results/run_2026-11-21/report/BSE5984_Final_Report.docx)
- [English Final Report — PDF](results/run_2026-11-21/report/BSE5984_Final_Report.pdf)
- [Methods, assumptions, exclusions, and source verification](results/run_2026-11-21/METHOD_NOTES.md)
- [Verified literature inventory](results/run_2026-11-21/source_inventory_verified.csv)
- [Indiana results](results/run_2026-11-21/analysis/indiana_results.csv) and [hotspots](results/run_2026-11-21/analysis/indiana_hotspots.csv)
- [Sensitivity](results/run_2026-11-21/analysis/sensitivity_oat.csv), [grid scenarios](results/run_2026-11-21/analysis/grid_sensitivity.csv), and [joint grid/FCR surface](results/run_2026-11-21/analysis/grid_fcr_surface.csv)
- [Alabama counterfactual and fixed-FCR comparison](results/run_2026-11-21/analysis/alabama_controlled_comparison.csv)
- [Machine-readable summary](results/run_2026-11-21/analysis/summary.json), [IPC checks](results/run_2026-11-21/ipc_validation.csv), and [independent validation](results/run_2026-11-21/validation.csv)
- [Publication figures](results/run_2026-11-21/figures/): `fig08` hotspots, `fig09` sensitivities, `fig10` grid/FCR contours, and `fig11` counterfactual comparison; each supplied as 300-dpi PNG and vector PDF.

The report uses APA author–date citations and references, with single spacing to match the course brief. Its main text includes the figures and table; references are separate. AI assistance is disclosed.

## Python environment — macOS / VS Code

Use **only the project `.venv`**, at `/Users/lihongyang/Desktop/final_project/.venv`, for the LCA analysis. The working environment is Python **3.12.13** on the user's Mac M4. `pip check` passed on November 21, 2026.

If `.venv` already exists, activate it; do not create another environment:

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
python -m pip install -r results/run_2026-11-21/environment_requirements.txt
python -m pip check
```

The recorded environment includes `olca-ipc==2.7.0`, `olca_schema==2.7.0`, pandas, NumPy, Matplotlib, openpyxl, and SciPy. The complete installed version record is [environment_requirements.txt](results/run_2026-11-21/environment_requirements.txt).

In VS Code, open `final_project`, run **Python: Select Interpreter**, and select `final_project/.venv/bin/python`. Check the path in a new terminal. Use `deactivate` to leave the environment. A repeated `(.venv)` prompt alone does not establish that two environments exist; `sys.executable` identifies the interpreter.

If an import fails, use `.venv/bin/python -m pip ...` so installation targets the intended interpreter. Use `python -m pip`, not `python -m python -m pip`.

## openLCA and database safety

Environment: **openLCA 2.7, ecoinvent 3.11 Cut-off, standard JSON-RPC IPC on port 8080**. Start the standard IPC server through openLCA's developer tools; do not use gRPC. `Unexpected HTTP/1.x request` usually indicates a protocol mismatch.

Only the database copy **`Shrimp_LCA_US_2026` may be written**. The original ecoinvent database must remain unchanged. The reviewed workflow uses existing product systems and performs **no database entity writes**, regardless of which database is open. IPC did not independently verify the active database name; this limitation is recorded in `provenance.json`.

Historical Steps 06, 14, 16, 18, 22, and 27 can create database objects under their respective flags or execution paths. Do not batch-run all numbered scripts. The new Step 31 is offline and replaces the former script that could create product systems. Existing product-system UUIDs must be available for Step 32; it fails rather than silently creating replacements.

## Recommended run order

The unit audit must precede Step 31, so the reviewed execution order is **32 → 31 → 33 → 34 → 35**. Steps 01–30 are historical preparation, not prerequisites to rerun.

To validate the delivered results offline:

```bash
cd ~/Desktop/final_project
.venv/bin/python scripts/34_validate_reviewed_results.py --run results/run_2026-11-21
```

To recalculate into a **new** run directory while openLCA IPC is running:

```bash
cd ~/Desktop/final_project
RUN_DIR="results/run_$(date +%Y%m%d_%H%M%S)"
.venv/bin/python scripts/32_audit_units_and_background.py --out "$RUN_DIR"
.venv/bin/python scripts/31_calculate_indiana_farming_gwp.py --run "$RUN_DIR"
.venv/bin/python scripts/33_scenarios_and_figures.py --run "$RUN_DIR" --controlled-alabama
.venv/bin/python scripts/34_validate_reviewed_results.py --run "$RUN_DIR"
```

Stop if a command fails. New-run guards refuse to overwrite an existing audit directory, analysis directory, or figure directory. Step 32 archives the preceding README, scripts, inventories, outputs, and figures with SHA-256 hashes. Step 34 checks the archive and preservation of the original data/outputs/figures.

Step 35 generates the report from a successful reviewed run and requires `python-docx`. The delivered report was built with the existing Codex document runtime, without creating another project virtual environment. To rebuild within your project environment, install the optional document dependency there and run:

```bash
.venv/bin/python -m pip install python-docx
.venv/bin/python scripts/35_build_final_report.py --run "$RUN_DIR"
```

PDF generation additionally requires a document renderer. For the delivered version, Codex used the documents skill's bundled LibreOffice renderer and visually inspected every page. Keep future Word/PDF exports together and recheck pagination after editing.

## Recovered Steps 01–30

Recovery used the existing scripts, CSVs, figures, and product systems, together with the original paper. Search matches are candidates, not approved providers or LCIA results. Earlier exports contain 454 candidate rows (including 193 low-voltage electricity markets) and 41 LCIA methods.

| Step | Work recovered | Evidence / status |
| --- | --- | --- |
| 01 | IPC connection test | Previously returned 25,412 processes; IPC available for this review |
| 02 | Background and method searches | `process_name_matches.csv`, `lcia_methods.csv` |
| 03 | US foreground inventory | `data/us_lci_baseline.csv`; literature inputs verified |
| 04 | Electricity/feed input plots | Legacy `fig01`, `fig02` |
| 05 | Background shortlist | `background_mapping_review.csv` |
| 06 | US electricity product system | Existing UUID reused; historical result had MJ/kWh error |
| 07 | Electricity system inspection | Displayed target unit alone did not establish calculation demand |
| 08 | Electricity contribution audit | Legacy arithmetic matched; Step 32 adds explicit units |
| 09 | Electricity-only shrimp estimates | Legacy output superseded by corrected factors |
| 10 | Feed C normalization | `data/feed_c_lci.csv`; fractions sum to 1 |
| 11 | Feed-provider search | `feed_provider_candidates.csv` |
| 12 | Broader searches for missing ingredients | `missing_feed_provider_candidates.csv` |
| 13 | Missing-provider review | Rendering, bicarbonate, rice/lecithin checks |
| 14 | 83%-mass feed ingredient process | Four ingredient inputs; fixed provider choices |
| 15 | Feed-process validation | Existing custom process structure |
| 16 | Feed product-system linking | Four foreground default providers linked |
| 17 | Partial ingredient GWP | 0.816535393 kg CO₂-eq/kg nominal feed; reproduced |
| 18 | Poultry proxy | Meat-and-bone-meal factor 0.026941154; imperfect proxy |
| 19 | Rice-bran/lecithin routes | `remaining_feed_routes.csv` |
| 20 | Missing-data register | `feed_c_missing_data_register.csv`; script retains original `.py.py` name |
| 21 | Rice-bran sensitivity | Hypothetical EF range; legacy scenario, not literature measurements |
| 22 | 100%-mass proxy hybrid | Ingredient GWP 0.912134347; not full method harmonization |
| 23 | Feed-processing/delivery inventory | `data/feed_c_processing_transport_lci.csv` |
| 24 | Processing-provider search | `feed_processing_provider_candidates.csv` |
| 25 | Provider shortlist refinement | `processing_provider_shortlist.csv` |
| 26 | Generic diesel-truck review | `generic_truck_candidates.csv` |
| 27 | Processing/delivery GWP | Electricity component corrected in new run |
| 28 | Feed hotspot aggregation | Legacy 1.199407 preserved; revised total 1.245165 |
| 29 | Indiana farming inventory | 0.921 kWh, 1.5 kg feed, 0.110 kg bicarbonate, 0.075 m³ water |
| 30 | Farm-provider validation | `farming_provider_mapping.csv`; matching units do not verify representativeness |

Legacy calculation call sites in Steps 06, 08, 17, 18, 22, and 27 now specify units and flow properties explicitly; Step 09's factor is corrected. These scripts were syntax-checked but were **not rerun**, because they may overwrite legacy exports or create systems. Use the versioned workflow above. Their pre-edit versions remain in the run's `legacy/scripts/` directory.

## Interpretation and assumptions

**Hotspots:** Indiana feed production/delivery contributes 75.95% of modeled GWP; farm electricity contributes 18.25%; bicarbonate contributes 5.80%. These shares apply only to the implemented inventory.

**Sensitivity:** ±25% FCR gives 1.992–2.926 kg CO₂-eq/kg shrimp. ±25% farm electricity or grid intensity changes the total by ±4.56%. Hypothetical grid factors span 0.05–0.80; the joint grid/FCR surface uses FCR 1–2. These are deterministic scenarios, not confidence intervals. Farm-only and farm-plus-feed-mill grid scenarios leave ingredient backgrounds unchanged.

**Counterfactual:** The common Feed C supply chain, including delivery distance, is held constant. The fixed-FCR contrast isolates +3.839430 kg CO₂-eq/kg from the electricity-demand difference. Changing FCR from 1.50 to 1.02 at Alabama electricity offsets 0.597679. A separate 1677 km Alabama delivery sensitivity gives 5.664837. None of these results demonstrate a causal advantage of biofloc technology or reconstruct actual Alabama Feed S production.

**Excluded / unresolved:** larval transport and rearing, infrastructure, farm GHGs, wastewater treatment, Alabama fertilizers, actual water supply, regional grid representativeness, and exact feed-proxy equivalence. Omitted flows are not assumed to be environmentally harmless. Post-farm stages are outside scope. Only GWP is quantified; eutrophication, water scarcity, biodiversity, and economics are not inferred from GWP.

## Sources and traceability

Primary foreground source: Al Eissa, A., Chen, P., Brown, P. B., & Huang, J.-Y. (2022). *Effects of feed formula and farming system on the environmental performance of shrimp production chain from a life cycle perspective*. Journal of Industrial Ecology, 26(6), 2006–2019. https://doi.org/10.1111/jiec.13370

The original PDF in `~/Downloads/` was read, and Table 2 was checked visually. The original paper's cradle-to-market results are not direct benchmarks for this narrower farm-gate screening. Sun et al. (2023) and the original Chinese-system handoff are separate datasets and are not mixed into this US baseline.

Detailed proxy provenance, source links, formulas, and interpretation limits are in [METHOD_NOTES.md](results/run_2026-11-21/METHOD_NOTES.md). The reviewed report contains APA references and an AI-use disclosure.
