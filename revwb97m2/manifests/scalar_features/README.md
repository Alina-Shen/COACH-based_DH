# Step 9 scalar double-hybrid features

The Step 9 stage consumes an independently validated Step 8 checkpoint and
does not rerun SCF. It records unscaled short-range HF at column 288, VV10 at
`b=10,C=0.01` at column 289, and total frozen-core canonical density-fitted
UMP2 at column 290. Same-spin and opposite-spin UMP2 terms are diagnostics;
only their total is fitted. It additionally records the frozen-parameter
COACH pure three-body D4-ATM energy at column 291. The four scalar coefficients
are fitted as part of the model; VV10, PT2, and D4-ATM are independently
bounded and have no sum equality.

The implementation is `revwb97m2/scalar_features.py`. The command-line runner
and independent validator are `revwb97m2/scripts/run_scalar_features.py` and
`revwb97m2/scripts/validate_scalar_features.py`. Publication is an atomic,
non-overwriting directory rename ending in `SCALAR_COMPLETE`; failures remain
in a hidden temporary directory with `FAILURE.json`.

Each artifact contains the actual selected `(64,154,166)` `3 x 96` matrix from
the parent identity grid assembled with the four scalars into a 292-vector.
The direct-energy identity is checked with deterministic test coefficients.
SR-HF, PT2, and geometry-only D4-ATM have zero semilocal-grid
differences for the recorded reasons.

The closed-shell `h2o_SW49` gateway and multi-electron open-shell gateway are
recorded by `step9_scalar_features_v1.yaml` and independently audited in this
directory's validation reports.
