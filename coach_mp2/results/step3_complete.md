# Step 3 — immutable data roles and metrics

Completed 2026-09-12. Solver choice is not required: no solver was installed,
invoked or selected, and no license session or cluster job was used. The frozen
scientific contract retains its historical Gurobi setting; the user has deferred
backend selection. Pause before implementing a backend-dependent optimizer route
(Step 14), or earlier if a backend-specific choice actually arises.

## Work completed and rationale

1. Read the Step 1 scientific contract, latest reference role/weight manifests,
   builders, COACH final-cycle SI transcription and benchmark analysis code.
   No existing reference results or inputs were changed.
2. Verified byte identity of seven current GSCDB metadata tables against the
   pinned reference: five core Info tables and BigNC/GDB9-W1-F12 DatasetEval.
   Copied these into the project-local source snapshot and recorded source hashes.
3. Independently expanded all 49 final-cycle SI selection/weight rows into the
   exact 1,498 ordered fitting entries. Preserved partial subset ordering,
   constants, and AE18 weight 1/sqrt(j). Weights multiply squared residuals:
   a least-squares matrix uses sqrt(weight), not weight. Historical Cycle-1
   weights are not a fitting input.
4. Rebuilt 11,839 reaction-role rows and exact stoichiometry/reference/order,
   17,452 species-role rows, and 142 dataset-role rows. Compared every role and
   fitting weight with revwb97m2. Preserved reference species/dataset order too.
5. Verified metadata species membership against the current core and three
   AdditionalSets Allmols_info files and the reference metadata table: 17,658
   total, including 206 OPT species excluded from the energy domain. This checks
   membership only; Step 4 still validates actual molecular input chemistry.
6. Recorded intentional overlap and protected final assessment at the reaction
   level. There is no random split or silent exclusion. Fitting and selection
   overlap; MB16-43 contributes 43 fitting/diagnostic rows. Final reactions are
   disjoint, but 6 species overlap fitting/final and 28 overlap selection/final.
   Shared species do not authorize use of final reaction errors in model choice.
7. Implemented a solver-neutral metric evaluator for already transformed benchmark
   values. Most datasets use MAE; Pol130/HR46/T144/OEEF use MARE; Dip146 uses
   the |reference| floor of 1; TMD10/MOR13/TMB11 use weighted absolute sums plus
   their published offsets; O24/O24x4 use weighted absolute sums. NER divides
   by Standard_errors.Metric. Overall NER is the equal mean over all 137 datasets,
   not an equal mean of category averages. The diagnostic averages its three NERs.
8. Distinguished this adopted benchmark policy from the generic COACH Python
   helper's all-RMSE analysis. Validated the adopted rules independently against
   all 137 COACH paper-workbook development NERs: maximum difference
   1.7676971e-12; reproduced overall mean 0.9367424523440216. No final-only
   benchmark results were scored or used to choose a model.
9. Added 18 tests for metric branches, missing/duplicate/nonfinite records,
   invalid normalizers, final-set injection, aggregation, altered weights,
   row reordering/removal, stoichiometry and species-role corruption.
10. Passed 79 semantic checks, recorded the metric oracle results, rechecked
    Step 1, froze the Step 3 artifacts by SHA-256, and updated the live plan table,
    progress manifest, README and dated project notes. Step IDs remain unchanged.

## Frozen role counts

| Role | Reaction/property rows | Unique species |
| --- | ---: | ---: |
| Coefficient fitting | 1,498 | 2,799 |
| Model selection: 137 datasets | 8,377 | 13,907 |
| Overfitting diagnostic | 219 | 249 |
| Final assessment | 3,462 | 3,573 |

Final assessment comprises SC74/OEEFD (71 rows), BigNC L14/vL11 (25), and
GDB_W1-F12 (3,366). These values cannot influence coefficients, sparsity or
functional design. Retain the caveat that original COACH tuned ATM on BigNC.
The reference policy reports GDB final MAE, mean signed error, and population SD.

## Artifacts and limits

`manifests/data_roles_v1/` holds local source tables, exact role CSVs,
`policy.json`, and source provenance. `manifests/step3_freeze_v1.json` pins the
artifacts. `scripts/build_step3_roles.py` is a non-overwriting builder (existing
dh environment/PyYAML); the validator and metric tools need only Python stdlib.
`results/step3_roles_validation.json`, `step3_metrics_validation.json`, and
`step3_tests.log` record the checks. Recheck with:

    python3.9 -B coach_mp2/scripts/validate_step3_roles.py

This does not claim orbital coverage, feature readiness or property-transform
validation. Metrics consume benchmark reporting units; Step 13 must implement
and validate the finite-field/frequency/property transformations before using
molecular energies. No solver-dependent experiment or candidate selection was
performed. All writes were confined to coach_mp2 and project notes.

Next stable step: 4, molecular input and basis authority.
