Scenario-Based Life Cycle Assessment of U.S. Shrimp Aquaculture: Energy Demand, Feed Efficiency, and Environmental Trade-offs

Lihong Yang | BSE 5984 Sustainable Agroecosystems
November 21, 2026

Abstract

This study develops a reproducible greenhouse-gas screening model for 1 kg of live-weight shrimp at the farm gate, using Indiana biofloc as the main case and an Alabama pond counterfactual. Literature inventories are combined with ecoinvent backgrounds and explicit feed proxies. An IPC unit audit corrected electricity from 0.135378 per MJ to 0.487361 kg CO₂-eq/kWh. The revised Indiana estimate is 2.459 kg CO₂-eq/kg shrimp. Feed supply is the largest contributor. Controlled comparisons separate electricity demand from feed conversion ratio (FCR), while sensitivity analysis identifies priorities for data collection. Results are conditional screening estimates, not measurements or complete comparative LCAs.

Goal, scope, and inventory

The research question is how electricity demand, grid intensity, and feed efficiency influence shrimp production GWP under a consistent accounting framework. Al Eissa et al. (2022) provide the foreground inventory. Their Indiana data were collected from a farm manager in 2019; Alabama data were drawn from an earlier pond study. These are literature-derived inputs in the present project. No new farm measurements, IoT records, or Virginia-specific data are required or claimed.

Table 1

Selected foreground inputs per kilogram of live-weight shrimp

Note. Inputs are from Al Eissa et al. (2022, Tables 1–2). The counterfactual replaces Alabama Feed S with the same Feed C supply chain used for Indiana; it does not reproduce the original Feed S system.

The intended boundary is cradle-to-farm-gate. The implemented inventory includes feed ingredients, processing and delivery, farm electricity, and Indiana bicarbonate. Farm water treatment is optional. Larval transport, farm infrastructure, wastewater treatment, and direct farm GHG emissions remain unmodeled. Post-farm packaging, ice, processing, and market transport are outside the selected boundary. Consequently, the reported total is a partial boundary screening estimate.


---


Background model and electricity verification

The workflow uses Python 3.12, openLCA 2.7 via IPC port 8080, and the supplied ecoinvent 3.11 Cut-off database. Nine existing product systems were recalculated read-only with explicit reference units and flow properties. The impact category is IPCC 2021 GWP100, total excluding biogenic CO₂. Root provider links and contribution sums were checked; every upstream exchange was not individually audited. No database entities were changed.

The previous electricity result of 0.135378 was reproducible, but its returned demand was 1 MJ. Explicitly requesting 1 kWh produced a demand of 3.6 MJ and 0.487361 kg CO₂-eq/kWh. The factor-of-3.6 difference explains the error. CalculationSetup exposes unit and flow-property fields (GreenDelta, n.d.). For context, the U.S. Energy Information Administration (EIA, n.d.) reports about 0.367 kg direct CO₂/kWh of U.S. generation in 2023. The corrected life-cycle, low-voltage factor is plausible in magnitude, but differences in boundaries and years prevent treating that benchmark as exact validation. The national market is a proxy for the farm grid.

Feed C represents 83% of ingredient mass with the existing background model and fills the remaining 17% with meat-and-bone meal, wheat bran, refined soybean oil, and a vitamin/mineral mixture proxy. The mixture factor is 1.33 kg CO₂-eq/kg delivered to a Norwegian feed mill (Winther et al., 2020, p. 51); its application to an undisclosed shrimp supplement blend is uncertain. Ingredient supply totals 0.912134 kg CO₂-eq/kg feed. Adding steam, electricity, water supply, and 1006 km delivery raises corrected Feed C GWP to 1.245165. The previous 1.199407 value is retained as superseded history.





Note. All contributions are per functional unit. The main case excludes farm water treatment; feed-mill water is included.

[Figure 1: fig08_indiana_hotspots.png]

Indiana totals 2.459 kg CO₂-eq/kg shrimp. Feed supply and delivery contribute 75.95%, farm electricity 18.25%, and bicarbonate 5.80%. Feed ingredients alone account for 55.64%. Applying a treated tap-water proxy to the reported 0.075 m³/kg adds 0.090, giving 2.549; the actual water source and treatment are unverified.


---


Electricity, grid, and FCR sensitivity

The main screening equation is G = F × C + E × g + B, where F is FCR, C is delivered Feed C GWP, E is farm electricity demand, g is the farm grid factor, and B is the bicarbonate contribution. C includes feed-mill electricity. One-at-a-time tests vary F, E, or g by ±25% while holding the other inputs fixed. These are deterministic scenarios, not confidence intervals or claims about achievable farm improvements.





Note. Panel A: farm electricity and farm-grid responses coincide because each scales the same E × g term. Panel B: the black point is the corrected baseline. Feed ingredient backgrounds remain fixed.

[Figure 2: fig09_sensitivity.png]

Varying FCR from 1.125 to 1.875 produces 1.992–2.926 kg CO₂-eq/kg shrimp, approximately ±19.0% around the baseline. A ±25% change in farm electricity or its grid factor changes the total by only ±4.56%. Thus, for this particular inventory, an equal proportional change in feed use has a larger modeled effect than farm electricity. This ranking depends on the inventory and does not establish the technical feasibility or cost of either intervention.

Broader grid scenarios span 0.05–0.80 kg CO₂-eq/kWh without assigning them to measured states or specific renewable technologies. Changing only the farm grid gives approximately 2.056–2.747 kg CO₂-eq/kg shrimp. Changing both the farm and feed-mill grids gives approximately 1.971–2.808. The latter is a supply-chain scenario because the mill and farm need not purchase the same electricity. A separate exported contour figure evaluates FCR 1–2 jointly with the grid range; it illustrates conditional combinations rather than probabilistic uncertainty.

Environmental trade-offs beyond GWP

Feed substitution may shift burdens between climate, nutrient discharge, land use, and marine resources. Al Eissa et al. (2022) found that replacing animal proteins with plant ingredients did not improve every impact category. The present model does not calculate eutrophication, water scarcity, biodiversity, or economic performance. Reported water volumes and land areas therefore remain inventory descriptors, not comparative impact scores. FCR improvements could alter survival, growth, feed composition, or aeration requirements; the one-at-a-time model holds those responses fixed.


---


Alabama counterfactual and fixed-FCR comparison

The comparison uses a common scope of feed production/delivery and farm electricity. Both cases share Feed C, processing, 1006 km delivery, and the grid factor. Bicarbonate, fertilizers, and other farm inputs are excluded from both subtotals. One contrast retains literature FCR and electricity; the other fixes FCR at 1.5 to isolate electricity demand. Neither reconstructs Alabama Feed S.





Note. These are counterfactual subtotals, not full farm footprints. The Indiana value differs from Figure 1 because bicarbonate is excluded to maintain the common scope.

[Figure 3: fig11_alabama_comparison.png]

The common-scope subtotal is 2.317 for Indiana and 5.558 kg CO₂-eq/kg shrimp for the Alabama counterfactual. Holding FCR at 1.5 gives 6.156 for Alabama electricity demand. Relative to Indiana, the isolated electricity effect is +3.839; the lower literature FCR offsets 0.598. These are arithmetic effects of prescribed inputs. Differences in scale, climate, operating practice, data collection, and biological performance prevent attributing the whole contrast to farming technology.

Under a shared farm-grid sensitivity, the two literature-FCR subtotals cross near 0.076 kg CO₂-eq/kWh, with feed-mill electricity held at baseline. This illustrates dependence of the ranking on assumptions. Using the source’s 1677 km Alabama delivery route instead of the standardized route raises its counterfactual subtotal to 5.665.

Limitations and conclusion

Limitations include incomplete farm coverage, mismatched geographies, allocation choices, and feed proxies. Complete feed mass representation does not ensure methodological harmonization. The low meat-and-bone-meal factor cannot establish poultry meal’s actual footprint. Published cradle-to-market totals are not directly comparable. Within these limits, feed efficiency is the dominant proportional sensitivity for Indiana, and the fixed-FCR contrast reveals the strong effect of the reported Alabama electricity demand. Better farm energy records, actual feed specifications, and regional electricity data would strengthen the next assessment.

AI disclosure. OpenAI Codex assisted with code review, unit debugging, literature extraction, scenario calculations, figures, and report drafting. Calculations were executed and checked against saved outputs and cited sources. No primary measurements were generated.


---


References

Al Eissa, A., Chen, P., Brown, P. B., & Huang, J.-Y. (2022). Effects of feed formula and farming system on the environmental performance of shrimp production chain from a life cycle perspective. Journal of Industrial Ecology, 26(6), 2006–2019. https://doi.org/10.1111/jiec.13370

GreenDelta. (n.d.). CalculationSetup. openLCA schema. Retrieved November 21, 2026, from https://greendelta.github.io/olca-schema/classes/CalculationSetup.html

U.S. Energy Information Administration. (n.d.). How much carbon dioxide is produced per kilowatthour of U.S. electricity generation? Retrieved November 21, 2026, from https://www.eia.gov/tools/faqs/faq.php?id=74&t=11

Winther, U., Hognes, E. S., Jafarzadeh, S., & Ziegler, F. (2020). Greenhouse gas emissions of Norwegian seafood products in 2017 (Report No. 2019:01505). SINTEF Ocean. https://www.sintef.no/contentassets/0ec2594f7dea45b8b1dec0c44a0133b4/report-carbon-footprint-norwegian-seafood-products-2017_final_040620.pdf