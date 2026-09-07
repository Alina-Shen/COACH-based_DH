# Q6 Q-Chem resource pilots and Step-13 regeneration complete

Date: 2026-09-05

## Outcome

Q6 passes. All three frozen small/medium/high pilot roles have complete,
validated Q-Chem imported-orbital integratedDV boundaries on grids 250974,
99590, and 75302, plus frozen geometry-only D4-ATM measurements. The immutable
initial 2,799-species Step-13 plan was generated and remains explicitly
non-submitting. Q7 bulk production is not authorized.

## Accepted terminal jobs

| Role | Species | Job | Attempt | State | Elapsed | Peak RSS | Request |
|---|---|---:|---|---|---:|---:|---:|
| small | 3d4dIPSS_Ag_GS | 25562223 | original | COMPLETED 0:0 | 00:01:23 | 1,899.37 MiB | 14 GiB |
| medium | TMB28_C1 | 25581129 | retry2 | COMPLETED 0:0 | 00:09:16 | 6,022.21 MiB | 62 GiB |
| high | MOR32_pr24 | 25582472 | retry2 | COMPLETED 0:0 | 10:43:03 | 46,905.40 MiB | 557 GiB |

The medium retry reused its already validated 250974/99590 boundaries and ran
only missing 75302 work. The high retry ran all three grids in 17,061.79,
11,290.00, and 10,127.68 seconds. Every accepted Q-Chem output reports that
the imported orbitals are not altered, contains one complete 96x180
integratedDV block, and ends with normal Q-Chem termination.

All failed/cancelled attempts remain recorded in
`revwb97m2/manifests/qchem_gateway/q6_slurm_accounting_v1.json`. The repeated
medium allocator abort and original high MKL segfault were not OOM. Both were
avoided by the frozen fixed-orbital control `MP2_RESTART_NO_SCF TRUE`, which
skips unnecessary post-Fock diagonalization without changing the imported
density, functional, grids, integratedDV equations, or tolerances.

## Resource decision

Measured 2x-peak-plus-2-GiB Q-Chem-grid references are 6, 14, and 94 GiB for
the small, medium, and high pilots. They are observations, not production
limits: only three cases cover three of seven inventory memory classes, and Q6
does not measure the still-gated same-archive VV10 or RI-MP2 stages.

The frozen decision therefore retains the existing Step-12 per-species
partition/account/QOS, CPUs, memory, walltime, and concurrency assignments for
the initial Step-13 plan. This is deliberately conservative and makes no
unmeasured cross-class or cross-stage extrapolation.

## Immutable artifacts

- Q6 Slurm accounting: `revwb97m2/manifests/qchem_gateway/q6_slurm_accounting_v1.json`, SHA-256 `b26ff5b812175dcacdd2a685b490007c90bba3c41544ca3795f90b665392147f`.
- Resource guidance: `revwb97m2/manifests/qchem_gateway/q6_resource_guidance_v1.yaml`, SHA-256 `adb0b3d5976cfed9c95c89737288ba01d47004ad9bf3d63668483eaa66030dc5`.
- Initial Step-13 plan: `revwb97m2/manifests/production_generator/step13_qchem_initial_plan_v1.json`, SHA-256 `fa4412f94bb88c8acda9f97c463fb33d0b612cafb9d222064be4caaed3f7eb28`, plan ID `4238aed395a11b6e`, 2,799 species, eight boundaries each, `submission_authorized: false`.
- Aggregate validation: `revwb97m2/manifests/qchem_gateway/q6_validation_v1.json`, SHA-256 `d57f19c1fd8cb2d7bfeae4e77e2bec12726f8af32e9c1b43364fdce376d83ac4`.

## Validation

- Q6 aggregate: all 11 aggregate checks pass; all per-case, per-grid, source,
  restart, D4, Slurm, resource, and Step-13 checks pass.
- Repository tests: 48/48 pass.
- Scientific specification v6: 189/189 checks pass.
- Resource-neutral full-population Step-13 validator: 14/14 checks pass over
  17,452 species and 139,616 boundary states.
- Python compilation, Slurm script syntax, and `git diff --check` pass.

## Remaining gates

Q6 completion does not authorize production. Step 9 must still implement and
validate VV10 and RI-MP2 from the same imported Q-Chem archive, Step 13 must
finish its production adapter around all eight boundaries, and Q7 requires a
separate explicit user approval before any bulk submission.
