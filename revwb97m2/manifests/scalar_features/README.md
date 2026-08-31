# Step 9 scalar double-hybrid features

The Step 9 stage consumes an independently validated Step 8 checkpoint and
does not rerun SCF. It records unscaled short-range HF at column 288, VV10 at
`b=10,C=0.01` at column 289, and total frozen-core canonical density-fitted
UMP2 at column 290. Same-spin and opposite-spin UMP2 terms are diagnostics;
only their total is fitted.

The implementation is `revwb97m2/scalar_features.py`. The command-line runner
and independent validator are `revwb97m2/scripts/run_scalar_features.py` and
`revwb97m2/scripts/validate_scalar_features.py`. Publication is an atomic,
non-overwriting directory rename ending in `SCALAR_COMPLETE`; failures remain
in a hidden temporary directory with `FAILURE.json`.

Each artifact contains the actual selected `(64,154,166)` `3 x 96` matrix from
the parent identity grid assembled with the three scalars into a 291-vector.
The direct-energy identity is checked with deterministic test coefficients.
SR-HF, once-evaluated frozen-grid VV10, and PT2 have zero semilocal-grid
differences for the recorded reasons.

The closed-shell `h2o_SW49` gateway and multi-electron open-shell gateway are
recorded by `step9_scalar_features_v1.yaml` and independently audited in this
directory's validation reports.
