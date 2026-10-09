# Review before sharing

Run the analysis and tests, then open the executed notebook and results.

Explain in your own words:

1. What is actually measured, and who collected the observations?
2. What units are used and where do conversions occur?
3. Why was this method chosen, and what is the comparison or baseline?
4. Which output supports the main finding?
5. What can the analysis not establish?
6. What additional data or validation would improve the project?

Supported CV sentence: Audited real EM27/SUN reference retrievals, reconstructed dry-air gas fractions and implemented sequential XAIR quality screening with controlled anomaly tests.

Main scope constraint: Only 26 reference rows across two days. These are precomputed retrievals, not measurements collected here. Synthetic anomalies are identified separately. The Jinja thresholds are a methodological demonstration and require site-specific validation.

## Result you should be able to explain

All 26 real reference records pass the demonstrated XAIR screening. One deliberately injected 0.005 XAIR anomaly is rejected in a separate synthetic experiment. The simple CO2/O2 ratio differs from reported XCO2 by up to **3.877 ppm**; including the documented postprocessing corrections reduces the maximum discrepancy to **0.00130 ppm**. This is a consistency audit using rounded reference fields and supplied XH2O, not an independent spectral retrieval.
