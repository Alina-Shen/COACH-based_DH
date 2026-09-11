# Continuous K14 diagnostics approved — pre-test checkpoint

## Why semilocal coefficients remained zero

Established observation:25778785 returned exactly the supplied analytic start,
not a newly optimized zero-sem ilocal solution. All288 semilocal values and their
selection variables started0; final arrays are bytewise/numerically unchanged.
One incumbent, objective32.19152576324623Ha²,100% finite consistent gap and600s
TIME_LIMIT. The supplied Start values did not fix model variables at those values.
This is not evidence semilocal contributions are physically unnecessary or that
zero semilocal coefficients are optimal.

Possible contributors, not established diagnoses:

- Discrete search: using a previously unselected feature requires a compatible
  selection/continuous solution under linking constraints. Full-data search
  processed96nodes without a better incumbent; ten minutes may be insufficient.
  Neither more time nor a different start guarantees improvement.
- Weak relaxation: beta linking +/-25z permits fractional selections to represent
  many small coefficients without integer support. Such relaxations can give weak
  lower bounds for integer solutions. Sampled bound stayed3e-26; this observation
  does not prove whether weakness or numerical solution difficulty caused it.
- Near dependence/scaling: weighted A has numerical rank290/292 at the reported
  threshold and weights0.02–10000. Correlated directions, cancellation and strict
  tolerances can make continuous subproblems expensive. Last sampled iteration
  count~1.009million shows activity, not an identified internal bug or condition
  number of the actual optimization system.
- Constraint coupling: UEG links exchange coefficients and SR-HF, and bounds/
  selections must hold together. A useful direction can require coordinated
  changes rather than one independent coefficient. A sparse boundary start may
  be unhelpful for search; this is a hypothesis, not a local-minimum proof.
- Implementation/formulation/numerical behavior still merits inspection even
  though independent input/model/start audits passed. New exported subproblem
  models make such inspection possible without regenerating features.

Not supported by evidence: OOM/license failure, grid restrictions (none in this
discovery), mandatory semilocal zeros (none), exhausted support budget (4of14),
or proven optimality. Tiny L2 ridge is not by itself an explanation for all288
exact zeros: the entire start was simply retained. No weight normalization,
column removal, ridge change or altered constraints are authorized by this list.

Reference: [Gurobi numerical geometry guide](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/geometry.html)
explains how ill-conditioning can hinder continuous linear-system solves; applying
that explanation to this run remains a hypothesis.

## Implemented diagnostics

1. **fixed_scalars:** retain original full model and all linear constraints;
   fix semilocal selections0 and scalar selections1, convert selection variable
   types to continuous. Linking keeps semilocal coefficients0; UEG forces
   SR-HF1. Only VV10/PT2/D4 can meaningfully vary. Tests whether even this small
   continuous subset improves objective; cannot by itself diagnose feature search.
2. **relaxed_k14:** convert selections to continuous[0,1], retain mandatory scalar
   selections1, support sum<=14, linking, UEG, coefficient bounds and original
   weighted residual/ridge objective. No feature selection is rounded. A feasible
   relaxation solution is not an MIO incumbent; a nonoptimal QP objective is not
   automatically a certified lower bound.

Both use all1,498 entries, unchanged scientific model coefficients/weights/ridge,
no grid constraints (matching discovery),600s each,16threads,32GiB/90min serial
job envelope retained. Nominal solver allowance20min plus overhead, not forecast.
No automatic MIO retry, larger K or bulk fitting. Subproblems independent: a
normal first timeout without solution does not suppress the second; callback/
execution failures stop with saved evidence.

## New files / locations

- `scripts/continuous_k14_v1.py`:17 controlled type/bound changes;27 independent
  fractional/fixed-support/UEG/link/residual/objective audit;49/58 frozen plan/
  tested-commit/release gates;72 solve with model.mps.gz export, model dimensions,
  parameters/progress/results;107 license-free saved readback;136 serial run.
- `tests/test_continuous_k14_v1.py`:11 offline cases cover exact diagnostic
  configuration, feasible fixed support, fractional nonpromotion, violations of
  linking/support/UEG/scalar/residual/finiteness checks and disabled release.
- `slurm/run_continuous_k14_v1.sh`: separate16CPU/32GiB/90min launcher; template
  cm1 route awaits live review. Heavy output namespace fitting/continuous_k14_v1.
- `scripts/freeze_continuous_k14_v1.py`: hash-only freeze reuses unchanged
  historical dependency hashes, generates new `manifests/continuous_k14_v1/plan.json`
  and `release_draft.json`. Scope approved; submission/tests/resource flags false.

Original production code, scientific spec, matrices and failed/diagnostic outputs
are unchanged. Only hash-generation utility executed; no new tests, numerical
subproblem solves, WLS environment or submissions. Tests await pre-test commit.
Notes and STATUS updated. This is diagnostic model modification, not a new
production scientific specification or relaxed production acceptance criteria.

## Commit and next gate

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/scripts/continuous_k14_v1.py revwb97m2/scripts/freeze_continuous_k14_v1.py revwb97m2/tests/test_continuous_k14_v1.py revwb97m2/slurm/run_continuous_k14_v1.sh revwb97m2/manifests/continuous_k14_v1/plan.json revwb97m2/manifests/continuous_k14_v1/release_draft.json revwb97m2/results/2026-09-11-continuous-k14-pretest.md
git diff --cached --stat
git diff --cached --check
git commit -m "Prepare fixed-support and relaxed K14 diagnostics before tests"
```

Then tests and full-data readback, live partition review (no lr_lowprio), tested
commit release and the two approved diagnostic solves. Do not promote fractional
solutions or infer automatic authorization for longer MIO/full scan.
