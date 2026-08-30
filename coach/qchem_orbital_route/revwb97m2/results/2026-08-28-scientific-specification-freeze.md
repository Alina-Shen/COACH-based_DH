# Scientific specification freeze — 2026-08-28

Status: **PASS**

The historical version-1 scientific specification is preserved at
[`../configs/archive/scientific_spec.v1.yaml`](../configs/archive/scientific_spec.v1.yaml).
It was subsequently superseded by version 2 after the authoritative GSCDB
manifest disproved the uniform-basis assumption.

## Decisions

- Fixed Q-Chem ωB97M-V orbitals; no orbital reoptimization during fitting.
- def2-QZVPPD, \(\omega=0.3\), full LR-HF, VV10 \(b=10,C=0.01\).
- Frozen-core canonical RI-MP2; total PT2 fitted, SS/OS saved as diagnostics.
- 291 features with semantic integratedDV rows `(64,154,166)`.
- C0 minimal-critical and C1 PT2+VV10-sum profiles are the first real fits.
- Full sampled COACH bounds are initially disabled.
- Grid stability remains a numerical pass-2 constraint at 0.015 kcal/mol.
- Version-controlled material and heavy data use separate fixed roots.

The accepted `(64,153,166)` H₂O and synthetic-reaction artifacts are retained
as legacy plumbing/algebra smoke fixtures. They are not scientific production
training data.

## Validation

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/venv/bin/python \
  revwb97m2/scripts/validate_scientific_spec.py
```

Result: **57/57 checks passed**.

The checks cover schema status, storage roots, orbital policy, energy
partition, nonlinear parameters, decoded integratedDV row semantics, feature
layout, legacy-smoke preservation, constraint profiles, numerical grids, and
data-splitting policy.

## Required next gate

Before pilot or production work, directly verify that rows `(64,154,166)`
reproduce the intended final COACH kernels, with special attention to the
same-spin row-153/154 basis distinction.
