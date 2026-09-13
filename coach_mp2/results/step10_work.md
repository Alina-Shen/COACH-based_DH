# Step 10 — resource pilots in progress

## Work performed

1. Read the frozen Step10 exit criterion, revwb97m2 Q6 pilot manifest/resource guidance/completion report, and the current COACH Step6/8 runtime contracts. The reference high-tier grid stage took about 11 hours and excluded RI-MP2; its memory observations cannot certify COACH production.
2. Selected the same three fitting-domain representatives as reference Q6: 3d4dIPSS_Ag_GS (180 AOs), TMB28_C1 (1342), MOR32_pr24 (4979). Compiled full available-source size context: 14081 species, including 14 above 5000 AOs. Three pilots do not validate all sizes/bases/spins.
3. Prepared 21 hash-pinned inputs: three integration grids, SRHF+VV10, full-HF, LRHF and canonical frozen-core RI-MP2 per species. Preserved authoritative geometry/basis/ECP and zero-SCF controls; omega remains 0.27. No automatic auxiliary replacement.
4. Implemented an isolated runner using the Step8 COACH executable/local libks.so. It verifies runtime/input/import hashes, copies only project-owned immutable imports to separate scratch per stage, checks normal termination, exact saved MOs and reconstructed spin densities, and validates feature shape/PT2 closure/HF and parent identities.
5. Instrumented source hashing/copying, native elapsed time, GNU-time peak RSS, output sizes and retained scratch bytes. Retained scratch is explicitly not a peak scratch measurement. Results survive subsequent stage failures; no automatic retries or overwriting existing pilot directories.
6. Used the partition skill. Its helper script was missing, so queried sinfo/sacctmgr/scontrol directly, checked storage (about 2.5 PiB filesystem free; not a quota guarantee), and compared sbatch test-only forecasts. Moved small/medium to cm1 without changing memory or CPUs. Retained lr8 for 557 GiB high-tier memory. Scheduler forecasts are provisional; small/medium started despite later predicted times.
7. Submitted small 25837195 (cm1/lr_qchem/condo_qchem, 8 CPU,14 GiB,2h), medium 25837197 (same route,8 CPU,62 GiB,8h), high 25837199 (lr8/lr_mhg2/mhg2_lr8_normal,16 CPU,557 GiB,48h). High walltime includes additional HF/VV10/RI stages relative to reference's 24h grid-only allocation.
8. Passed 21 input/control/hash checks, Python parsing and shell syntax checks, and Slurm preflight. These are preparation checks, not completed native resource validation.
9. Added a read-only-to-jobs accounting collector: `python -B coach_mp2/scripts/collect_step10.py` using the dh environment. It writes progress evidence and keeps native success separate from capacity signoff. It never submits/retries or marks Step10 complete automatically.
10. Recorded protocol, hashes, job IDs, inventory context, progress and project notes. No solver or license was used. No bulk production was submitted.

## Remaining completion gates

Wait for all native stages and terminal Slurm accounting, inspect failures if any, and review per-stage CPU/memory/storage evidence before publishing resource guidance. Do not infer safe class-wide downsizing from three species. Step10 remains in progress; Step11 has not started. The solver decision remains deferred until backend-dependent work (expected Step14). Carbon F01 and GDB9 F02 remain unchanged.

Code/settings/important results: `/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2`.
Heavy measurements/outputs: `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step10_v1/<tier>`.
Separate stage scratch: `/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step10_v1/<species>_<stage>`.
All source orbital archives and reference projects remain read-only.

[Latest collected status](step10_progress.json) · [Protocol](../manifests/step10_protocol_v1.json) · [Job IDs](../manifests/step10_jobs_v1.json) · [AO inventory](step10_inventory_context.json)

## Latest checkpoint

Jobs 25837195 and 25837197 are RUNNING. Ag has passed all three grid stages; its observed maximum stage RSS so far is about 1910 MiB (partial measurement, not a recommended memory limit). Job 25837199 is PENDING with `QOSGrpCpuLimit`, a scheduler QOS CPU-capacity restriction. No memory request has been reduced to bypass that restriction.
