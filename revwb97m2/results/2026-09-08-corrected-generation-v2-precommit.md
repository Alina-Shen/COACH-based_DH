# Corrected seven-canary integration and first16 v2 pre-commit checkpoint

Implemented and validated; stop for user commit and live resource/submission
review. No Slurm jobs, new SCF/native calculations, data overwrites or cleanup.
Historical code, first16 v1, canary plans and outputs remain unchanged.

## Changes and rationale

- `scripts/corrected_canary_evidence.py`: explicit seven-species registry reader.
  Requires exactly the five corrected checkpoint cases and two corrected large
  publications; checks marker/record/artifact/source/spec/contract hashes and
  independently reparses native data. Provides validated vectors, corrected fixed
  energies and grid differences. Strict stoichiometric assembly adapter passes
  these values into the existing reaction assembler, rejecting missing species.
- Same module's `components`: production postprocessing now uses the tested
  corrected nuclear parser; supports explicit field inputs only with the final
  nuclear breakdown present. No tolerance changes: fixed HF2e-8Ha; D4-only1e-12Ha;
  allother291columns/grids remain exact on readback.
- `scripts/generate_training_features_v2.py`: separate v2 generator/validator and
  release gate. Requires corrected registry hash, seven-case validation, explicit
  user submission/resource approval and a commit containing frozen code/plan.
  Complete/partial same-contract restart semantics, duplicate lock, input/build/
  restart-tree checks remain. v2 explicitly rejects legacy reuse references until
  their corrected migration is audited, rather than silently accepting old fixed
  values. Historical v1 is preserved for historical validation.
- `slurm/run_training_features_v2.sh`: points to v2 generator/manifest and requires
  a release file. Keeps first16 8CPU/14GiB/72h requests and approved modules.
- `tests/test_corrected_generation_release.py`:six new tests cover absent release
  before side effects, legacy rejection, exact-seven coverage, record/marker/
  artifact corruption, corrected fixed/stoichiometric assembly, missing species
  and wrong registry hash. Full157tests pass8.07s; shell syntax/diff checks pass.

## Frozen artifacts

- `manifests/production_generator/corrected_canary_evidence_v1.json` pins accepted
  five-case checkpoint25702574 and two large publications25703663/25703685.
  SHA256 `56979840d120d03bfc69853b32ad8857628c9deb6d2bd878aab1f2c6d556b7e9`.
- `manifests/production_generator/training_first16_v2.json`:
  SHA256 `1ccb606f4a3fe8a6744f470d6749cf7856c71c636489f854c2cbdbf95b9aeafe`.
  Same16 species, derived inputs, basis/source-tree identities and resource routes
  as v1, independently compared.94 native stages; two one-electron PT2 exemptions.
  Restart-copy lower bound5184757659bytes (4.8287GiB), excluding generated scratch.
- `manifests/production_generator/training_first16_v2_release_draft.json` binds
  these hashes but user_approved_submission=false/resource_review_passed=false
  and a non-commit placeholder. Tested to reject launch. This is not a release.

New planned roots (neither created):
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/training_first16_v2`
and `/clusterfs/mhg-data/yaoshen/scf_read/revwb97m2/training_first16_v2`.

## Real-data validation

Fresh corrected-registry validation passes allseven, including original native
plan/build/source trees, smaller checkpoint and large publication evidence.
Separately ran the NEW generic component reader on allseven retained raw cases:
all vectors/fixed energies/grids agree with accepted corrected publications.
Machine-readable results:
`results/2026-09-08-corrected-generation-v2-validation.json`.
No expensive native reruns; D4 is recomputed only for readback validation.

This is NOT production of16 new species, numerical assembly of100/1498entries,
or full migration of the earlier38-species refresh cohort. That cohort remains
historical and requires explicit corrected reuse auditing before wider assembly.
The assembly adapter is tested with synthetic signed combinations; no chemical
reference data or fitting weights were invented for an absent matrix.

## Next steps

1. User reviews/commits these new files (commands provided in chat). Do not edit
   frozen files without re-freezing a new tested contract.
2. Verify the resulting commit, review live partition/account/QOS, storage and
   existing jobs; choose/review concurrency (proposal8). Create a separate actual
   release referencing that commit after explicit submission approval. Do not
   simply mark the draft true without performing these checks.
3. Submit first16 only after release; review actual native execution and outputs
   before wider species generation. No queue-time/runtime promise from this step.
4. Audit remaining224-pilot-species reuse/missing stages and prepare full100-row
   assembly once their corrected compatible values exist. All1498 COACH training
   entries/weights remain unchanged; solver-gap closure is not a prerequisite for
   compatible feature generation.

Verification commands:

```bash
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m pytest revwb97m2/tests -q
bash -n revwb97m2/slurm/run_training_features_v2.sh
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m revwb97m2.scripts.generate_training_features_v2 check --plan revwb97m2/manifests/production_generator/training_first16_v2.json
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m revwb97m2.scripts.generate_training_features_v2 check-evidence --plan revwb97m2/manifests/production_generator/training_first16_v2.json
```
