# Full 1,498-entry numerical matrix accepted — September 10, 2026

## Outcome

PASS: **1,498 entries x 292 features**, exactly **2,799 species**, all **49**
COACH Cycle-2 fitting groups. All 100 accepted pilot rows match exactly across
all seven arrays. Species generation and full numerical assembly are complete;
no full-data optimizer execution or bulk fitting occurred.

Matrix directory:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/matrices/full1498_v1`

Validation SHA256:
`493a6a465ea71539e291501645d6a186ffd86f1bd597174035d6fe7c1675eef8`

## Work performed and reasons

1. Added a versioned assembler outside the frozen top-level package dependency
   glob. Historical native readers and manifests were not edited or bypassed by
   monkey-patching; accepted pilot publications are consumed explicitly by hash.
2. Rechecked metadata checksums and reconstructed the training definitions from
   the original entry, DatasetEval and role tables. Verified order, stoichiometry,
   Hartree references, original Cycle-2 objective weights and fitting-only roles.
   Historical metadata readiness annotations are preserved as history, not used
   as current readiness claims.
3. Bound the 2,569 generated publications to the accepted final native audit and
   frozen campaign/plans. Rechecked publication identities, completion markers
   and every published artifact hash. This uses the just-completed full raw audit;
   it does not rerun all 15,412 native stages.
4. Explicitly ingested the 230 accepted reuse sources: earlier pilot generic
   publications, 38 corrected legacy fixed-energy records, corrected water/Y
   publications, and seven corrected canaries (one belongs to the pilot; six are
   additional reuse). Fresh canary readback passed. The 224 pilot species retain
   their exact accepted source interpretation, including legacy corrections.
5. Assembled feature, fixed, reference, target and weight arrays plus both
   grid-difference matrices. Target remains reference minus fixed energy.
   Independently checked each energy/grid channel with a stoichiometry matrix.
   Existing tolerances retained: rtol1e-12, atol2e-10. All arrays finite; scalar
   grid differences remain zero, including the documented SG1-only VV10 policy.
6. Required exact equality with all 100 accepted pilot rows, not approximate
   agreement. Published sources.json with per-species source/artifact hashes and
   explicit corrected fixed energies, reactions/species lists, validation and
   completion marker, and a real fitting-input manifest accepted by load_inputs.
7. Added 11 unit cases and ran the complete suite: **256 passed in12.46s**.
   Tests cover sums/targets/weights, missing/extra/partial scope, wrong groups,
   duplicate reactions, nonfinite vectors, altered scalar grids, invalid weights,
   exact pilot mapping/mutation rejection and refusing existing outputs.
8. Ran a fresh-process audit that rechecked all bound files and independently
   reconstructed every matrix channel with math.fsum, rather than either the
   production accumulation loop or matrix multiplication. Real loader readback,
   source closure, and exact pilot comparison passed again.
9. Updated project notes and STATUS's current table and Steps14/17. No jobs,
   Q-Chem rebuild, SCF, solver calls, scientific-setting changes, deletions or
   historical publication overwrites.

## Numerical evidence

| Channel | Maximum error: independent S@X | Maximum error: fresh math.fsum |
|---|---:|---:|
| Features | 4.974e-14 | 4.263e-14 |
| Fixed energy | 7.958e-13 | 5.560e-13 |
| Grid99590 | 5.421e-20 | 5.421e-20 |
| Grid75302 | 6.939e-18 | 7.589e-19 |

These are floating-point assembly/readback differences in Hartree-valued channels,
not fitting errors, chemical accuracy estimates or solver gaps.
See [independent audit JSON](./2026-09-10-full1498-matrix-independent-audit.json).

## Added code and locations

| File | Lines / purpose |
|---|---|
| scripts/assemble_full1498_v1.py |23 metadata/source/role checks;50 accepted-source ingestion;149 independent assembly;178 exact pilot comparison;186 strict readback;213 publication;251 CLI. |
| scripts/audit_full1498_matrix_v1.py |10 fresh-process audit, source closure and independent math.fsum reconstruction;43 CLI. |
| tests/test_full1498_assembly.py |21 numerical test;29 rejection cases;44 exact pilot regression;52 overwrite guard. |

Existing production code and frozen contracts were not modified. New diagnostic
and assembly code is uncommitted pending the user's commit.

## Next step and limits

Stop for the user's commit. Afterward, prepare/review the full-data optimizer
integration and bounded validation plan, followed by the pre-bulk specification,
code/matrix freeze and explicit model-size/resource scan approval. The existing
100-entry launcher remains pilot-specific and is not silently pointed at full
data. COACH ridge/model-selection protocol and user-review gate remain intact.
Outstanding solver-gap/optimality and final-selection decisions remain in STATUS;
this numerical acceptance does not resolve them or certify an optimum.

Commit from `/clusterfs/mhg-data/yaoshen/coach-based_dh`:

```bash
git add -- revwb97m2/scripts/assemble_full1498_v1.py revwb97m2/scripts/audit_full1498_matrix_v1.py revwb97m2/tests/test_full1498_assembly.py revwb97m2/results/2026-09-10-full1498-matrix-accepted.md revwb97m2/results/2026-09-10-full1498-matrix-independent-audit.json revwb97m2/results/2026-09-10-final-generation-audit.json revwb97m2/results/2026-09-10-final-generation-audit.md revwb97m2/results/2026-09-10-final-generation-audit.py
git diff --cached --stat
git diff --cached --check
git commit -m "Validate full1498 training matrix and preserve generation acceptance"
```

The explicit file list leaves earlier September9 untracked reports untouched.
Heavy arrays stay in the approved data directory; project notes are outside this
repository and are not included by this commit command.
