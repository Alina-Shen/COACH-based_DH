# Bounded v7 chemical refresh: implementation awaiting commit

Scope: the existing validated38species/20reaction Step14 cohort only. No full
dataset generation, SCF, new PT2, Q-Chem rebuild or automatic Slurm submission.
No test, configuration freeze or chemical run was executed on this new code.

## New code

- `v7_refresh.py`: immutable plan freeze, legacy/recovery revalidation, one-
  species scalar refresh, independent species readback, reaction assembly and
  fitter-facing publication. Only column289 (VV10) changes. Old SR-HF, PT2,
  D4, semilocal/grid and field-aware fixed energy are reused after checks.
- `scripts/v7_refresh.py`: explicit `freeze`, `species`, `validate-species`,
  `assemble` commands. There is no loop that submits38 jobs automatically.
- `tests/test_v7_refresh.py`: four new tests for no-overwrite behavior, vector
  validity, independent stoichiometric tamper detection and VV10-only target
  invariance. Tests are added but unrun pending the user's checkpoint.

The prior synthetic integration harness, its launcher and test report remain
uncommitted from the previous turn and should be included in the checkpoint.
Its corrected fresh rerun is still pending; prior corrected readback passed.

## Safety and recovery semantics

Freeze revalidates all existing species and reconstructs the old reaction arrays
against their hashed Step14 outputs. It checks normal/legacy PT2 parsing,
hydrogen's approved zero PT2, Q4 grid provenance and field-aware fixed energy.
It records code, source and Q-Chem launcher/executable/libks library hashes.
The output root must be new and outside authoritative/historical source trees.

Species execution checks the original full orbital tree hash, makes a fresh
non-overwriting copy and verifies it before Q-Chem. The only new electronic
job prints raw SR-HF/VV10 with b5.5 and zeroSCF. SR-HF must agree with the old
value within1e-8Ha before retaining the old fixed-LR partition. This threshold
uses the existing parent-energy reconstruction tolerance, not a newly relaxed
criterion. Source-tree and working-qarchive identities are checked afterward.
The seven legacy recovery cases are revalidated/reused, not blindly recalculated
with the normal parser. Any mismatch blocks publication and preserves partials.

Species readback independently extracts printed SR-HF and VV10, checks exact
prepared input controls, every reused column, fixed energy, grid differences
and working archive hash. A completion marker is written only after readback.
Restart of a complete matching species validates/reuses; partials fail and are
not deleted or silently rerun.

Assembly calls the loop-based reaction assembler and separately reconstructs
using a stoichiometric matrix. Reference-minus-fixed targets and Cycle2 weights
must remain equal to the old baseline. It saves spec/plan/species/array hashes,
validates the fitter-facing manifest through `load_inputs`, then publishes
`reactions/inputs.json` and ASSEMBLY_COMPLETE. VV10 grid differences remain zero
with explicit SG-1-only reason; no both-grid VV10 robustness claim.

## After commit: staged commands (not executed here)

First run the full unit suite and config validation, then freeze a NEW plan:

```bash
python -m pytest -q revwb97m2/tests
python -m revwb97m2.scripts.validate_scientific_spec --json
python -m revwb97m2.scripts.v7_refresh freeze \
  --plan revwb97m2/manifests/reaction_features/v7_refresh_plan_v1.json \
  --root /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step14/v7_vv10_refresh_v1
```

Use activated dh and the documented Q-Chem runtime environment. Freeze may
perform substantial source/output reads but does not run jobs or copy orbitals.
Review its cases/resources before selecting bounded chemical gateway jobs.
Cases retain the prior per-species8CPU allocations and conservative resources;
partition/account/QOS must be checked live before submission. No Slurm script
is added yet to avoid implying a frozen resource/launch approval for all38.

On an approved compute allocation, run one listed species, e.g.:

```bash
python -m revwb97m2.scripts.v7_refresh species \
  --plan revwb97m2/manifests/reaction_features/v7_refresh_plan_v1.json \
  --species 11_Reactant1_EIE22 --cpus 8
```

After all required cohort species pass, assemble:

```bash
python -m revwb97m2.scripts.v7_refresh assemble \
  --plan revwb97m2/manifests/reaction_features/v7_refresh_plan_v1.json
```

The existing separate h2o/NH2rad Step9 gateways are NOT automatically included
in these38 fitting species. Their b5.5 input-preparation checks already exist;
separate runtime checks need their own bounded plan, not fabricated cohort
membership. Verify spin coverage of selected cohort gateways before launching.
Use the resulting `reactions/inputs.json` for the bounded v7 fit runner only
after publication completes. Full1498row generation remains outside this module.

## Commit scope

Review and commit new refresh module/CLI/tests/document plus prior test harness,
launcher, small test report and configuration-validation record. Do not stage
chemical work directories, solver arrays/logs, licenses or private reproducer
inputs. No commit or push performed by the assistant.
