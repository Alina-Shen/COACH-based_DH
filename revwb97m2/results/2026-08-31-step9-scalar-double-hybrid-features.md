# Step 9: scalar double-hybrid features

## Outcome

Step 9 is complete. The checkpoint-only stage evaluates unscaled SR-HF,
fixed-density VV10, and frozen-core canonical DF-UMP2 without rerunning a
validated omegaB97M-V parent. Both the recovered closed-shell `h2o_SW49`
gateway and the real multi-electron open-shell `12_NH2rad_HNBrBDE18` gateway
passed independent validation.

## Implementation

- `revwb97m2/scalar_features.py` independently validates every parent
  checkpoint and its immutable input, basis-overlay, specification, and
  artifact hashes before calculation.
- Column 288 is the unscaled short-range HF exchange. Full unscaled LR-HF is
  retained in `E_fixed` with nuclear repulsion, one-electron, and Coulomb
  terms.
- Column 289 is VV10 at `b=10,C=0.01`, evaluated once on the fixed parent
  total density and frozen nonlocal grid.
- Column 290 is total frozen-core canonical DF-UMP2 using the explicit Step-6
  auxiliary definition. Same-spin and opposite-spin components, frozen-core
  count, and the exact component-sum residual are diagnostics.
- The selected `(64,154,166)` `3 x 96` identity-grid features are assembled
  with the scalars into a named 291-vector. Two deterministic coefficient
  vectors prove the direct named-channel energy equals
  `E_fixed + feature_vector dot coefficients` within `1e-12 Eh`.
- SR-HF, once-evaluated VV10, and PT2 explicitly store zero semilocal-grid
  differences with reasons.
- Publication refuses overwrites, uses a hidden temporary directory and
  atomic rename, writes hashes and `SCALAR_COMPLETE`, and leaves failures with
  `FAILURE.json`. Timings, maximum RSS, scratch use, software, host, source,
  and authority hashes are recorded.

## Closed-shell gateway

The validated specification-v3 `h2o_SW49` parent was consumed without SCF.
The scalar artifact is at
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/scalar/gateway/h2o_SW49`.

- SR-HF: `-7.336839258204929 Eh`.
- VV10: `0.020787561237750714 Eh` on 12,936 SG-1 points.
- total DF-UMP2: `-0.3334012925516243 Eh`;
  SS `-0.07968300790900397 Eh`, OS `-0.25371828464262036 Eh`.
- The total differs from the accepted earlier DF-UMP2 result by about
  `1.4e-15 Eh`; `E_PT2-E_SS-E_OS` is exactly zero.
- Both direct-energy identities have zero observed difference.
- Scalar-stage wall time: `51.71 s`; end maximum RSS: `275.62 MiB`;
  observed scratch: zero bytes because the DF tensors remained in memory.

## Open-shell gateway

`12_NH2rad_HNBrBDE18` is a locked GSCDB137 model-selection species: neutral
doublet NH2, 9 electrons, 129 orbital AOs, and 287 auxiliary AOs. Slurm job
`25426183` ran on `mhg` (`account=mhg`, `qos=normal`) with 8 CPUs and 40 GB.
It completed in `00:01:26`, used `08:04.236` aggregate CPU, and peaked at
`1200080 KiB` RSS.

- Parent energy: `-55.87821037601809 Eh`; reconstruction residual
  `7.105427357601002e-15 Eh`; `<S^2>=0.7532338971525303`.
- Stability: `unavailable` because this species was not selected for the
  separate diagnostic; no alternative orbitals were adopted.
- SR-HF: `-5.860756549779014 Eh`.
- VV10: `0.018654599079494568 Eh` on 12,856 SG-1 points.
- total DF-UMP2: `-0.23521668710122212 Eh`;
  SS `-0.05032575501791932 Eh`, OS `-0.18489093208330282 Eh`.
- `E_PT2-E_SS-E_OS` is exactly zero, so the case exercises nonzero total,
  same-spin, and opposite-spin correlation.
- The largest direct-energy identity residual is
  `7.105427357601002e-15 Eh`, below the `1e-12 Eh` tolerance.
- The publishing process proved bitwise checkpoint density/feature identity.
  An independent process reproduced density within `2.78e-17` and features
  within `4.44e-16`, below the strict `1e-14` and `1e-12` tolerances.
- Scalar-only wall time was `5.95 s`; end maximum RSS `243.00 MiB`; observed
  scratch zero bytes.

## Stability specification amendment

Specification v3 is archived byte-for-byte. Version 4 changes only stability:
validated checkpoints are authoritative independently of the incomplete,
expensive PySCF NLC-omitting response. Stability is a separate timed
diagnostic for gateway/model-critical or flagged species and records
`stable`, `unstable`, `indeterminate`, or `unavailable` without automatic
orbital replacement. All other scientific choices are unchanged.

## Validation

- Four scalar-layout and direct-energy unit tests pass.
- Python compilation and shell syntax checks pass.
- The version-4 scientific-specification validator passes every check.
- Both scalar gateway reports pass all 14 top-level checks.
- The open-shell parent report passes all 15 checks, including the recorded
  within-process bitwise proof and independent cross-process numerical reload.
- No Q-Chem orbitals or `qarchive.h5` were read.
