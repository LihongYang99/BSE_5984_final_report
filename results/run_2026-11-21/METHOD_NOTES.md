# Methods and evidence review — 21 November 2026

## Source verification

Read the locally supplied Al Eissa et al. (2022) full paper, DOI https://doi.org/10.1111/jiec.13370, especially Tables 1–2 (pp. 2009, 2012) and Sections 2.2.1–2.2.3. The Indiana inventory comes from the source authors' 2019 farm-manager data. It is **secondary, literature-derived data for this project**, not new measurements. Alabama is compiled in that paper from Reis et al. (2020). No IoT or Virginia-specific data are used.

Feed C fractions: fishmeal .30, poultry by-product meal .05, soybean meal .20, wheat flour .30, rice bran .05, fish oil .03, soybean lecithin .03, supplements .04. Table 1 labels ingredient origins as assumptions. The original Alabama feed is Feed S, not Feed C. No claim is made to reproduce its original production chain.

The current working provider choices supersede the earlier candidate mapping in `data/feed_provider_mapping_review.csv`: the actual fishmeal/fish-oil UUIDs are those in the Step 14 model, not the earlier review candidates. The original 83% feed model was recalculated at exactly 1 kg; its 0.816535393 result was unchanged. The remaining 17% uses meat-and-bone meal, wheat bran, refined soybean oil, and a literature premix factor. All are proxies, not exact ingredient matches. Complete mass representation is not equivalent to complete or harmonized LCA coverage.

Winther et al. (2020), *Greenhouse gas emissions of Norwegian seafood products in 2017*, report 2019:01505, p. 51, explicitly reports 1.33 kg CO2e/kg vitamin/mineral mix delivered to a Norwegian feed mill. The primary report was checked at https://www.sintef.no/contentassets/0ec2594f7dea45b8b1dec0c44a0133b4/report-carbon-footprint-norwegian-seafood-products-2017_final_040620.pdf . Applying it to the full undisclosed 4% shrimp supplement blend is an inherited proxy assumption. Its LCIA/allocation/geography are not fully harmonized with ecoinvent/IPCC 2021.

## Electricity error and correction

The old CalculationSetup specified amount=1 without unit/flow_property. The actual returned demand is 1 MJ, despite the product-system display target being 1 kWh. An explicit kWh calculation returns demand=3.6 MJ and GWP=0.4873610116670967. Thus 0.1353780587964153 is kg CO2-eq/MJ and must not be used as kg CO2-eq/kWh. This is a demonstrated unit correction, not a new grid scenario. See `../review_2026-11-21/electricity_unit_test.json` and `background_factors.csv`.

The EIA historical 2023 national generation benchmark is 0.81 lb CO2/kWh, approximately 0.367 kg CO2/kWh: https://www.eia.gov/tools/faqs/faq.php?id=74&t=11 . It is direct generation CO2, whereas the model is delivered low-voltage life-cycle CO2-equivalent. Different years, geography and boundaries prevent treating the benchmark as a replacement factor or exact validation target. The corrected factor has a plausible order of magnitude; it is not verified as an Indiana-specific grid factor. API schema: https://greendelta.github.io/olca-schema/classes/CalculationSetup.html .

Nine existing product systems were recalculated read-only, with explicit units and flow properties. Root default-provider links and contribution sums passed. All non-electricity factors remained unchanged. The electricity system contains 17,182 processes and 194,947 links. These checks do not certify every upstream exchange or characterization mapping. No Process, Flow, ProductSystem or method was created, edited or deleted. IPC does not establish the active database name here; because all operations were read-only, original ecoinvent was not changed.

## Scope and equations

Functional unit: 1 kg live-weight shrimp at farm gate. Intended boundary: cradle-to-farm-gate. Implemented result: an incomplete, proxy-assisted GWP screening inventory. Post-farm processing, packaging, ice and market transport are outside the selected boundary. Larval transport, larval rearing, farm infrastructure, direct farm GHGs, wastewater treatment and some farm inputs remain outside the implemented inventory. Known excluded flows are recorded in `source_inventory_verified.csv`, not assumed to have zero impact. Water volume is not a water-scarcity result. N/P discharges are not interchangeable with N2O/CO2 emissions; no GWP factor was invented for them.

Indiana: G = FCR × Feed_C + electricity × grid + 0.110 × bicarbonate_EF (+ optional 75 × tap_water_EF).
Feed_C = ingredients + .320 × steam_EF + .130 × grid_mill + (2000/1500) × tap_water_EF + 1.006 × truck_EF.
The feed-mill water input uses exact normalization (2 m3 / 1500 kg feed × 1000 kg/m3); the legacy 1.333333 rounding changed only the last decimals.

## Approved counterfactual comparison

User approved a common Feed C supply chain and explicitly requested a fixed-FCR electricity contrast. Both cases use the same composition, processing quantities per kg feed, grid factor and 1006 km delivery distance. Retain literature farm electricity .921 vs 8.799 and FCR 1.5 vs 1.02. The common scope includes feed supply/delivery and farm electricity only; Indiana bicarbonate is removed **from this comparison only**. Alabama fertilizer, larvae and other omitted inputs are not represented. A separate delivery-distance sensitivity uses 1677 km from the source and is not the main comparison. Table 2 transport totals are rounded; the sensitivity uses the stated route distance.

The third case keeps FCR=1.5 and changes only farm electricity to 8.799. The electricity contrast is +3.839430 kg CO2-eq/kg; changing only FCR from 1.5 to 1.02 at Alabama electricity is −0.597679. This is algebraic attribution within a prescribed model, not causal evidence about biofloc versus pond technology. Feed changes could affect growth, survival or electricity needs; those responses are not predicted.

## Sensitivity design

One-at-a-time multipliers .75–1.25 for electricity use, farm grid and FCR, holding other parameters fixed. FCR range 1.125–1.875. Broader hypothetical farm-grid range .05–.80 kg CO2-eq/kWh; no grid scenario is labeled as a measured state or specific renewable technology. Joint grid/FCR surface uses FCR 1–2. Separate farm+mill grid scenario changes only those explicit electricity inputs; ingredient/background supply chains stay fixed. These are deterministic scenarios, not confidence intervals or Monte Carlo uncertainty distributions.

## Remaining scientific limitations

The 0.026941 kg CO2-eq/kg meat-and-bone-meal proxy is especially sensitive to dataset allocation and by-product treatment; it is not a validated poultry-meal factor. The legacy Campos sensitivity remains available but was not adopted as baseline. Background geography and inventory years differ; neither aggregate method conformity nor a farm technology advantage is established. GWP does not quantify eutrophication, water scarcity, biodiversity, marine resource use, or profitability. The paper's cradle-to-market totals cannot validate this narrower screening total directly.
