# Step 9 scalar double-hybrid features

The production Step 9 stage consumes an isolated, hash-verified copy of the
authoritative Q-Chem omegaB97M-V `qarchive.h5` and never optimizes orbitals. It
records unscaled short-range HF at column 288, VV10 at
`b=10,C=0.01` at column 289, and total frozen-core canonical density-fitted
UMP2 at column 290. Same-spin and opposite-spin UMP2 terms are diagnostics;
only their total is fitted. It additionally records the frozen-parameter
COACH pure three-body D4-ATM energy at column 291. The four scalar coefficients
are fitted as part of the model; VV10, PT2, and D4-ATM are independently
bounded and have no sum equality.

The production implementation is `revwb97m2/qchem_scalar_features.py`; its
preparer, publisher, and aggregate validator are
`scripts/prepare_step9_qchem_gateway.py`, `scripts/publish_step9_qchem_scalar.py`,
and `scripts/validate_step9_qchem_gateway.py`. Publication is an atomic,
non-overwriting directory rename ending in `SCALAR_COMPLETE`; failures remain
in a hidden temporary directory with `FAILURE.json`.

SR-HF/VV10 and RI-MP2 are evaluated in two non-SCF Q-Chem jobs that read the
same copied archive. The first isolates unscaled erfc SR-HF and unit-scaled
VV10. The second uses Q-Chem's native wB97M(2)/RIMP2 path so the Fock operator
and orbital energies remain those of the imported wB97M-V parent. Q-Chem
prints the MP2 spin components after the method's common `0.34096` factor; the
publisher divides that factor back out, fits same-spin plus opposite-spin
canonical doubles, and excludes/records non-Brillouin singles. D4-ATM is
evaluated independently from the authoritative geometry and charge.

Each artifact contains the actual selected `(64,154,166)` `3 x 96` matrix from
the parent identity grid assembled with the four scalars into a 292-vector.
The direct-energy identity is checked with deterministic test coefficients.
SR-HF, PT2, and geometry-only D4-ATM have zero semilocal-grid
differences for the recorded reasons.

The old `scalar_features.py` checkpoint route and
`step9_scalar_features_v1.yaml` remain validated PySCF fallback evidence. The
production closed-shell `h2o_SW49` and open-shell `12_NH2rad_HNBrBDE18`
gateways are frozen by `step9_qchem_same_archive_v3.yaml` and audited by
`step9_qchem_validation_v3.json`.
