# Inventory completeness review

Review date: November 23, 2026. This is a targeted evidence review, not a systematic review. The original November 21 calculation package is preserved.

## Corrections calculated from reported quantities

Al Eissa et al. (2022), Table 2, p. 2012 reports 140 and 62 t·km of larval airfreight per 1000 kg harvested shrimp in Indiana and Alabama. The modeled demands are therefore 0.140 and 0.062 t·km/kg shrimp. Section 2.2.2 describes Florida hatcheries; Table 2 records no truck demand for these two cases. Do not add the same route a second time as truck freight. Generic global aircraft freight is a background proxy; short- and medium-haul markets are evaluated separately because actual flight itineraries and aircraft are unknown.

Alabama fertilizer inputs are 0.3 kg triple superphosphate and 1.7 kg urea per 1000 kg shrimp, hence 0.0003 and 0.0017 kg product/kg shrimp. The selected ecoinvent reference flows are kg product, not kg N or P2O5. North American urea and rest-of-world triple superphosphate are supply proxies. The triple-superphosphate descriptor says RoW while its generic description says Global; this documentation inconsistency is retained in the exported provider JSON. Fertilizer application emissions are not included in the supply factors.

Six read-only process-target calculations use the same IPCC 2021 GWP100 excluding biogenic CO2 method as the reviewed model. Contributions reconcile to each total. The electricity process calculation reproduces the earlier explicit-unit product-system result. The nine saved product-system IDs are unchanged; no create, put, or delete calls are made. Full provider and reference-flow metadata are in the JSON files. These checks do not audit every upstream link or characterize the actual farms' suppliers.

## Hatchery production

The principal source omits hatchery production for lack of data and cites Cao et al. (2011). Cao's primary Table 2 reports hatchery GWP of 188 and 70.8 kg CO2-eq per tonne of harvested shrimp for intensive and semi-intensive Chinese systems, respectively: 0.188 and 0.0708 kg/kg shrimp. Larval transport is a separate row, so these hatchery entries do not duplicate the restored transport.

Both published values are applied to each US subtotal only as external benchmark scenarios. They are neither bounds on US uncertainty nor a validated US hatchery inventory. They differ in geography, production system, inventory year, survival and characterization. The project does not have a validated US hatchery factor or survival-normalized larvae requirement. A small share in a different LCA cannot establish that this omission is negligible here.

Source: Cao, L., Diana, J. S., Keoleian, G. A., & Lai, Q. (2011). Life cycle assessment of Chinese shrimp farming systems targeted for export and domestic sales. Environmental Science & Technology, 45(15), 6531–6538. https://doi.org/10.1021/es104058z

Primary full text retrieved through web access: https://marineagronomy.org/sites/default/files/Cao%20et%20al.%202011.%20Life%20Cycle%20Assessment%20of%20Chinese%20Shrimp%20Farming.pdf . A separate local download returned HTTP 406; no local PDF is claimed.

## Infrastructure and land

Al Eissa et al. (2022), Section 2.2.3, p. 2010 reports a preliminary infrastructure contribution below 0.1% in its assessed categories, with equipment lives of 7 to 20 years. This is a source-specific screening justification, not a verified upper bound for the present model. Equipment masses, replacements and allocation over output are not provided sufficiently to reconstruct that estimate here. Cao Table 2 reports 64.5 and 20.5 kg CO2-eq/t shrimp from grow-out infrastructure (0.0645 and 0.0205 kg/kg). These provide an external scale comparison, not replacement US data.

Area without occupation time or a documented transformation cannot be converted into a land-use or land-use-change GWP. The US cases do not justify importing the original paper's Vietnamese mangrove-deforestation factor. Land-use change already embedded in feed backgrounds must not be counted again.

## Direct farm GHGs and effluent

Heisterkamp et al. (2016) found N2O production in shrimp from a German indoor RAS. Its incubation result (4.3 ± 1.5 nmol per individual per hour) used freshly killed animals; it is not a farm-integrated emission factor. Animal size, exposure duration, biomass trajectory, microbial treatment, survival and gas transfer prevent direct scaling to annual US farm emissions. It establishes that a zero-emission assumption is unsupported, not a transferable emission rate for these cases.

Source: Heisterkamp, I. M., Schramm, A., de Beer, D., & Stief, P. (2016). Direct nitrous oxide emission from the aquacultured Pacific white shrimp (Litopenaeus vannamei). Applied and Environmental Microbiology, 82(13), 4028–4034. https://doi.org/10.1128/AEM.00396-16 . Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC4907211/ .

The source's total-N and P discharge rows are not N2O or CH4 measurements. Table 2 contains ranges and negative entries for some systems; no gas emission factor is inferred from those nutrient totals. Neither freshwater intake nor seawater volume equals wastewater volume requiring municipal treatment. Treatment route, discharge, sludge management, carbon and nitrogen balances remain unresolved. Additional pumping electricity must not be added without checking whether the reported farm electricity already includes it.

Total farm GWP remains covered subtotal + unresolved net burden U. An extra 5% of Indiana's covered subtotal is an illustrative materiality reference, not an ISO cut-off or proof of insignificance. The expanded ranking would reverse if U_Indiana − U_Alabama exceeded the difference between their covered subtotals. These equations expose what is unknown; they do not set U to zero or supply an uncertainty interval.

## Search and applicability record

Searches used web discovery followed by primary full-text checks on November 23, 2026:

- `shrimp aquaculture direct methane nitrous oxide emissions biofloc ponds life cycle assessment hatchery Cao 2011`
- `Al Eissa 2022 jiec 13370 shrimp supporting information larvae air freight`
- `site.ecoinvent.org triple superphosphate reference product kg P2O5 urea nitrogen`

Al Eissa's full paper was already supplied locally. Cao 2011 and Heisterkamp 2016 were assessed as the cited hatchery evidence and direct-emission evidence. Search results on coastal Chinese ponds, rice-shrimp systems, and WWF summaries were not adopted as US baseline factors. No exhaustive database coverage is claimed.

## Software and editorial assistance

The scientific-critical-thinking and literature-review skills guided the evidence review. Their software reference was verified against the current arXiv record: Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent Skills: A library of procedural knowledge for research agents. arXiv. https://doi.org/10.48550/arXiv.2609.00065 . This is a workflow credit, not evidence for shrimp inventory values.
