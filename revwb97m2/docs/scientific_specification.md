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
`gamma_c,os=0.006`. The project-owned production implementation is
[`../integrated_dv.py`](../integrated_dv.py), whose independent validation is
recorded in
[`../manifests/integrated_dv/validation.json`](../manifests/integrated_dv/validation.json).
It returns the three selected rows as a `3 x 96` matrix and contains no
published COACH coefficients. The legacy row-153 smoke remains a plumbing
fixture but is not a production scientific definition.

## Training and numerical passes

Use one fixed-parent training cycle with the selection and weights from the
updated COACH SI final/Cycle-2 Table 2. The validated machine-readable 49-row
input and expanded 1,498-entry manifest are published under
`revwb97m2/manifests/weights/`. Within that one training cycle, retain two
numerical optimization passes: pass 1 identifies
grid-sensitive rows and pass 2 applies the selected grid-difference
constraints. These passes never regenerate parent orbitals or scalar features.

The Cycle-2 table fixes coefficient-fitting membership and weights. Data-role
policy v2 now assigns the four downstream roles explicitly. The 1,498 Cycle-2
entries determine coefficients; all 137 GSCDB137 datasets supply the
COACH-faithful dataset/category NER model-selection metric; `AE11`, `MB08-165`,
and `MB16-43` supply the published overfitting diagnostic; and the appended
`SC74`/`OEEFD`, BigNC, and GDB9-W1-F12 are reserved for final energy
assessment. GDB9-W1-F12 is the strongest untouched robustness test. BigNC is
post-freeze here, but COACH itself tuned D4-ATM on L14/vL11, so no project
parameter may be selected from BigNC. OPT is a separate geometry assessment.
These roles
are intentionally overlapping where the source protocol overlaps: GSCDB137 is
not an independent validation set, and `MB16-43` is both fitting data and an
overfitting diagnostic. Final external errors may not change the model.

The exact roles and unique species lists are versioned under
`revwb97m2/manifests/data_roles/`. Geometry, charge, multiplicity, basis,
auxiliary basis, ECP, and counterpoise ghost-center metadata are parsed from
verified, hash-pinned Q-Chem input snapshots. Q-Chem orbitals, `qarchive.h5`,
and orbital scratch directories are prohibited as inputs. The official GSCDB
AdditionalSets snapshot supplies BigNC, GDB9-W1-F12, and OPT inputs.

The corresponding 17,658 all-UKS molecular definitions are now frozen in the
read-only heavy-data snapshot
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/authoritative_inputs/pyscf/revwb97m2_all_uks_inputs_v1`.
Every record stores `spin = multiplicity - 1`, requests UKS/UMP2 without an
exception path, and carries its source-input and normalized PySCF-geometry
hashes. The checksum-manifest SHA-256 is
`c4f2d596a5b779bc6bb25d6fb31a2ab79c285374af6388ec960b1461b40238bb`.
The immutable source snapshot deliberately retains its original Step-5
``blocked_pending_step_6`` marker. Step 6 is now complete as a separate,
versioned overlay under `revwb97m2/manifests/basis_bridge/`: all 17,658 records
have resolved orbital, auxiliary, and ECP definitions and passed independent
dimension, element-coverage, electron-count, and representative PySCF-build
checks. Production code must combine the immutable molecular record with this
validated bridge; it must not edit or reinterpret the Step-5 snapshot.

Named RI bases are translated from hash-pinned files in the Q-Chem auxiliary
library, which preserves heavy-element coverage that PySCF's packaged aliases
do not always provide. Q-Chem's implicit def2 ECP behavior is made explicit in
PySCF. Missing source RI assignments are frozen as `rimp2-def2-TZVPPD` for
BigNC, `rimp2-def2-TZVP` for GDB9-W1-F12, and `rimp2-def2-QZVPPD` for OPT;
runtime automatic auxiliary generation is forbidden. `AE11_Yb` preserves its
verified explicit all-electron orbital and auxiliary blocks with no ECP.

## Remaining gates before a real pilot

1. Pass an open-shell PySCF parent/UMP2 gateway.
2. Obtain the authoritative published omegaB97M(2) coefficients and reproduce
   trusted molecular and reaction energies.

The Cycle-2 fitting-weight, locked data-role, immutable all-UKS molecular-input,
PySCF basis-bridge, and project-owned integratedDV-kernel gates are complete.
The manifest-driven all-UKS parent driver and bitwise checkpoint
density/feature-identity gate are also complete for the closed-shell
`h2o_SW49` gateway. Its PySCF stability response remained indeterminate because
the response omits NLC and was prohibitively slow; this is recorded rather
than interpreted as a stable or unstable solution.

Changing the parent method, fixed-orbital policy, 291-feature layout,
semilocal forms, nonlinear parameters, or energy partition requires a new
specification version.
