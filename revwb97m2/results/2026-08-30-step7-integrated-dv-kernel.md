# Step 7: project-owned selected integratedDV kernel

## Outcome

Step 7 is complete. `revwb97m2/integrated_dv.py` now constructs the 288
semilocal fitting features from fixed omegaB97M-V spin densities using the
COACH integratedDV protocol. It does not reproduce or embed the final COACH
functional: no published COACH coefficients are present, and the features are
intended for fitting a new omegaB97M(2)-form double hybrid.

## Frozen feature definition

The kernel returns a `3 x 96` matrix instead of carrying all 180 candidate
rows. The three rows are already frozen by scientific specification v3:

- row 64: range-separated exchange with nonuniform scaling, monomial `u_x`
  and Legendre `beta_f`;
- row 154: SCAN-alpha=1 same-spin correlation with self-correlation correction
  `2 beta`, monomial `u_ss` and Legendre `beta_f`;
- row 166: SCAN-alpha=1 opposite-spin correlation, Legendre `u_os` and
  Legendre `w`.

The nonlinear values are `omega=0.3`, `gamma_x=0.004`, `gamma_ss=0.01`, and
`gamma_os=0.006`. Flattening the selected matrix gives semilocal columns
`0:288`; SR-HF, VV10, and total RI-MP2 later supply columns 288, 289, and 290.

## Implementation details

- Implemented project-owned polynomial recurrences and 8-by-12 tensor-product
  ordering, SCAN-alpha=1 correlation bases, short-range exchange attenuation,
  nonuniform exchange scaling, same-spin self-correlation correction, and
  opposite-spin subtraction.
- Added strict shape/finite checks, safe zero-density masks, alpha/beta spin
  symmetry, block accumulation, an unpruned PySCF grid builder, and conversion
  from PySCF's half-tau convention to the COACH/Q-Chem tau convention.
- Added serializable kernel metadata that records the scientific target,
  nonlinear parameters, selected row semantics, output shape, and the fact
  that published COACH coefficients are not used.
- Kept `coach/` unchanged. The accepted legacy smoke remains unchanged as a
  plumbing fixture and continues to document its row-153/`gamma_ss=0.2`
  limitations.

## Independent validation

`revwb97m2/scripts/validate_integrated_dv.py` passed every check and wrote
`revwb97m2/manifests/integrated_dv/validation.json`. Tests cover:

- independent decoding of rows `(64,154,166)`;
- exact frozen-parameter and fit-target metadata;
- finite `3 x 96` output and zero-density behavior;
- a real PySCF MGGA-density/grid adapter test on a 504-point He/STO-3G grid;
- alpha/beta exchange symmetry and grid-block partition invariance;
- independent one-point monomial/Legendre coordinate identities;
- agreement with maintained upstream rows 64 and 166, whose nonlinear values
  already match the frozen specification, plus exact row-154 agreement when
  the project kernel is deliberately evaluated at the upstream legacy gamma;
- a required negative regression showing that upstream `gamma_ss=0.2`
  changes row 154. The synthetic test's maximum absolute same-spin feature
  difference is `0.007768994740725371`.

The validator intentionally tests features rather than fitting or adopting the
published COACH coefficient vector. The next ordered gate is Step 8: a
manifest-driven PySCF parent-SCF driver with checkpoint/reload identity.
