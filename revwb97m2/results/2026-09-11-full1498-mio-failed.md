# Job25778194: no-incumbent timeout, bounded test not accepted

## Results

Slurm FAILED1:0 after00:10:55, ending September11 00:22:08PDT. Batch MaxRSS
1,168,396KiB (~1.11GiB), far below32GiB;90min allocation was not exhausted.
Synthetic control passed. The first real solve, discovery14, returned Gurobi
status9 (TIME_LIMIT),600.0456s,zero incumbents and26 processed nodes. No accepted
coefficients or grid rows were published. The orchestrator intentionally stopped
with ValueError; discovery80 and the four constrained/restart solves never ran.
No PILOT_COMPLETE marker. Empty stderr does not imply successful fitting.

## Checks performed

Read scheduler accounting, stdout/stderr, failure record, contract, result and
telemetry. Independently verified release/committed code/plan/input identities,
full1498 source/matrix readback and earlier pilot-row identity, synthetic report,
correct first-solve configuration and absence of later outputs. Evidence checks
PASS; the actual bounded fitting workflow FAILS its incumbent acceptance gate.
No optimizer, WLS session, new chemistry or resubmission was executed during audit.

Saved parameters were16threads,600s,seed0,FeasibilityTol/IntFeasTol1e-9,
MIPGap1e-4,MIPGapAbs1e-10,Gurobi13.0.3. The first solve has no grid constraints
and no warm start: full-grid advancement checks did not cause this failure.
This is not an OOM, license startup failure or90min scheduler timeout.

Independent read-only algebraic check: all288 semilocal coefficients0,
SR-HF1, VV10/PT2/D4 each1e-8, exactly four scalar selections. This satisfies
the K14 discovery model's bounds, UEG, support and mandatory-selection checks.
Weighted SSE32.19152576314622Ha²; ridge1e-10Ha². It is a poor-fit feasibility
witness, not a fitted functional, optimizer incumbent or supplied start. Its
existence rules out concluding infeasibility merely from this no-incumbent run.
It does not explain the solver's internal search behavior or guarantee acceptance
of a future MIP start.

## Remaining uncertainty and recommended next step

The current zero-incumbent branch saves status/runtime/node count/parameters,
but no detailed solver log or objective-bound trajectory. There is no incumbent
gap to compare against the100-entry pilot.26 nodes alone cannot identify the
bottleneck. Weighted-feature near dependence remains a diagnostic, not a proved
cause of the no-incumbent timeout.

Recommend a separately versioned diagnostic recovery (requires user approval):
record private solver progress/model statistics/bounds even with no incumbent,
validate/export an explicit full-data feasibility start, and run a focused K14
checkpoint with the same science and initially the same600s/16CPU/32GiB budget.
If needed, compare matched cold/warm starts or a longer budget after inspecting
the diagnostic evidence. Do not simply increase memory, relax constraints,
change weights/ridge, import incompatible pilot coefficients or resubmit blindly.
Preserve frozen run and failure history; changed code needs tests/commit/release.
Full training feature/matrix acceptance remains valid, but full-data bounded MIO
and bulk release are not cleared. No final model or optimality claim.

[Machine-readable audit](./2026-09-11-full1498-mio-failure-audit.json).
