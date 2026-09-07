# Remaining v7 cohort refresh and success-gated assembly

User authorized the remaining33species and20reaction assembly. Scientific code
remains commit1cbe45b67ca3c0ab2de677b7018df2cccc931281; no science/core edits.
The prior untracked checkpoint report was preserved. Two new Slurm wrappers
are uncommitted execution orchestration, not changes to hash-pinned science.

## Checks and execution

- Loaded and verified frozen plan/source/code/build hashes. Revalidated allfive
  completed species and excluded them. Exactly33 species have no output folder;
  no partial output was silently reused or removed.
- Used partition skill: live mhg had idle CPU nodes with physical memory well
  above21GiB and a valid mhg/normal association. No existing jobs were listed
  for the user at preflight. Kept frozen8CPU,14/21GiB,4hour allocations.
- New remaining-species launcher checks Slurm CPU and memory allocation against
  the exact frozen case. Both resource-class arrays passed test-only scheduling;
  both new scripts passed bash syntax checks. No Q-Chem compilation.
- Array25676786: indices0-9,11,13-14,18-25,27,29-35,37 (30species),14GiB,%2.
- Array25677457: indices15-17 (3species),21GiB,%2,
  dependencyafterok:25676786. Thus no more than two refresh tasks concurrently
  across the arrays; the second does not start following first-array failure.
- Assembly25677566:1CPU,4GiB,30minutes,afterok:25676786:25677457.
  Calls the unchanged committed assembly routine: all38species readback,
  independent stoichiometric reconstruction, unchanged fixed/reference/target/
  Cycle2weights, array serialization checks and validated fitter manifest.
  Wrapper reloads the published manifest and asserts20x292 plus completion marker.

Output root remains
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step14/v7_vv10_refresh_v1`.
Expected fitter manifest after successful assembly: `reactions/inputs.json`.
Logs: repository `revwb97m2/results/v7_remaining_<array>_<index>.out/.err`
and `v7_assembly_25677566.out/.err`.

## Observed status at handoff

Tasks25676786_0 and_1 COMPLETED0:0 in4m22s/4m36s, with validated refresh messages.
Tasks_2 and_3 RUNNING normally; no traceback/error found in current Slurm logs.
Other26tasks await the concurrency limit; three21GiB tasks and assembly await
their success dependencies. **Assembly has not yet run; no20reaction completion
or full38species pass is claimed.** Follow up with sacct and final output/manifest
readback. Preserve failures/partials; do not resubmit automatically or weaken checks.

No new SCF/PT2, bulk fitting, full1498row generation, source deletion, rebuild,
commit or push. The workflow refreshes onlyVV10 atb5.5 using saved orbitals.
