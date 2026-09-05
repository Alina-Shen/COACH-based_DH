# Q2 Q-Chem build started

Date: 2026-09-03

Status: in progress

## Frozen source

- Q-Chem: `https://jubilee.q-chem.com/svnroot/qchem/trunk`, revision 48798.
- libks external: `https://jubilee.q-chem.com/svnroot/libks/trunk`, revision 1666.
- Complete scheduled libks diff SHA-256:
  `8d40ca02fac8edd3f1d99886755a0a7794c462bbcb606f2378f23eabb5570bf0`.
- Exactly four intended libks paths are changed: two modified and two added.
  Their content hashes are frozen in
  `revwb97m2/manifests/qchem_build/q2_qchem_build_v1.yaml`.

## Build request

- Slurm job: `25523453` (`rev_q2_qchem_build`).
- Partition/account/QOS: `cm1/lr_qchem/condo_qchem`.
- Resources: one node, one task, 16 CPUs, 128 GB, 12 hours.
- Compiler: GNU 10.5.0, matching the last known working Q-Chem trunk build.
- Configuration: shared `RELWITHDEBINFO`, OpenMP, embedded version metadata.
- Isolated installation root:
  `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_builds/qchem-r48798-libks-r1666-idv-8d40ca02`.

Live Slurm comparison with the same resources predicted `cm1` as the earliest
eligible CPU partition. Only `partition`, `account`, and `qos` changed after the
comparison; CPU count and requested memory were preserved.

## Safety and completion contract

The job aborts before configuration if either SVN revision, the complete libks
diff hash, or any modified-file hash changes. It refuses to overwrite a
completed build or reuse a partially configured build tree. After a successful
full build and install it records compiler/tool versions, source pins,
executable SHA-256, executable size, and `ldd` output, and rejects unresolved
dynamic libraries.

The independent validator was run before the build. It failed as intended
because no completion marker, executable, or build logs exist yet, while every
current-source identity check passed. Q2 remains in progress until job
`25523453` is terminal and the validator passes. No chemistry calculation was
submitted.
