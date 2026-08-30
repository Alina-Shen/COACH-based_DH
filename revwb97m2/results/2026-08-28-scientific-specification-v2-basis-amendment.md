# Scientific specification version 2 — GSCDB basis amendment

Date: 2026-08-28

Status: **PASS**

## Decision

Follow COACH/GSCDB closely by using the authoritative per-species orbital-basis
assignments rather than uniform def2-QZVPPD. BigNC remains a separate external
evaluation set and is not part of GSCDB137 training.

The original specification is preserved verbatim at
`configs/archive/scientific_spec.v1.yaml`. Version 2 is authoritative at
`configs/scientific_spec.yaml`.

- Version-1 SHA-256: `7655331b2d8edc43650f36187391ce62fe910f46ce19f0ad59dcf83e2cc03106`
- Version-2 SHA-256: `14bec05194b32e329dcd43ba5c466849fff5830b0565e70cef4cde30c70d4a0e`

## Frozen basis policy

- 13,907 core GSCDB137 species and 14 manifest basis labels.
- 8,276 def2-QZVPPD species and 5,631 species using other GSCDB assignments.
- Q-Chem `BASIS GEN`/`GENERAL` realizations must retain their complete `$basis`
  sections.
- Per-species `AUX_BASIS_CORR` values and generated `$aux_basis` sections must
  be preserved; Q-Chem `input0` is authoritative over incomplete advisory
  metadata.
- Uniform basis replacement is forbidden for production training.

## Validation

The live validator read all 13,907 core Q-Chem `input0` files:

- all inputs and `$rem` blocks were present;
- every orbital basis agreed semantically with the GSCDB manifest;
- all generated orbital and auxiliary basis sections were present;
- every nonblank auxiliary-basis metadata label matched Q-Chem;
- the only advisory omission was `AE11_Yb`, whose input explicitly supplies
  `AUX_BASIS_CORR GEN` and `$aux_basis`.

`scripts/validate_scientific_spec.py` passes **75/75** checks, and
`scripts/validate_gscdb_basis_policy.py` passes all seven live checks.

No orbital or heavy-data files were copied or modified.
