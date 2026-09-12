# Approved two-session WLS throttle

User confirmed two concurrent WLS sessions and approved implementation/documentation.
Starting commit: `0d49f1c`; initial worktree clean. No jobs submitted.

- `production_submit_v1.py`: discovery array now `0-13%2`; selected-grid array `0-41%2`. Existing afterok discovery -> grid -> selected dependencies prevent overlap between passes. Grid selection opens no WLS session. All56solves,7200s/solve,16CPU/32GiB per task remain unchanged.
- Added a fail-closed submission check for the two-session plan and `wls_sessions_reserved_for_campaign=true` in the reviewed release. This is an operational reservation acknowledgment, not a global license-server lock. Other projects/interactive Gurobi sessions must not use these slots while the campaign runs; multiple simultaneous campaign launches also need coordination.
- `test_production_execution_v1.py`: checks exact throttled array arguments and adds missing-reservation/wrong-capacity rejection tests.
- `freeze_production_execution_v1.py`: records capacity2 and defaults the reservation flag tofalse. Refreshed the UNRELEASED plan's three changed file hashes and the disabled draft's plan identity. All submission/review/reservation flags remainfalse. Historical plan and preflight evidence remain in Git/history; old test reports cannot release the revised plan.
- Full regression suite: **407 PASS,16.58s**. Read-only command preview and all frozen source/draft/graph identity checks PASS; `git diff --check` PASS. No scheduler, license or optimizer calls this turn.

The scientific model builder/executor, task graph, data and Slurm allocation template are unchanged. Build/start-import evidence from25795805 therefore remains relevant to those unchanged components, but it is not evidence of a new full runner execution. No repeat chemistry or new scientific fitting experiment is required for this submission-only change.

Next: user commit, record post-commit tests against the new plan, refresh live resources and confirm both sessions reserved, then explicit production release. Budget approximately56hours of elapsed solver occupancy if all56solves use7200s with two active throughout, plus setup/grid/queue time; this is not a wall-clock guarantee. Queue cap remains998 expanded active tasks, not998running, and no lr_lowprio.
