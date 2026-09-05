# Frozen scientific specification, version 6

The authoritative machine-readable specification is
[`../configs/scientific_spec.yaml`](../configs/scientific_spec.yaml). Version 5
is preserved byte-for-byte at
[`../configs/archive/scientific_spec.v5.yaml`](../configs/archive/scientific_spec.v5.yaml)
with SHA-256
`527d4d04a4c77cf6cbc591ad77113330664bf06466a384fab3368e0b450e2dc4`.

## Version-6 dispersion and coefficient decision

The revised model contains both the original-form VV10 feature (`b=10`,
`C=0.01`) and the pure three-body D4-ATM feature used by COACH. The raw D4
feature freezes COACH's damping definition at `s6=0`, `s8=0`, `s9=1`,
`a1=0.215`, `a2=5.8`, and `alp=16`; therefore it contains ATM only, with no
two-body D4 contribution. Its fitted linear coefficient `c_d4_atm` is distinct
from the internal `s9=1` used to define the feature.

`c_vv10`, `c_pt2`, and `c_d4_atm` are fitted independently. The published
omegaB97M(2) relation `c_vv10 + c_pt2 = 1` is not imposed on the revised model.
Each coefficient has conceptual domain `(0,1)`. Since MIO solvers do not
represent strict inequalities, the executable bounds are
`1e-8 <= c <= 0.99999999`. No equality couples these three coefficients.

## Version-5 orbital-source decision

Production reuses the existing self-consistent Q-Chem unrestricted
omegaB97M-V archives. A live versioned authority check confirms a regular,
nonempty `qarchive.h5` for all 14,006 canonical GSCDB and auxiliary-only
species under `/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2`. Every
feature job copies the source archive into an isolated non-overwriting run
directory, verifies source/copy hashes, sets `MAX_SCF_CYCLES 0` and
`GEN_SCFMAN FALSE`, and never updates the orbitals.

The matching verified Q-Chem input remains the authority for geometry, charge,
multiplicity, orbital basis, auxiliary basis, ECP, and unrestricted-reference
settings. IntegratedDV, SR-HF, VV10, and RI-MP2 must use the same imported
archive; mixing a Q-Chem integratedDV density with independently optimized
PySCF orbitals is forbidden. PySCF inputs, basis translation, checkpoints, and
pilots remain validated fallback/regression evidence but are never selected
silently.

The orbital authority and its validation are versioned under
`revwb97m2/manifests/qchem_orbitals/`. BigNC has 75/75 source archives, which
must be copied into project-owned non-overwriting storage before post-freeze
use. GDB9-W1-F12 has verified input metadata but no validated Q-Chem orbital
authority, so that final assessment is explicitly blocked pending a new
versioned inventory; PySCF regeneration is not an implicit substitute. OPT is
outside the fixed-geometry energy workflow.

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

## Frozen 292-feature energy model

The fixed energy is

\[
E_{\mathrm{fixed}} = E_{\mathrm{nuc}} + E_{\mathrm{one}} + E_J
                   + E_x^{\mathrm{LR-HF}}.
\]

The fitted vector has exactly 292 columns:

- columns `0:96`: semilocal short-range exchange;
- columns `96:192`: semilocal same-spin correlation;
- columns `192:288`: semilocal opposite-spin correlation;
- column `288`: unscaled short-range HF exchange;
- column `289`: VV10 correlation at `b=10`, `C=0.01`;
- column `290`: total frozen-core canonical RI-MP2 correlation.
- column `291`: frozen-parameter COACH pure three-body D4-ATM energy.

Thus the fitted scalar contribution is

\[
c_{\mathrm{srHF}}E_x^{\mathrm{srHF}} + c_{\mathrm{VV10}}E_c^{\mathrm{VV10}}
+ c_{\mathrm{PT2}}E_c^{\mathrm{PT2}} + c_{\mathrm{D4ATM}}E^{\mathrm{D4ATM}}.
\]

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
and orbital scratch directories were excluded by the version-4 metadata policy;
version 5 separately authorized the matching Q-Chem archive as the fixed
orbital input. This does not change the data-role manifest's narrower metadata
provenance claim. The official GSCDB AdditionalSets snapshot supplies BigNC,
GDB9-W1-F12, and OPT input metadata.

The corresponding 17,658 all-UKS PySCF molecular definitions remain frozen as
a nonproduction fallback in the read-only heavy-data snapshot
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
checks. Fallback code must combine the immutable molecular record with this
validated bridge; it must not edit or reinterpret the Step-5 snapshot.

Production Q-Chem uses each matching named or embedded orbital, ECP, and
auxiliary-basis definition directly. The validated PySCF translations remain
available only for fallback and cross-engine checks. Missing source RI
assignments are frozen as `rimp2-def2-TZVPPD` for BigNC,
`rimp2-def2-TZVP` for GDB9-W1-F12, and `rimp2-def2-QZVPPD` for OPT; runtime
automatic auxiliary generation is forbidden. `AE11_Yb` preserves its verified
explicit all-electron orbital and auxiliary blocks with no ECP.

## Version-5/6 integratedDV output contract

The current Q-Chem trunk prints integratedDV only when
`QCHEM_PRINT_INTEGRATED_DV=1`. A feature run must use a meta-GGA functional and
emit a final complete block delimited by `COACH integratedDV begin` and
`COACH integratedDV end`, with label `integratedDV` and printed shape 96x180.
The extractor records the number of complete blocks, retains the final complete
block, transposes it to the COACH 180x96 convention, and selects rows
`(64,154,166)`. Grid `250974` supplies the 288 semilocal fitting columns;
`99590` and `75302` supply grid-difference constraints.

The Q-Chem port follows the historical layout but uses the frozen revised-model
`gamma_c,ss=0.01`, not historical `0.2`. Source-level selected-feature parity
against `revwb97m2/integrated_dv.py` passed with maximum absolute difference
`3.4694469519536142e-18`. Native Q-Chem build and smoke validation remain
Step-7/Step-10 execution gates; they are not prerequisites for freezing the
scientific policy in Step 1.

## Remaining gates before a real pilot

1. Build and provenance-pin the current Q-Chem executable.
2. Pass restricted and unrestricted archive-reuse gateways on all three feature
   grids, including archive hash identity and native integratedDV comparison.
3. Complete: the final-complete-block extractor, immutable atomic publisher,
   restart reuse, and missing/corrupt-archive refusal pass fixtures and all six
   native Q3 cases.
4. Prove that integratedDV and scalar features use the same imported archive.
5. Validate the COACH D4-ATM definition and independent open-interval solver
   bounds.
6. Reproduce the parent/component, published omegaB97M(2), reaction, and direct
   energy identities required by the machine-readable specification.

The Cycle-2 fitting-weight, locked data-role, Q-Chem orbital-authority, immutable
PySCF fallback-input, PySCF basis-bridge fallback, and project-owned Python
integratedDV reference gates are complete. The previous parent/checkpoint and
stability evidence remains regression evidence. Version 6 performs no new SCF
or stability search and never substitutes an alternative solution.

Changing the parent method, fixed-orbital policy, 292-feature layout,
semilocal forms, nonlinear parameters, or energy partition requires a new
specification version.
