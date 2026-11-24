# Screening estimates for unresolved burdens: evidence notes

Review date: November 24, 2026. Step 43 (`scripts/43_quantify_unresolved_burdens.py`) turns the burdens drawn as "not yet quantified" in Figure C1 into low, central and high screening values. They are deterministic ranges built from literature factors and stated assumptions. They are not confidence intervals, they are not added to the reviewed subtotals, and they do not replace farm measurements.

GWP100 values follow IPCC AR6 as applied by the IPCC 2021 GWP100 method in openLCA: biogenic CH4 27.0 and N2O 273. Sources that used other metrics were recalculated with these values.

## Sources checked against the primary text

| Value used | Source and location | How it was checked |
| --- | --- | --- |
| Default aquaculture N2O factor 0.00169 kg N2O-N per kg produced, 95% CI 0 to 0.0038 | Kennedy et al. (2014), IPCC Wetlands Supplement, Ch. 4, Table 4.15, p. 4.35 | Text extracted from the published chapter PDF |
| Derivation: product N 2.84%, 1.8 ± 0.7% of N released to water emitted as N2O-N | Kennedy et al. (2014), Annex 4A.5, p. 4.41 | Same PDF. The chapter states the factor was developed for fish and that wider use adds uncertainty |
| Aerated-pond CH4 4.50 ± 1.73 mg m-2 h-1 (AP I and AP II), N2O 11.72 and 15.96 µg m-2 h-1 | Yang et al. (2023), Section 3.3, accepted manuscript | Text extracted from the Swansea repository PDF |
| Yang ponds: salinity about 4 ppt, single crop May to November, aerated yield 6,800 kg ha-1, feed about 9,044 kg ha-1 | Yang et al. (2023), Sections 2.2, 4.1 and 4.2 | Same PDF. Yang used sustained GWP 45 for CH4 and 270 for N2O; values were recalculated here |
| Gulf Shores pond trials: 16 ponds of 0.1 ha, 38 shrimp m-2, 13-week production trial, survival 58.5 to 63.9 | Davis et al. (2018), Responsible Seafood Advocate | Web page read in full |
| Claude Peteet Mariculture Center: 35 ponds and a pump station built in 1973, HDPE liners in 1986, Auburn shrimp research in about half the ponds, water from the Intracoastal Waterway or a Gulf pipeline | Alabama Gulf Seafood (2020) | Web page read in full |
| EF5 leaching and runoff 0.0075 kg N2O-N per kg N, range 0.0005 to 0.025 | De Klein et al. (2006), IPCC Vol. 4, Ch. 11, Table 11.3, p. 11.24 | Text extracted from the chapter PDF |
| Urea emission factor 0.20 kg C per kg urea | De Klein et al. (2006), IPCC Vol. 4, Ch. 11, Section 11.4, pp. 11.32 and 11.34 | Same PDF |
| Hatchery 0.0708 and 0.188, grow-out infrastructure 0.0205 and 0.0645 kg CO2-eq per kg shrimp | Cao et al. (2011), Table 2 | Checked on November 23 (see the completeness evidence review) |
| Indiana infrastructure below 0.1% of the source total, source total 4,025 kg CO2-eq per t with Feed C | Al Eissa et al. (2022), Section 2.2.3 and Table 3 | Local copy of the paper |
| Indiana postlarvae raised for 5 months to 20 g, electricity for heating and aeration; Alabama data from 16 outdoor 0.1-ha ponds | Al Eissa et al. (2022), Sections 2.2.2 and 2.2.3 | Local copy of the paper |

## Assumptions

- Feed C crude protein is 35 to 40% (central 36%). The source does not report it.
- Shrimp N content equals the IPCC fish default of 2.84% of live weight.
- Alabama grow-out lasts 13 weeks, as in the Gulf Shores trials. The high CH4 value instead scales emissions by feed applied, which is independent of season length.
- Pond fluxes from unlined estuarine ponds in subtropical China transfer to HDPE-lined Gulf Shores ponds. Liners probably reduce sediment CH4, so the CH4 range is more likely to overstate than understate.
- Pond filling lifts 1.456 m3 per kg shrimp by 3 to 10 m at 50 to 70% pump efficiency. Some of this may already be in the reported farm electricity.
- No land conversion falls within a 20-year amortization period. For Indiana this is an assumption because the building history is not documented.

## Not quantified

Indiana tank CH4 and sludge fate. The source mentions landfilling separated sludge as an option for phosphorus control but gives no sludge mass or disposal route. With the screening values, the ranking of the expanded subtotals would reverse only if this burden exceeded about 2.47 kg CO2-eq per kg shrimp.

## Sources that could not be used

Naegel (2010) reports hatchery electricity and propane use in Baja California Sur. Its repository server reset the connection, and search summaries give a postlarvae count that conflicts with the same hatchery's other publication by a factor of 100. No value from it is used.

No measured N2O conversion for biofloc shrimp tanks was found. The Indiana range therefore rests on the IPCC wastewater-plant analogy, which suits aerated biofloc better than ponds but remains unvalidated.

## References

- Alabama Gulf Seafood. (2020, May 21). Claude Peteet Mariculture Center in Gulf Shores celebrates 50 years of conservation. https://aqua.alabama.gov/articles/story/claude-peteet-mariculture-center-50-years.html
- Davis, A., Ullman, C., Rhodes, M., Novriadi, R., & Swanepoel, A. (2018, April 9). Automated feeding systems in pond production of Pacific white shrimp. Responsible Seafood Advocate. https://www.globalseafood.org/advocate/automated-feeding-systems-in-pond-production-of-pacific-white-shrimp/
- De Klein, C., Novoa, R. S. A., Ogle, S., Smith, K. A., Rochette, P., Wirth, T. C., McConkey, B. G., Mosier, A., & Rypdal, K. (2006). Chapter 11: N2O emissions from managed soils, and CO2 emissions from lime and urea application. In H. S. Eggleston, L. Buendia, K. Miwa, T. Ngara, & K. Tanabe (Eds.), 2006 IPCC guidelines for national greenhouse gas inventories (Vol. 4). IGES. https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/4_Volume4/V4_11_Ch11_N2O&CO2.pdf
- Kennedy, H., Alongi, D. M., Karim, A., Chen, G., Chmura, G. L., Crooks, S., Kairo, J. G., Liao, B., & Lin, G. (2014). Chapter 4: Coastal wetlands. In T. Hiraishi, T. Krug, K. Tanabe, N. Srivastava, J. Baasansuren, M. Fukuda, & T. G. Troxler (Eds.), 2013 supplement to the 2006 IPCC guidelines for national greenhouse gas inventories: Wetlands. IPCC. https://www.ipcc-nggip.iges.or.jp/public/wetlands/pdf/Wetlands_separate_files/WS_Chp4_Coastal_Wetlands.pdf
- Yang, P., Tang, K. W., Yang, H., Tong, C., Zhang, L., Lai, D. Y. F., Hong, Y., Tan, L., Zhu, W., & Tang, C. (2023). Contrasting effects of aeration on methane (CH4) and nitrous oxide (N2O) emissions from subtropical aquaculture ponds and implications for global warming mitigation. Journal of Hydrology, 617, Article 128876. https://doi.org/10.1016/j.jhydrol.2022.128876
