# Step 1 complete — scientific specification and frozen step index

Date: 2026-09-12

## Contents

- [Specification](../configs/scientific_spec_v1.json)
- [Index](../configs/step_index_v1.json)
- [Freeze manifest](../manifests/scientific_spec_v1.freeze.json)
- [Validation](step1_validation.json)
- [Tests](step1_tests.json)
- [Database comparison](step1_database_comparison.json)
- [Inheritance audit](step1_inheritance_audit.json)

## Changes and reasons

1. Froze all 18 tracking IDs before implementing the specification. Renamed
   Step 5 for archive import, Step 9 for constraint implementation and Step 16
   for final model selection/freeze. Kept existing numbers, made LMP2 optional,
   and documented pilot-versus-full-data dependencies. The progress manifest
   can change without editing the frozen index.
2. Created authoritative `scientific_spec_v1.json`: fixed COACH parent and
   omega=0.27; zero new SCF; 292 feature columns with explicit polynomial order;
   fixed-energy partition; VV10/ATM/total-PT2 definitions; C0/UEG constraints;
   grids, data roles, weights, solver/audit tolerances and current K14–82 campaign.
   Future omega scan is optional/disabled until design choices are fixed.
3. Defined exact code/heavy/scratch write roots and read-only reference roots.
   Project notes are the only explicit extra write location. Symlink/path
   escapes are checked; no source project or shared environment is modified.
4. Recorded 35 reviewed source identities, including paper/SI, original COACH
   code, current reference implementations, metadata/weights and environment
   baseline. This is scientific provenance, not a full runtime dependency lock.
5. Compared the user-named GSCDB's three main metadata tables against the
   reference: byte-identical, with 8448 DatasetEval, 142 Datasets and 137
   Standard_errors rows. Full metadata-role and input validation stay in Steps
   3/4; these counts do not claim COACH archive coverage.
6. Independently checked inherited semilocal definitions (apart from declared
   omega/order metadata), data roles, dispersion, coefficient bounds and solver
   tolerances. Kept later implementation overrides for expanded objective,
   remaining-row grid selection and all integer K14–82.
7. Added a standard-library validator and 17 adversarial regressions. Tests
   cover omega mismatch, old parent/row/gamma contamination, energy/dispersion/PT2
   errors, scalar coupling/support errors, grid policy changes, holdout leakage,
   legacy campaign/objective settings, accidental runtime enablement, malformed
   JSON, hash changes, path traversal and symlink escapes.
8. Published a 14-artifact scientific hash freeze after tests and preflight,
   then passed 50 post-freeze checks. Wrote scientific/storage explanations,
   synchronized project-root documentation and recorded Step 1 completion in
   project notes. Existing dated chapters remain intact.

## Verification and limits

17 tests passed; 50 validator checks passed. Source hashes unchanged. Scientific
specification SHA-256:
`f4977550a9905cb630aaeea1039bffab0ae500f4ee86c627ecb10d3fb62e5aae`.
Index SHA-256:
`29383d65b257fa04d5b1d56cd4d75800aa0f8a335a9116aabcd281ca4ae590fa`.
The freeze is hash-based and is not a Git commit or a runtime release.

No Q-Chem/SCF/PT2 or Gurobi calculation, Slurm submission, orbital copy or
heavy numerical generation occurred. No reference files were changed. All
scripts and test temporary files stayed inside coach_mp2; Python used -B.
The native omega=0.27 kernel/input port and numerical identity gates are still
required, as are the actual supplied orbital method/version and denominator
checks. None of those reference-project successes were marked as COACH passes.

Next: Step 2, COACH baseline/source provenance. The orbital source path will be
needed for archive-dependent work in Steps 2/4/5. No scientific clarification
is outstanding for Step 1. Any later contradictory source evidence requires
a versioned amendment before dependent execution.
