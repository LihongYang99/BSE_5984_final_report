# Recovered Steps 01 to 30

Model development began with inventory preparation and provider searches, followed by provider checks, supply-chain linking, impact calculation, scenarios, and reporting. A provider supplies an input. A product system links a process to its upstream supply chain. LCI records physical inputs and outputs; LCIA converts them into indicators such as GWP.

Steps 01 to 30 document preparation and exploratory work. Several write legacy CSVs or can create database entities, so routine use of the reviewed results does not require rerunning them. Use the current workflow above for a new reviewed run.

The handoff was checked against the scripts, CSVs, figures, existing product systems, and original paper. Earlier searches returned 454 candidate rows, including 193 low-voltage electricity markets, and 41 LCIA methods. These matches still require provider review; they are not LCIA results.

| Step | Script | Purpose and meaning | Output / behavior |
| --- | --- | --- | --- |
| 01 | `01_test_connection.py` | Check whether Python can communicate with the active openLCA database before attempting any model work. | Process count and sample names in the terminal. |
| 02 | `02_find_processes.py` | Search broadly for electricity, feed-related materials, and available LCIA methods. A name match is only a candidate. | `outputs/process_name_matches.csv`; `outputs/lcia_methods.csv`. |
| 03 | `03_prepare_us_LCI.py` | Convert the literature electricity and feed quantities for Indiana and Alabama to the common basis of 1 kg live shrimp. | `data/us_lci_baseline.csv`. |
| 04 | `04_plot_us_LCI.py` | Show differences in physical electricity and feed demand before applying emission factors. | Legacy `fig01_US_electricity` and `fig02_US_feed` plots. |
| 05 | `05_validate_background.py` | Inspect shortlisted providers to check their reference products, units, and locations; search for bicarbonate. | `outputs/background_mapping_review.csv`; terminal review. |
| 06 | `06_calculate_electricity_gwp.py` | Build an upstream electricity product system and calculate its impacts per requested unit. The original omitted-unit result was mislabeled per kWh. | Creates a product system; writes `outputs/electricity_gwp_us.csv`. Current audit: Step 32. |
| 07 | `07_check_electricity_system.py` | Inspect the electricity system reference process, displayed target unit, process count, and links. This diagnoses model structure, not its GWP. | Terminal inspection; no database writes. |
| 08 | `08_audit_electricity_gwp.py` | Break electricity GWP into process contributions and check whether they sum to the total. A matching sum alone cannot detect the former unit error. | Legacy electricity contribution CSV and `fig03_electricity_gwp_audit.png`. |
| 09 | `09_electricity_only_shrimp.py` | Multiply farm electricity demand by the electricity factor to compare the electricity contribution alone. Feed and other farm inputs are excluded. | `outputs/electricity_only_shrimp_gwp.csv`; legacy `fig04` plots. |
| 10 | `10_prepare_feed_lci.py` | Translate Feed C into ingredient quantities per kg feed and per kg shrimp so the recipe can be modeled consistently. | `data/feed_c_lci.csv`; eight ingredient shares sum to 1. |
| 11 | `11_find_feed_providers.py` | Search for production/supply datasets for each Feed C ingredient and inspect the reference products and geography. | `outputs/feed_provider_candidates.csv`; candidates still require review. |
| 12 | `12_find_missing_feed_providers.py` | Broaden search terms for ingredients not found by the initial search, including rendering, rice processing, and soybean refining routes. | `outputs/missing_feed_provider_candidates.csv`. |
| 13 | `13_review_missing_providers.py` | Inspect selected rendering and bicarbonate processes and search product flows to assess possible substitutes. | Terminal provider/product review; no database writes. |
| 14 | `14_build_feed_screening.py` | Construct a custom feed process with fishmeal, soybean meal, wheat flour, and fish oil, covering 83% of Feed C mass. | Validation by default; `--write` creates the partial feed flow and process. |
| 15 | `15_verify_feed_model.py` | Check that the custom feed process has four inputs, one reference output, and assigned providers before linking/calculation. | Terminal structural checks; no LCIA result. |
| 16 | `16_create_feed_product_system.py` | Link the custom feed process to upstream suppliers and verify that its four inputs use the intended providers. | Reuses an existing system or creates one with `--write`; checks direct links. |
| 17 | `17_calculate_feed_gwp.py` | Calculate GWP for the 83%-mass ingredient model at 1 kg nominal feed. The missing 17% is not implicitly filled in. | `outputs/feed_c_partial_ipcc2021.csv` and `feed_c_partial_gwp_summary.csv`. |
| 18 | `18_test_poultry_proxy.py` | Evaluate meat-and-bone meal as an imperfect proxy for the 5% poultry by-product meal fraction. | `outputs/poultry_proxy_scenario.csv`; may create a missing background system. |
| 19 | `19_find_remaining_ingredient_routes.py` | Search alternative production routes and reference products for rice bran and soybean lecithin. | `outputs/remaining_feed_routes.csv`; no automatic acceptance of a substitute. |
| 20 | `20_prepare_missing_data_register.py` | Record unresolved ingredients, their mass shares, proposed data sources, and evidence gaps. Unknown impacts remain unknown. | `data/feed_c_missing_data_register.csv`. The script was named `20_prepare_missing_data_register.py.py` until November 24, 2026. |
| 21 | `21_rice_bran_sensitivity.py` | Test how hypothetical rice-bran emission factors change the earlier partial feed result. The tested factors are not measurements. | `outputs/rice_bran_sensitivity.csv`; legacy `fig05` plots. |
| 22 | `22_feed_proxy_100pct_scenario.py` | Add explicit proxies for the missing 17%, producing a 100%-mass ingredient screening model and a poultry-proxy alternative. | Feed V2 contribution/summary CSVs and legacy `fig06`; processing/delivery still excluded. |
| 23 | `23_prepare_feed_processing_lci.py` | Normalize feed-mill steam, electricity, water, land, and feed-delivery quantities to kg feed and kg shrimp. | `data/feed_c_processing_transport_lci.csv`. |
| 24 | `24_find_processing_providers.py` | Find candidate background datasets for feed-mill inputs and truck transport. | `outputs/feed_processing_provider_candidates.csv`. |
| 25 | `25_refine_processing_providers.py` | Narrow candidates using actual reference products, units, and geography; distinguish steam from heat and ordinary trucks from refrigerated transport. | `outputs/processing_provider_shortlist.csv`. |
| 26 | `26_select_truck_provider.py` | List generic diesel-truck candidates appropriate for feed delivery. Despite its name, the script exports candidates for review rather than making a final selection. | `outputs/generic_truck_candidates.csv`. |
| 27 | `27_calculate_feed_processing_gwp.py` | Calculate the additional GWP from feed-mill steam, electricity, water, and delivery, using validated products and units. | `outputs/feed_processing_transport_gwp.csv`; calculation requires `--calculate` and may create systems. |
| 28 | `28_plot_hotspot.py` | Combine ingredient, processing, and delivery results to identify which parts of Feed C supply contribute most GWP. | `outputs/feed_c_hotspot_analysis.csv`; legacy `fig07`. Reviewed feed total is 1.245165. |
| 29 | `29_prepare_indiana_lci.py` | Prepare the Indiana farm inventory per kg shrimp: feed, electricity, bicarbonate, water, and the reference shrimp output. | `data/indiana_biofloc_farming_lci.csv`. |
| 30 | `30_validate_farming_providers.py` | Check that farm-background candidates supply the intended products in the intended units. This does not establish that a proxy matches the actual farm. | `outputs/farming_provider_mapping.csv`. |

Steps 06, 08, 17, 18, 22, and 27 now specify calculation units and flow properties, and Step 09 uses the corrected factor. These scripts passed syntax checks but were not rerun because they may overwrite legacy exports or create systems. Their earlier versions are in the run’s `legacy/scripts/` directory. Use the versioned workflow above for calculations.

Return to the [project README](../README.md).
