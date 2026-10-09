# Data provenance

Real EM27/SUN SN039 reference retrieval output from Sodankylä, Finland, 8–9 June 2017.
26 rows, supplied with PROFFASTpylot, not collected by Miranda Finjap.
Source: https://gitlab.eudat.eu/coccon-kit/proffastpylot
Pinned commit: c1c6333e246b0bcac15a00b2009c2ff83a5010fc
File: example/Reference_Output_Example_Sodankyla.csv
Upstream authors: Benedikt Herkommer, Lena Feld, Darko Dubravica, Moritz Makowski.
The upstream repository is GPLv3; its included CSV is retained with the full GPL
license in THIRD_PARTY_GPL_LICENSE. This repository uses GPLv3 to preserve upstream licensing.
Current software documentation: https://www.coccon.kit.edu/69.php

Units: XCO2 ppm; XCH4 and XCO ppm; XAIR dimensionless; O2, CO2, CH4 and CO
are molecular column amounts. Gas dry-air fractions are gas_column/O2_column ×0.2095.
Retrieval output is already Level-2-like column information; this project does not
claim to have collected measurements or rerun the raw interferogram retrieval.
Published XAIR screening thresholds are adapted from Humpage et al. (2024),
https://doi.org/10.5194/amt-17-5679-2024. They were developed for Jinja and are
demonstrated here, not independently validated for Sodankylä.

## Postprocessing audit

The elementary gas/O2 ×0.2095 ratio does not reproduce the reported columns:
PROFFAST applies air-mass-independent (AICF), angular (ADCF), water-vapour and
time-dependent oxygen-fraction corrections. `corrected_fraction` reproduces
these equations using the v2.4.1 source and the pinned template coefficients
from `prfpylot/templates/template_invers26.inp`. It uses supplied XH2O rather
than independently retrieving water. This is a postprocessing consistency audit,
not a fresh inversion from spectra. Coefficients are version/dataset specific.
Equation source: KIT PROFFASTv2.4.1, `source/invers/invers26.f90`,
`postprocessing` subroutine; https://www.coccon.kit.edu/69.php
