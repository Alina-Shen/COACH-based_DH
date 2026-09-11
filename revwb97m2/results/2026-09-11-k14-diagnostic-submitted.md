# K14 diagnostic tests, release and startup — September11

- Verified clean committed implementation04ef24cbc10456250d6c3ff2fe43a4f7bbf9abab.
  Full suite277 passed in11.15s; frozen diagnostic code/plan check passed. No fix
  or production source edit required. New ten tests are now executed, not pending.
- Fresh full1498 matrix/source/identity readback passed. Analytic four-scalar
  start and1498 residuals passed independent audit, objective32.19152576324622Ha².
  Evidence: `2026-09-11-k14-diagnostic-preflight.json` and `-tests.json`.
- Live partition review:cm1 five idle48CPU/241732MiB nodes; mhg four idle nodes;
  lr8 three idle and five mixed nodes. Kept committedcm1 route, valid
  lr_qchem/condo_qchem association; no lr_lowprio. User queue empty. Direct Slurm
  fallback used because partition helper was previously found missing. Dry-run
  predicted immediatecm1 placement. No launcher/resource changes.
- Created separate `manifests/k14_diagnostic_v1/release_20260911.json`, validated
  against committed file hashes and passing test evidence. Disabled draft retained.
- Submitted **25778785**, started **00:39:57PDT** on **n0001.cm1** with16CPU/32GiB,
 90min allocation (deadline02:09:57). Only oneK14/600s solve, not allsix or bulk.
- Startup: model has2082 variables,292 binaries,2088 constraints,1790 quadratic
  objective terms; build/start~4s. Saved solver13.0.3 parameters match approved
 600s/16threads/seed0 and unchanged numerical tolerances.
- Progress shows `Loaded user MIP start with objective 32.1915`; at~0.423s,
  MIP_SOLCNT=1, best objective32.19152576324623, bound3e-26. This is direct
  start-acceptance evidence. The initial start is a poor-fit feasibility witness,
  not a useful final model or proof of optimum. Logs record presolve/MIP progress
  and nonfinite sentinels without exposing credentials; stderr empty at check.
- No need to wait for completion this turn. After job ends, run independent
  `k14_diagnostic_v1 validate`, inspect objective improvement/bound trajectory,
  final incumbent/constraints/gaps and peak memory before deciding next scope.
  Do not automatically restart six-solve workflow or change science/resources.

Output root:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/k14_diagnostic_v1/25778785`.
Logs: heavy-data `logs/k14_diagnostic_25778785.out` and `.err`.

Only operational release/test/preflight/report artifacts added; no production
code changes, native chemistry or data cleanup. Updated project notes/STATUS.
