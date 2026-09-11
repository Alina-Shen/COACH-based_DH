# K14 diagnostic25778785: accepted start, no fitting improvement

## Outcome

Slurm COMPLETED0:0,elapsed10m21s,ended00:50:18PDT. Peak batch RSS2,754,236KiB
(~2.63GiB), within32GiB. Gurobi TIME_LIMIT/status9 after600.0869s,96 final nodes,
one incumbent. No callback errors; stderr empty. Independent license-free CLI
readback passed, including publication/code/release/matrix/seed/parameter and
incumbent/objective/gap/grid checks. Diagnostic completed correctly; this does
not certify a useful fit, optimum, six-solve acceptance or production readiness.

## What changed during the solve

Nothing in the accepted coefficients: final coefficient and selection arrays
are exactly equal to the supplied analytic start (maximum coefficient change0).
All288 semilocal coefficients remain0;SR-HF1;VV10/PT2/D4 each1e-8. Selected4
scalar features, within K14. The solver accepted the start but never improved it.

| Quantity | Final value |
|---|---:|
| Weighted SSE (Ha²) |32.19152576314622|
| Ridge penalty (Ha²) |1e-10|
| Solver objective (Ha²) |32.19152576324623|
| Lower bound (Ha²) |3e-26|
| Raw/recomputed relative gap |1.0 =100%, consistent|
|99590/75302 grid maxima (kcal/mol) |0 /0|

The zero grid differences are trivial for this scalar-only start: all semilocal
coefficients are zero and scalar difference columns are defined zero. They do
not demonstrate a useful grid-stable optimized functional. In particular VV10
is SG1-only and its zero difference is not independent VV10 convergence evidence.

Progress contains1start-acceptance message,1solution event,1presolve record and
14MIP samples. All sampled incumbents remain32.19152576324623 and bounds3e-26.
Last sample~600.062s reports52nodes and1,008,702 simplex iterations; final model
reports96nodes. Callback samples and final totals are not identical timestamps,
so this difference is not itself corruption. Counters show solver activity,
not why the search failed to improve. No bound tightening observed in samples.

## Interpretation and recommended next diagnostic

The start mechanism works, eliminating the immediate zero-incumbent outcome
without changing the feasible model. It has not solved the substantive search
problem. The finite100% gap is consistent; it is distinct from historical
raw-infinite gap reporting discrepancies. Internal numerical/search cause remains
unresolved. Not OOM, scheduler deadline or license failure. More memory is not
supported as the remedy; a longer unchanged solve is not guaranteed to help.

Recommend separately approved, bounded continuous-subproblem diagnostics before
relaunching the six-solve workflow:

1. Optimize coefficients with support fixed to the existing four-scalar start,
   retaining original objective, bounds and UEG. This tests continuous optimization
   on a simple feasible subset and may yield a better valid start. It is not
   final scientific model selection or a permanent restriction to four terms.
2. Solve the continuous relaxation of the full K14 model (relax selection
   integrality while retaining the same linear constraints/objective). Compare
   numerical progress and objective/bound evidence to separate continuous-solver
   behavior from discrete feature selection. Fractional selections are diagnostic,
   never a valid MIO incumbent or automatically imported as a start.
3. Based on evidence, propose a validated stronger start, targeted solver/support
   investigation or a longer bounded MIO retry. No automatic parameter changes,
   removal of feature columns, new constraints or bulk release.

These are recommendations, not implemented or authorized new solves. Only read-only
result checks and report/note/status writes performed this turn; no production code
changes, license initialization, resubmission or chemistry. Full matrix remains
accepted; K80 and full-data constrained/restart behavior remain untested.

[Machine-readable independent audit](./2026-09-11-k14-diagnostic-independent-audit.json).
