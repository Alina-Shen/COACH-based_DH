# Frozen scientific specification, version 3

The authoritative machine-readable specification is
[`../configs/scientific_spec.yaml`](../configs/scientific_spec.yaml). Version 2
is preserved byte-for-byte at
[`../configs/archive/scientific_spec.v2.yaml`](../configs/archive/scientific_spec.v2.yaml).

## Version-3 engine decision

Each species receives one self-consistent PySCF unrestricted omegaB97M-V
calculation. Its checkpoint and density are fixed for integratedDV, SR-HF,
VV10, frozen-core RI-MP2, reaction assembly, and all coefficient searches. The
fitted double hybrid does not update or reoptimize the parent orbitals.

The verified immutable GSCDB137/Q-Chem input publication remains the metadata
source for geometry, charge, multiplicity, orbital basis, auxiliary basis, and
ECP definitions. Q-Chem orbital files are not read by the production workflow.
Generated basis, auxiliary-basis, and ECP definitions must be translated to
PySCF and validated before the corresponding species can run.

The old route is preserved under `coach/qchem_orbital_route` and
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/qchem_orbital_route`.

## RI-MP2 decision gate

The matched `h2o_SW49` comparison is recorded in
[`../results/2026-08-29-pyscf-qchem-rimp2-h2o-sw49.json`](../results/2026-08-29-pyscf-qchem-rimp2-h2o-sw49.json).

- PySCF/Q-Chem parent-energy difference: `-1.2963e-8` hartree.
- PySCF/Q-Chem scaled opposite-spin RIMP2 difference: `-1.1157e-8`
  hartree.
- PySCF density-fitted versus conventional UMP2 total-correlation difference:
  `1.1609e-5` hartree, or `0.00728` kcal/mol.

The first two pass the existing COACH cross-engine tolerances. The last is
below the specification's already-defined `0.015` kcal/mol numerical
threshold. Total PT2 is the fitted feature; same- and opposite-spin values are
stored as diagnostics only. The initial stricter diagnostic report is retained
beside the accepted report rather than discarded.

## Frozen 291-feature energy model

The fixed energy is

\[
E_{\mathrm{fixed}} = E_{\mathrm{nuc}} + E_{\mathrm{one}} + E_J
                   + E_x^{\mathrm{LR-HF}}.
\]

The fitted vector remains exactly 291 columns:

- columns `0:96`: semilocal short-range exchange;
- columns `96:192`: semilocal same-spin correlation;
- columns `192:288`: semilocal opposite-spin correlation;
- column `288`: unscaled short-range HF exchange;
- column `289`: VV10 correlation at `b=10`, `C=0.01`;
- column `290`: total frozen-core canonical RI-MP2 correlation.

| Channel | Expansion | integratedDV row |
| --- | --- | ---: |
| Exchange | monomial in `u_x`, Legendre in `v` | 64 |
| Same-spin correlation | monomial in `u_c,ss`, Legendre in `v` | 154 |
| Opposite-spin correlation | Legendre in `u_c,os` and `w` | 166 |

The compression parameters remain `gamma_x=0.004`, `gamma_c,ss=0.01`, and
`gamma_c,os=0.006`. The legacy row-153 smoke remains a plumbing fixture but is
not a production scientific definition.

## Training and numerical passes

Use one fixed-parent training cycle with the selection and weights from the
updated COACH SI final/Cycle-2 Table 2. A validated machine-readable
transcription is still mandatory before fitting. Within that one training
cycle, retain two numerical optimization passes: pass 1 identifies
grid-sensitive rows and pass 2 applies the selected grid-difference
constraints. These passes never regenerate parent orbitals or scalar features.

The Cycle-2 table fixes coefficient-fitting membership and weights but does not
assign every remaining point to model-selection or final-assessment roles.
Those roles must be versioned before model selection; random point-level splits
remain forbidden.

## Remaining gates before a real pilot

1. Verify semantic integratedDV rows `(64,154,166)` against the final COACH
   kernels.
2. Prove checkpoint reload gives identical densities and features.
3. Pass an open-shell PySCF parent/UMP2 gateway.
4. Validate all needed named, generated, ECP, and auxiliary basis translations.
5. Obtain the authoritative published omegaB97M(2) coefficients and reproduce
   trusted molecular and reaction energies.
6. Publish the validated Cycle-2 weight manifest and locked data-role manifest.

Changing the parent method, fixed-orbital policy, 291-feature layout,
semilocal forms, nonlinear parameters, or energy partition requires a new
specification version.
