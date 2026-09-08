# Two corrected-parser large canaries submitted

User-authorized launches completed after interruption/resume and fresh duplicate
check. Commitcfc4722 verified. Corrected-parser checkpoint25702574 completed0:0
in22s oncm1;149tests and repeated five-smaller-case raw audits passed, corrected
candidate artifacts/hash marker verified. No native rerun was needed for dimer.

| Job | Species | Resources | Initial state |
|---|---|---|---|
|25703663|BSR36_c4|16CPU,227GiB,336h|RUNNING on n0072.lr8; entered250974 stage|
|25703685|MOR16_ed33|16CPU,557GiB,336h|PENDING(Resources)|

Both use lr8/accountlr_mhg2/QOSmhg2_lr8_normal. Physical memory773569MiB/node
supports both separate allocations; Slurm associations/dry runs checked. No
duplicate jobs were present.336h is a time ceiling, not ETA. BSR startup log has
no stderr output and its first native stage has PREPARED/input/qchem.out files.
MOR has not started at this check. Do not claim either chemical case completed.

## New launch implementation

- `scripts/run_large_corrected_canaries.py`: two-case-only adapter uses unchanged
  native run_stage/Q4 routines and the committed checkpoint's corrected audit.
  Validates five-smaller checkpoint marker/artifact/dependency hashes; verifies
  source trees, allocation/route and storage; preserves partials and uses a
  duplicate lock; repeats raw readback before corrected publication.
- `slurm/run_large_corrected_canaries_v1.sh`: user-approved module stack,16CPU,
  lr8 route,227GiB default overridden to frozen557GiB for MOR,336h, external logs.
- `tests/test_large_corrected_canaries.py`: two added tests for large-only scope,
  exact allocations and invalid-contract blocking. Full151tests passed9.52s.
- `manifests/production_generator/large_corrected_canaries_v1.json`: freezes
  adapter/checkpoint/recovery/launcher/test hashes and accepted checkpoint path.

These newly introduced launch files are hash-pinned but not yet committed; prior
checkpoint code is committed. User explicitly requested immediate large launches.
Historical top-level parser, native plan and smaller outputs remain unchanged.
No Q-Chem rebuild/new SCF. D4-only1e-12 and fixed-HF2e-8 tolerances unchanged.

Raw stages remain under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/v7_canary_v1/{species}`;
scratch remains `/clusterfs/mhg-data/yaoshen/scf_read/revwb97m2/v7_canary_v1/{species}`.
Corrected publications use separate root
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/large_corrected_canaries_v1/{species}`
with publication.json and LARGE_CANARY_COMPLETE. Do not use historical
CANARY_COMPLETE/species.json as acceptance for these corrected publications.
Broader first16 release/assembly must explicitly adopt corrected five-smaller
checkpoint and two-large publication evidence; old release code is not silently
updated. First16 and100-entry fitting remain unlaunched.

Logs are under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/large_corrected_25703663.out`
and `large_corrected_25703685.out`, with matching `.err` files.

Submitted commands:

```bash
sbatch --parsable --job-name=r2_large_BSR36 --mem=227G revwb97m2/slurm/run_large_corrected_canaries_v1.sh BSR36_c4
sbatch --parsable --job-name=r2_large_MOR16 --mem=557G revwb97m2/slurm/run_large_corrected_canaries_v1.sh MOR16_ed33
```

Do not rerun these commands while jobs are queued/running. Next validate completed
results using the new adapter and explicitly migrate release evidence. Preserve
pinned source files while these jobs depend on them. Commit commands supplied
in chat; committing unchanged files does not alter hashes.
