# Big-M retained, semilocal test submitted, expanded comparison prepared

## Decisions and execution

User confirms big-M remains the selection formulation; SOS1 is a deferred future test, not a current change. Four COACH-seed semilocal columns means using the support of COACH's built-in seed (exchange00/exchange01/SS00/OS00), refitting coefficients under our constraints with four DH scalars, then using the independently valid solution to start MIO. It is not literal copying of historical COACH coefficients.

Committed35b867a passed324 tests in16.58s. Real full1498 semilocal witness and frozen commit hashes passed. Live cm1 five idle241732MiB nodes,valid account/QOS,empty queue,2.5PiB filesystem free; no lr_lowprio. Submitted seven-case search diagnostic25787074 with16CPU/32GiB/3h.

Job25787074 started11:49:10PDT and FAILED1:0 after16s BEFORE optimize. It wrote identity/model.mps.gz and empty qp_dual/model.json, no progress/result files; failure.json recordsValueError. The model metadata newly includes NodeLimit=Infinity, rejected by the strict allow_nan=False JSON writer. [Official parameter reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html) confirms its unlimited default. This is a metadata serialization failure, not fitting or license failure. Prior offline tests did not exercise actual model metadata serialization; add regression coverage. No results for semilocal fit yet.

## Versioned correction

Preserved original v1 code/plan/artifacts; new search_diagnostic_v2.py changes only plan location and parameter encoding: finite settings unchanged, nonfinite parameter values represented by explicit numeric state/null. Same seven cases,science,resources. New9-case test file,launcher and hash freeze/disabled release. No automatic retry submitted. Test and retry after user commit.

## Expanded quadratic test

New expanded_objective_v1.py builds the same292-coefficient,big-M model, then replaces residual objective/variables/equalities with `beta.T Q beta -2 linear.T beta + constant`, where `X=sqrt(w) A`, `y=sqrt(w)b`, `Q=X.T X+1e-10 I`, `linear=X.T y`, `constant=y.T y`. This is twice COACH code's entire half-SSE objective, so normalization/ridge are held fixed against our baseline. No SOS1,modified physical constraints or automatic production adoption.

Residual model2082vars/2088constraints; expanded584vars/590constraints,292binaries in MIO; assertzero SOS. Removing1498 residual equations does not remove scientific constraints: they define eliminated residual variables. Saved models/arrays and independent direct weighted-SSE audit check cancellation/error; recomputed residuals are explicitly labelled, not presented as solver residual variables.

Three matched cases,600s each,16CPU/32GiB/90min job:

1. residual_mio: fresh explicit-residual MIO control;
2. expanded_qp: expanded continuous relaxation,Method2/BarConvTol1e-12,reference accuracy;
3. expanded_mio: expanded MIO, otherwise same default solver settings as control.

Both MIO cases use the SAME frozen optimized four-scalar start, not the pending semilocal fit. This isolates representation and avoids confusing a start change with objective change. The separate search diagnostic tests semilocal starting support. Expanded objective may improve presolve/search or worsen conditioning/cancellation; no outcome assumed. Five prepared algebra/gradient/normalization/release tests. After commit also verify actual model dimensions, unchanged feasible constraints and objective agreement on real data before release.

## Handoff

New tests/solves NOT run before commit. Hash-only freezes/bash syntax checked; all historical source files unchanged. Next: commit correction+expanded checkpoint,run full suite and real preflight/live resource review,then submit corrected seven-case diagnostic and independent expanded comparison. Production scientific_spec unchanged; SOS1 deferred in project STATUS. Job25787074 never reached solving, so it cannot provide evidence for or against a semilocal start.
