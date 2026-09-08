# Approved ECP/storage correction and smaller-canary launch

User approved implicit-ECP correction and defined storage policy: retained data
under `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2`, disposable
scratch under `/clusterfs/mhg-data/yaoshen/scf_read/revwb97m2`. No separate quota
ceiling beyond available filesystem capacity. This resolves prior quota blocker.

## Changes and validation

- `v7_canary.py`: schema2 manifest pins basis bridge, exact case records and
  source/basis/ECP identities. MOR16_ed33 uses200explicit electrons with28removed
  core electrons from implicit_named_def2_ecp; no change to Q-Chem basis/input.
- External scratch routing: each retained stage's qcscratch is a checked link
  to its isolated scratch directory. Q-Chem cwd/QCSCRATCH/TMPDIR/TMP/TEMP all
  use scratch. Native inputs/outputs/launch logs remain in the retained tree.
- Startup headroom check uses the minimum of the two destinations' free space,
  not their sum; checks again before copies. This does not reserve disk or
  predict all Q-Chem growth. No automatic cleanup; working-qarchive evidence
  is still needed by readback. Atomic final-array staging is retained-data work.
- Launcher Slurm logs now go under the data root's logs directory.
- Added implicit-ECP identity/mismatch, real MOR16 count, scratch-link overwrite
  refusal and native cwd/temp routing regressions; updated scratch readback test.
- **114 tests passed in4.80s**. Config validation, bash syntax and whitespace
  checks pass. Existing110test result did not validate these corrections.

No changes to historical drivers, scalar defaults, solver/scientific settings,
old artifacts or authoritative archives. Corrections are uncommitted on top
of b8736a7, explicitly recorded by plan code hashes. No commit/push/rebuild.

## Freeze and storage

Seven-case freeze/load now passes. Plan:
`manifests/production_generator/v7_canary_v1.json`;
SHA2569b8e9982da58d61ab0e0ba9c237d4e5e7b33cf764ffd1f7172f4e4b51bacf7be.
Copy-only lower bound24.314176807GiB; free space at verification
2753366746726400bytes (~2.5PiB), same filesystem for both roots.
Retained root: `coach-based_dh_data/revwb97m2/species/v7_canary_v1`.
Scratch root: `scf_read/revwb97m2/v7_canary_v1` (both under /clusterfs/mhg-data/yaoshen).

## Submitted smaller cases

Used partition skill: live mhg idle nodes, physical memory exceeding all five
requests, valid mhg/normal association and sufficient walltime policy. Allfive
sbatch test-only checks passed. Independent jobs, no globaltwojobcap:

| Job | Species | CPUs | GiB | Wall cap |
|---|---|---:|---:|---:|
| 25680429 | TMD01_H | 8 | 14 | 72h |
| 25680433 | S22_06b | 8 | 21 | 72h |
| 25680434 | HR46_N-methylacetamide | 8 | 35 | 72h |
| 25680435 | HR46_toluene | 8 | 62 | 72h |
| 25680436 | 3019_41UracilPentane090_dim_S66x8 | 8 | 117 | 72h |

Allfive RUNNING at initial14s check. Subsequent check: TMD01_H COMPLETED0:0
in56s; separate CLI species validation passed. Otherfour RUNNING at1m29s.
Confirmed physical scratch symlink routing and H saved-orbital electron evidence.
No fullcohort completion claim. No automatic
retry or dependent large-case launch. BSR36_c4 and MOR16_ed33 await small-case
result review. No new SCF, no fullpopulation feature generation or bulk fitting.
