# Tested100-entry MIO pilot released and submitted

## Completed checks

- Verified clean pre-test commit `ccd5b19ed8fce79f5d21e4b2ef95d1ac78e5e884`.
- Full offline suite: **197 passed in10.50s**, including11 new pilot tests.
- Shell syntax, frozen-plan check and git diff --check passed. No code fixes
  needed; committed source/config/launcher/frozen plan left unchanged.
- Published isolated real adapter at
  `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/pilot100_adapter_check_20260909`.
  Strict loader and adapter readback passed; all original matrix file hashes
  unchanged. Input-manifest SHA256:
  `ded5495640495704c957b05f0d099a9d645b5ad6745078255fb6c097d778062a`.
- Saved passing test/real-data evidence in
  `revwb97m2/results/2026-09-09-pilot100-mio-tests.json`, tied to exact commit/plan.
- Fresh partition review: cm1 five idle241732MiB nodes, approved lr_qchem/
  condo_qchem association, no duplicate user jobs, approximately2.5PiB available
  shared storage. Bundled partition helper absent; manual live queries used.
- Created `revwb97m2/manifests/pilot100_mio_v1/release_20260909.json` referencing
  passing test evidence. Existing release checker verified committed frozen files,
  plan and report hashes. Disabled draft preserved. No lr_lowprio or artificial
  global concurrency cap; approved serial pilot remains unchanged.

## Actual submission and initial evidence

Submitted **25727562**, cm1/lr_qchem/condo_qchem, node n0001.cm1,
16CPU/16GiB/45min. Started2026-09-09 00:33:12 PDT. Initial check RUNNING,
empty stderr; in-job adapter published, synthetic integration report passed all12
checks, Discovery14 contract exists and first real solve has started.
`sbatch --test-only` identifier25727536 is NOT this submitted job.

Approved sequence: Discovery14,Discovery40,Constrained14,Restart14,Constrained40,
Restart40, followed by no-solve resume/independent audits.300s per real solve;
nominal30min real-solver allowance plus overhead, not convergence prediction.
Slurm limit ends01:18:12 PDT if fully used; not a promise of successful completion.

Retained root:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/pilot100_mio_v1/25727562`.
Logs: `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/pilot100_mio_25727562.out`
and matching `.err`. WLS initialization and synthetic solves ran on compute node;
credentials were not read into this conversation or copied to reports.

## Scope and next action

No Q-Chem calculation/rebuild, scientific change, source cleanup, full1498
generation, bulk fitting or final model selection. No new production source code
was modified this turn. Only test evidence, approved release and this report were
added in the repository; isolated adapter and job outputs live in the data tree.

The pilot is running, NOT completed or certified optimal. When finished, inspect
Slurm outcome/RSS, validate the six outputs and PILOT_COMPLETE independently,
compare objective/SSE/ridge, support/UEG/grid limits, starts/restarts and raw versus
recomputed gaps. TIME_LIMIT with an audited incumbent is feasibility evidence,
not optimality;75302 stays diagnostic. Preserve failed output and review rather
than automatically retry. Do not change hash-pinned code while the pilot runs.
