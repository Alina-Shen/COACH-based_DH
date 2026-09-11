# Approved K14 diagnostic recovery — pre-test checkpoint

## What incumbent means

For this minimization, an incumbent is the best feasible coefficient/support
solution Gurobi has found and retained so far. It obeys the model constraints
but need not be globally optimal or scientifically useful. A lower objective
feasible solution improves the incumbent; the bound describes how good an
optimal solution could still be. Their gap concerns optimality, not feasibility.
Job25778194 had zero incumbents: no accepted feasible solution within600s, not
proof no feasible solution exists. An independently checked vector supplied as
a MIP start is not automatically a solver incumbent: its acceptance must be
observed. A start can help but provides no runtime guarantee.

## Implemented changes and explanations

- Added `scripts/k14_diagnostic_v1.py`, a separate one-solve full1498/K14 workflow.
  Preserves frozen pilot/full1498 drivers, scientific spec, matrix and failed run.
 600s,16threads,32GiB,90min allocation unchanged. No grid constraints in this
  discovery diagnostic; no automatic cold rerun, six-solve retry or bulk scan.
- Line29: deterministic feasibility start:288 semilocal coefficients0,SR-HF1,
  VV10/PT2/D4 each1e-8; selectfour scalars. Rechecks independent model feasibility,
  calculates all1498 weighted residuals, supplies all primal start variables,
  saves coefficient/selection/residual arrays and audit with explicit non-incumbent
  label. No protected data or earlier pilot coefficient identity is imported.
- Lines20/64: strict-JSON diagnostics for finite/nonfinite/sentinel numbers and
  throttled presolve/simplex/barrier/MIP progress, bound/node counts and solution
  events. Start messages are allowlisted; general/license text is not captured.
  Callback errors terminate and remain explicit, rather than silently disabling
  logging. A MIPSOL event is not mislabeled as proof of final acceptance.
- Line91: saves model dimensions, build/start timing, version/parameters, progress
  and final status/bound even when solution_count=0. If present, saves solver
  coefficients, independent SSE/ridge/objective/constraint audit, gap and both
  grid maxima. Does not manufacture an incumbent/gap on no-solution timeout.
- Lines39/50/140/181: frozen code/matrix, committed tested release and route
  gates; private compute-only WLS initialization; source/seed/model/parameter/
  solution/gap/grid readback with no license environment. Distinct diagnostic
  completion marker is evidence completion, not six-solve or scientific acceptance.
  Outputs are nonoverwriting and preserve failures.
- Added `slurm/run_k14_diagnostic_v1.sh`: same16CPU/32GiB/90min resource envelope,
  new diagnostic log/output namespace. cm1 template awaits live route review.
- Added `tests/test_k14_diagnostic_v1.py`:10 offline cases for full-data seed
  algebra, nonfinite/sentinel serialization, disabled release, message filtering,
  callback-failure stop and overwrite refusal. Existing tests remain regression
  coverage. Tests are **not run yet**, preserving the user pre-test commit gate.
- Added hash-only `scripts/freeze_k14_diagnostic_v1.py`; generated new plan and
  disabled release draft in `manifests/k14_diagnostic_v1`. Frozen historical
  plan/dependencies inherited by hash, never rewritten. Only hash-generation
  utility executed, not the diagnostic or tests; no new WLS session/submission.
- Updated project STATUS and notes with approval, incumbent explanation and
  pre-test stop. Internal cause of prior no-incumbent timeout remains unresolved.

Implementation references: [Gurobi callback codes](https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/callbacks.html)
and [MIP-start guidance](https://support.gurobi.com/hc/en-us/articles/360043834831-How-do-I-use-MIP-starts).

## Next gate

User commits, then run new/full tests and real-data seed/readback checks without
solving. If passing, fresh live partition/resources and gated release precede
the approved single diagnostic solve. Investigate start acceptance and progress
before proposing longer runs or restarting all six solves. A poor starting
incumbent alone is not a useful fit, small gap or cleared production gate.

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/scripts/k14_diagnostic_v1.py revwb97m2/scripts/freeze_k14_diagnostic_v1.py revwb97m2/tests/test_k14_diagnostic_v1.py revwb97m2/slurm/run_k14_diagnostic_v1.sh revwb97m2/manifests/k14_diagnostic_v1/plan.json revwb97m2/manifests/k14_diagnostic_v1/release_draft.json revwb97m2/results/2026-09-11-k14-diagnostic-pretest.md
git diff --cached --stat
git diff --cached --check
git commit -m "Prepare K14 feasible-start diagnostics before tests"
```

Explicit scope leaves earlier untracked release/audit reports untouched; preserve
them. Project notes lie outside this repository and are saved separately.
