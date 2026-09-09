# Water scalar refresh and embedded-ECP Y gateway — 2026-09-08

## Outcome

Implemented, tested and frozen for the user's pre-execution commit. No native
calculations or real Slurm submissions occurred. Numerical coverage remains
221/224 species and the existing 93-row diagnostic is not a full pilot release.
No Q-Chem rebuild, new SCF, scientific-specification changes, tolerance relaxation,
historical artifact replacement, or scratch cleanup was performed.

## Reference calculations and diagnosis

Inspected `/clusterfs/mhg-data/yaoshen/wb97m_os/GSCDB/debug/3d4dIPSS_V_GS+`
and `/clusterfs/mhg-data/yaoshen/wb97m_os/GSCDB/wb97m_os_rimp2/work`.
The completed production Y_GS and Y_GS+ inputs are byte-identical to the project's
authoritative `input0` files. They already specify BASIS GEN, ECP GEN, PURECART
11111, SCF_GUESS READ and N_FROZEN_CORE FC, with complete embedded basis/ECP
blocks. Both corresponding outputs terminate normally with 180 orbital basis
functions and 252 auxiliary functions. The Y ECP removes 28 core electrons:
neutral Y has 11 explicit electrons (6 alpha/5 beta), Y+ has 10 (5/5).
The legacy Python gateway explicitly rejects embedded ECPs; the references do
not establish a need to change Q-Chem or the authoritative Y inputs.

V debug experiments include reduced angular-momentum bases and incomplete runs.
The `_old.out` reports `Error in gen_scfman`; `_pass.out` ends at the first SCF
cycle and is not successful merely because of its filename. The final production
V+ result instead completes with AUG-CC-PWCVQZ and SCF_GUESS READ (185 orbital,
309 auxiliary functions). These mixed experiments do not isolate one causal V
fix. No exploratory V basis reduction was transplanted into Y.

## New code and purpose

| File | Main locations | Explanation |
| --- | --- | --- |
| `revwb97m2/scripts/refresh_water_scalar_v1.py` | reuse audit19; vector update57; load65; validation75; execution93; CLI132 | Audits retained water grids/PT2/fixed energy and source orbitals; runs only the scalar stage at approved VV10 b5.5/C0.01. Changes only VV10 column289 (zero-based), preserving the other291 features. Rejects SR-HF/PT2 inconsistencies and nonfinite values; validates before publishing completion. |
| `revwb97m2/scripts/embedded_y_features_v1.py` | ECP count24; input preservation40; freeze57; load98; component readback112; validation131; execution144 | Narrowly allows only the two validated Y cases with ECP28 and matching electron/spin bridge. Preserves complete molecule/basis/ECP blocks across all six native stages; pins successful production references and orbital provenance; reconstructs and validates292 features before completion. |
| `revwb97m2/slurm/run_water_scalar_refresh_v1.sh` | whole new launcher | One8CPU/14GiB/72h scalar job with approved modules and dh environment. |
| `revwb97m2/slurm/run_embedded_y_features_v1.sh` | whole new launcher | Two8CPU/14GiB/72h six-stage tasks, array0-1 without an artificial concurrency cap. |
| `revwb97m2/tests/test_water_scalar_refresh.py` | whole new test file | Four tests cover single-column replacement and refusal of changed SR-HF, PT2 or nonfinite VV10. |
| `revwb97m2/tests/test_embedded_y_features.py` | whole new test file | Six tests cover validated valence counts and rejection of wrong ECP core, representation, element or bridge. |

All six files are additions. Existing hash-pinned generic/canary drivers were
left unchanged so previously accepted evidence remains reproducible. The ECP
exception is deliberately not a claim of arbitrary-element ECP support.

## Frozen plans, verification and resources

Created under `revwb97m2/manifests/production_generator`:

- `water_scalar_refresh_v1_base.json`: generic source/input contract. It pins all
  six derived inputs conservatively; actual water execution is scalar-only.
- `water_scalar_refresh_v1.json`: water-specific reuse/code contract.
- `water_scalar_refresh_v1_release_draft.json`: disabled precommit release.
- `embedded_y_features_v1.json`: exact two-case execution/reference contract.
- `embedded_y_features_v1_release_draft.json`: disabled precommit release.

Full test suite: **182 passed in6.40s**. Both shell syntax checks and
`git diff --check` pass. Fresh water reuse and Y preserved-input/source-tree
checks pass. Both draft releases correctly reject execution. Actual derived
water scalar input contains NL_VV_B550 and NL_VV_C100.

Planned native work is13 stages: one water scalar and six stages for each Y.
Water source copy60,776,002bytes; the two Y six-stage copies total268,091,058bytes
(these are copy sizes, not estimates of all outputs/scratch). New retained roots
are under `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/`
with namespaces `water_scalar_refresh_v1` and `embedded_y_features_v1`; scratch
uses the same namespaces beneath `/clusterfs/mhg-data/yaoshen/scf_read/revwb97m2`.
All new execution roots were absent at final checks.

Live partition inspection favored cm1/lr_qchem/condo_qchem with idle nodes and
sufficient memory. `sbatch --test-only` estimated immediate starts at the review
time; identifiers25725964 and25726066 are test-only, NOT submitted jobs. Recheck
queue/storage/duplicates after commit. Never use lr_lowprio; no eight-task cap.

## Next gate

User commits the new code, plans and pending prior readback/submission evidence.
Then verify commit hashes, repeat live route/storage/duplicate checks, create
approved releases and submit the three tasks. After completion, independently
validate all three species and integrate their explicit adapters plus corrected
legacy fixed energies into the exact100-row/292-column pilot export. Validate
the full matrix before the bounded MIO pilot. Do not silently fit only93 rows.
