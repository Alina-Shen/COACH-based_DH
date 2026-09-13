# COACH MP2 storage and write boundaries

## Contents

- [Scientific contract](../configs/scientific_spec_v1.json)
- [Code-root README](../README.md)
- [Heavy-root README](../../../coach-based_dh_data/coach_mp2/README.md)
- [Q-Chem scratch README](../../../scf_read/coach_mp2/README.md)

User-frozen write scope:

| Root | Purpose |
|---|---|
| `/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2` | Scripts, settings, manifests, tests, documentation, important lightweight results. |
| `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2` | Numerical arrays/checkpoints, processed matrices, optimizer artifacts, full logs and heavy build artifacts. |
| `/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2` | Isolated Q-Chem scratch folders and verified working archive copies. |

Explicit exception: project notes under
`/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh`.
Reference COACH/revwb97m2/GSCDB sources and source orbital archives are read-only.
Do not write task staging files to /tmp or edit shared Q-Chem/environment source.
If a later Q-Chem change is needed, prepare its patch/source/build inside project
roots; shared-tree modification is outside this project's allowed scope.

Resolve output paths before writing; reject symlink and sibling-prefix escapes.
Publish successful stages atomically without overwriting validated artifacts.
Store spec/input/code/archive/omega identities with artifacts. Never use scratch
as the sole copy of a reproducibility-critical manifest. A species name or
292-column shape is not sufficient cache identity.

Step 1 introduces no heavy numerical data or archive copies. Future heavy
subdirectories are species/, processed/, optimization/, logs/ and build/ as
needed; Q-Chem working directories live under the designated scratch root.
General temporary files for tests must remain in the code project's tests/
subtree, with Python bytecode disabled when reading reference code/packages.
Keep root READMEs synchronized with actual structure and purpose changes.
