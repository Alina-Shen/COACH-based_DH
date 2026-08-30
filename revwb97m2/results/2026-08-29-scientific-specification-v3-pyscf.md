# Scientific specification version 3 — PySCF parent route

Date: 2026-08-29

Status: **PASS**

## Decision

Replace Q-Chem orbitals with one self-consistent unrestricted PySCF
omegaB97M-V parent calculation per species. Freeze each validated PySCF
checkpoint and density for all 291 features, reaction assembly, and coefficient
searches. Q-Chem remains input-metadata provenance and cross-engine regression
material only.

Version 2 is preserved byte-for-byte at
`configs/archive/scientific_spec.v2.yaml` with SHA-256
`14bec05194b32e329dcd43ba5c466849fff5830b0565e70cef4cde30c70d4a0e`.

## RI-MP2 evidence

The matched `h2o_SW49` calculation used the authoritative Q-Chem geometry,
`def2-QZVPPD`, `rimp2-def2-QZVPPD`/`def2-qzvppd-ri`, one frozen core orbital,
the unrestricted reference, the `(99,590)` parent grid, and SG-1 VV10 grid.

- PySCF parent: `-76.4399676777627` hartree.
- Q-Chem parent: `-76.4399676648` hartree.
- Parent difference: `-1.2962701e-8` hartree.
- PySCF density-fitted UMP2 OS: `-0.2537182846426216` hartree.
- Q-Chem unscaled RIMP2 OS: `-0.2537182600352889` hartree.
- Scaled OS difference at Q-Chem `a_os=0.4534`: `-1.1156965e-8`
  hartree.
- PySCF RI-minus-conventional total UMP2: `1.1608544e-5` hartree =
  `0.00728` kcal/mol, below the frozen `0.015` kcal/mol numerical threshold.

The accepted machine-readable report is
`results/2026-08-29-pyscf-qchem-rimp2-h2o-sw49.json`. The initial stricter
diagnostic report is retained as
`results/2026-08-29-pyscf-qchem-rimp2-h2o-sw49.strict-preliminary.json`.

## Preserved model

- Semantic integratedDV rows remain `(64,154,166)`.
- Feature layout remains 288 semilocal terms plus SR-HF, VV10, and total PT2.
- Fixed energy remains nuclear + one-electron + Coulomb + full LR-HF.
- Use one fixed-parent training cycle with updated SI final/Cycle-2 weights.
- Retain two numerical grid-optimization passes inside that one cycle.

`scripts/validate_scientific_spec.py` passes all version-3 checks. Open-shell,
generated-basis/ECP/auxiliary-basis, kernel-semantic, published omegaB97M(2),
Cycle-2 weight-manifest, and locked data-role gates remain required before a
real pilot.
