# Recovery tests passed; execution checkpoint prepared

## Completed this turn

- Verified clean commit194beea. Full committed suite306 passed in16.76s (dh environment, BLAS/OMP/MKL threads1).
- Ran real-data continuous_readback_v2 against job25783741. Fixed=true, relaxed=false reproduced; independent fixed-support MIO audit passed and full-primal start exported to `2026-09-11-continuous-v2-readback.json`. Original artifacts/producer unchanged.
- Added solver_recovery_v1 runner: two precision variants (BarConvTol1e-12; same plus NumericFocus3) and independent7200s K14 MIO confirmation importing all coefficients, selections and residual starts. Scientific objective/weights/ridge/constraints unchanged. Writes effective parameters/model export/progress/solution/quality/audits; MIO additionally bounds/gaps/start improvement. No automatic retries or full scan.
- Added guarded hash-only freezer, disabled release, two Slurm launchers and four test cases covering variant parameters, disabled release, complete primal import and invalid-start rejection. These NEW tests are not yet run;306 refers to committed reader checkpoint.
- Precision job:16CPU/32GiB/90min, two600s caps. MIO job:16CPU/32GiB/3h scheduler limit for one7200s solve plus setup. Both currently cm1/lr_qchem/condo_qchem. Jobs are independent; no afterok dependency on the relaxation, whose fractional result is never a MIO start.
- Partition helper missing; used direct live sinfo/squeue/sacctmgr. cm1 five idle241732MiB nodes, mhg four idle515986MiB, lr8 four idle773569MiB. Empty user queue. cm1 physical memory exceeds32GiB and association valid; no lr_lowprio.
- Both scheduler dry-runs passed, predicting immediate placement. Numbers25783961/25783962 are TEST-ONLY scheduler responses, NOT submitted jobs. Bash syntax passed. No actual sbatch submission.
- Freeze requires the NEW runner/launchers/plan/start report committed and tested before release. User's latest commit contained the reader, not this execution code. Stop with explicit commit commands; after commit run full suite, refresh live resource review, release and submit both jobs. No additional algorithm development intended at that submission checkpoint unless tests expose a defect.

## Terminology

| Term | Meaning here / purpose |
|---|---|
| Numerical-accuracy discrepancy | Solver OPTIMAL versus independently recomputed UEG error5.608e-10 >1e-10 and weighted-residual identity error7.214e-8 >1e-9. Distinct from readback's ~1e-15 scalar roundoff, now handled by the new reader. |
| MIO candidate | A particular coefficient vector plus discrete selected-term set returned by a mixed-integer solve. Only independently accepted candidates are eligible for scientific comparison; an incumbent is the best feasible candidate found so far, not proof of global optimality. |
| Improved-start import | Load the audited four-scalar solution into Gurobi's Start attributes for coefficients, selection variables and residuals; check its feasibility again and verify solver acceptance. It guides search but does not fix the final support or guarantee improvement. |
| Larger-support | Test a higher term budget, e.g.K80 rather thanK14: up to76 rather than10 semilocal terms, plus four mandatory scalars. Same292 feature columns and1498 entries. |
| Grid-constrained | Add inequalities limiting energy changes between numerical integration grids for selected training rows, using the approved0.015kcal/mol bound/internal margin. This is numerical quadrature stability, not a parameter grid search. |
| Restart path | Save a candidate and begin another solve from it, checking state/parameter/provenance import and independent output. It is a new solve, not resuming Gurobi's entire branch-and-bound tree and not rerunning SCF. |

## Why not simply launch the full COACH-style fit?

There is no mathematical prohibition, no missing training matrix and no requirement for zero gap. The approved scientific protocol already follows COACH where specified (basis choice, ridge, training weights, model-size comparisons/repeats and grid-stability pass). Our gates are engineering validation, not additional COACH physical constraints. A failed fractional relaxation is not itself a compulsory final-fit criterion if accepted discrete solutions are independently valid.

However this is not the identical COACH executable/model:292 rather than289 features, additional independently fitted PT2/VV10/D4 terms, different retained constraints, explicit residual formulation and selected-variable linking. Original COACH success cannot establish correctness of this adapter/import/grid/restart implementation. Recent real-data runs exposed a reader defect and numerical discrepancies; launching every size/repeat now would replicate unvalidated behavior. The two-hour improved-start run is genuine full-data fitting at one model size, not another chemistry-generation test. It advances toward the production scan while keeping output independently checked.

COACH's local Optimization.md specifies1–2h per subset size, one restart,16cores; our7200s confirmation is comparable in wall-time scale. It tests longer search plus a better start, NOT a controlled time-only comparison. It does not guarantee a small gap. The relaxed solve's0.907s OPTIMAL exit was not a600s timeout.

Remaining after these jobs: evaluate candidate accuracy/improvement/gap and numerical diagnostics; validate K80/grid/restart full-data sequence; freeze production candidate union/starts/resources and obtain pre-bulk commit/launch approval. Do not keep adding unspecified tests: these are the existing finite gates.
