# Q2 in-place Q-Chem build and integratedDV runtime probe

Date: 2026-09-04

Status: build evidence verified; Q2 not closed because the required runtime
output is absent and a source correction plus rebuild is required.

## Build evidence

- Build/install root: `/clusterfs/mhg-data/yaoshen/qchem/trunk`.
- Q-Chem SVN revision: `48798`; libks external revision: `1666`.
- The four intended libks file hashes and the complete local-diff hash match
  `q2_qchem_build_v1.yaml`; the diff SHA-256 is
  `8d40ca02fac8edd3f1d99886755a0a7794c462bbcb606f2378f23eabb5570bf0`.
- Executable: `/clusterfs/mhg-data/yaoshen/qchem/trunk/exe/qcprog.exe`,
  198,414,032 bytes, SHA-256
  `4763b8ced28f8598c460c1f947bf1072ff3bb1855da9c6973fee8c8ec5145b4b`.
- Installed libks: `/clusterfs/mhg-data/yaoshen/qchem/trunk/lib/libks.so`,
  SHA-256
  `36a8f41a10d7541c25731be398ae270814dde7c5f23d2aeea52a6023e3b629a7`.
  It exports `libks::eval_integrated_dv(...)` and contains the environment
  variable and begin/end marker strings.
- `configure.log` records `./configure gnu openmp relwdeb`, GNU 10.5.0 for C,
  C++, and Fortran, OpenMP enabled, and installation into the trunk. The
  install manifest has 346 entries. `ldd` has 163 linked entries and zero
  unresolved (`not found`) dependencies.

## Runtime probe

A one-thread H2/STO-3G wB97M-V probe ran successfully with the new executable
and `QCHEM_PRINT_INTEGRATED_DV=1`. A second probe seeded and then read a Q-Chem
archive with `SCF_GUESS READ`, `MAX_SCF_CYCLES 0`, and `GEN_SCFMAN FALSE`.
Both calculations reached normal Q-Chem termination, and the archive-reuse
probe explicitly reported reading both MO coefficient sets, but neither output
contained `COACH integratedDV begin`, the matrix label, or
`COACH integratedDV end` (`begin=0`, `end=0`, `rows=0`).

The first attempted invocation inherited an unrelated `QCPROG` and therefore
selected the old `loco_os_yao` executable. It was discarded. All reported
results above use `env -u QCPROG` and explicitly show
`/clusterfs/mhg-data/yaoshen/qchem/trunk/exe/qcprog.exe` in the launcher output.

## Diagnosis and next gate

The feature implementation is compiled into `libks.so`, but the environment
check and emitter are located only in `ks_driver_exc::perform`. The normal
single-point SCF/fixed-orbital route evaluates XC through the Fock-building
path `fock_xc -> ks_driver_exc_fxc`, so the emitter is never reached. This is a
runtime call-path defect, not a missing or stale build artifact.

Do not mark Q2 complete and do not begin Q3. Route the opt-in integratedDV
evaluation through the actual fixed-orbital Fock path, preserve the 96x180
contract and MGGA refusal, rebuild using user-supplied commands, then repeat
the archive-read runtime probe and re-pin the resulting executable/libks hashes.
No production job was submitted and no authoritative orbital archive was
modified.
