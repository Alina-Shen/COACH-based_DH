# Search-v2 and expanded comparison submitted

## Validation

Committed855928a was clean at start. Full suite **338 tests passed in15.24s**. Frozen code/plan/input hashes and full1498 matrix preflight passed. Direct starting-point objective4.429743141174104 versus expanded4.429743141173731 (difference~3.73e-13), within unchanged tolerance. Infinite-parameter JSON regression passes. Both shell launchers pass syntax checks.

Compute-node build-only test **25787291** COMPLETED0:0 in15s. Constructed actual full-data Gurobi model, verified that all590 non-residual constraints and all remaining variable bounds/types are identical before/after elimination. Expanded model584variables/590constraints/292binaries/zeroSOS. No optimize call in build test. WLS access worked quietly. Temporary `/tmp/expanded-build-check.py` was embedded in Slurm wrap; no tracked production code edits.

## Release/submission

Direct live partition review:cm1 five idle241732MiB nodes and valid lr_qchem/condo_qchem association; empty initial user queue,2.5PiB filesystem free. Retained cm1 launchers,16CPU/32GiB each; no lr_lowprio. Bound releases to tested commit, respective plans,test reports and compute-build record.

- **25787336** corrected seven-case search/semilocal diagnostic,started11:59:55PDT,n0001.cm1,3h scheduler limit. Up to7x600s solver time; dependent MIO cases require accepted semilocal start. Estimated~13:10PDT if all caps used,plus overhead; hard deadline14:59:55.
- **25787337** three-case residual/expanded comparison,started11:59:59PDT,n0001.cm1,90min scheduler limit. Up to3x600s solver time; estimated~12:30PDT at all caps,plus overhead; hard deadline13:29:59.

Both RUNNING at startup check,empty stderr,model exports/parameter JSON created. search_v2 successfully serialized unlimited NodeLimit and created its optimization progress file,passing the prior pre-solve failure location. These are startup checks,not completed solver acceptance. Do not infer semilocal fit or expanded formulation success before final readback.

Subsequent startup telemetry confirms qp_dual is iterating and the residual MIO control loaded user start objective4.42974. Intermediate simplex objectives have nonzero primal infeasibility and are NOT accepted candidate energies or final results.

Heavy artifacts under `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/search_diagnostic_v2/25787336` and `expanded_objective_v1/25787337`. Releases under corresponding repo manifests as release_20260911.json; preflight/build/test records under results. Big-M retained,SOS1 deferred,production specification unchanged. No additional retry or bulk fitting authorization.

Next: completed independent artifacts/objective/constraint/bound/start audit, compare QP algorithms/root behavior,check semilocal fit and same-start residual/expanded outcomes. No need to wait for completion this turn. No tracked solver/source/config edits; only operational reports/releases and notes added.
