# Recovery jobs submitted — September 11, 2026

## Release and placement

Validated release_20260911.json against tested commit0feb182,310-test report and frozen file hashes. Direct live partition review (helper unavailable): cm1 five idle241732MiB nodes with valid lr_qchem/condo_qchem association; mhg/lr8 also had idle capacity. User queue empty; storage2.5PiB available. Retained committed cm1 launchers,16CPU/32GiB each; no lr_lowprio or source/scientific changes. Release permits only the two approved recovery jobs, not bulk fitting or retries.

Submitted **25784018** (precision) and **25784019** (7200s improved-start K14 MIO). Both started09:23:20PDT on n0001.cm1. Precision scheduler limit90min; MIO3h. Both independently allocated16CPUs/32GiB.

## Startup and short-job results

- 25784018 COMPLETED0:0 in26s, batch MaxRSS191200K (~187MiB). Both variants report solver OPTIMAL and all in-job independently recomputed acceptance checks pass. No callback errors. Tight barrier:0.989s, objective1.12729476992599, UEG error3.997e-15, residual identity error1.665e-13. Tight barrier+NumericFocus3:3.291s, objective1.1272947699259757, UEG error2.220e-15, residual identity error1.362e-13. Scientific tolerances unchanged;51 fractional selections each, not MIO candidates. This resolves the observed continuous accuracy failure in these diagnostic variants, not the internal cause of earlier MIO stagnation. Separate post-completion provenance/readback can accompany full results review; current result review inspected saved artifacts/in-job audits.
- 25784019 RUNNING at startup check, empty stderr, positive CPU use. Progress confirms `Loaded user MIP start with objective 4.42974` and incumbent4.4297431411741; initial bound3e-26. Start acceptance is now verified by Gurobi, not merely mock import. No search improvement or final acceptance claimed. Expected end near11:24PDT if full7200s solver cap used, plus setup/finalization; Slurm hard deadline12:23:20PDT. Do not wait for completion this turn.

Heavy outputs under `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/solver_recovery_v1/25784018_precision` and `25784019_mio`. Logs under project data `logs/recovery_precision_25784018.{out,err}` and `logs/recovery_mio_25784019.{out,err}`.

Next: after MIO finishes, independently review artifact hashes, candidate coefficients/support, objective improvement, constraints, bounds/gaps and resource use. Then decide existing K80/grid/restart validation steps; do not automatically broaden production or alter tolerances. No new implementation commit required by this submission turn; only operational records/notes added.
