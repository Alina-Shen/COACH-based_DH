# Throttled production release review

## Completed checks

1. Starting commit `a67a7ed2d6c1458fae78258bad308208a00384d7` was clean. Reran the full suite: **407 passed in19.11s**. Recorded a new test report against the current plan hash, not the superseded pre-throttle plan.
2. Verified101source/plan identities against both working files and committed Git content. Revalidated the frozen task/noise graph and real1498x292matrix.
3. Verified publication hashes for compute preflight25795805 and that the production builder is unchanged from the preflight commit. No new compute preflight or fitting experiment was required/performed.
4. Used the partition skill's manual fallback; its helper remains missing. Live19:38PDT snapshot: cm1 had5idle nodes,48CPUs/241732MiB each, correct lr_qchem/condo_qchem association and no maximum walltime conflict. lr8 had9idle nodes;mhg4. All can fit32GiB, but cm1 already offered immediate scheduler eligibility and matches the existing template. No route/memory/script changes were needed.
5. `sbatch --test-only --array=0-13%2 ...` accepted the16CPU/32GiB/2h30m production allocation and predicted immediate eligibility on n0001.cm1. This did NOT submit a job; the displayed test-only ID25795985 is not a running production job. Actual starts remain scheduler-dependent.
6. User queue was empty; shared data filesystem reported2.5Pavailable. Neither proves WLS slots are unused outside Slurm. User-confirmed license entitlement is2; reserve both for this campaign and avoid other Gurobi environments during it.
7. Prepared `manifests/production_multistart_v1/release_candidate_20260911.json`, linked to committed tests/currentplan. Tests/resources are marked reviewed; submission,prebulkapproval and WLSreservation remainfalse. No solver/submission code changed and no jobs were submitted.
8. Updated project chapter/index and STATUS forward table using proj_notes.

## Proposed release

56solves total:14discovery -> one non-WLS shared-grid job ->42selected-grid solves.
Both fitting arrays use%2; maximum2simultaneous solves within this campaign.
Per solve:7200seconds optimizer limit,16CPUs,32GiB,2h30m Slurm allocation.
Grid job:30minutes. Partitioncm1/accountlr_qchem/QOScondo_qchem recommended.
Expected full-limit solver occupancy at2concurrent is56hours elapsed, plus
setup/queue/grid/audit overhead, not a guaranteed finish time.

All scientific choices,starts,noise,bigM,selected-row policy and finaluserreview
remain unchanged. Less than999active Slurm tasks and no lr_lowprio remain enforced.

## Remaining launch gate

User commits this evidence/candidate and explicitly approves production launch,
confirming both WLS sessions are reserved (including no competing use elsewhere).
Then refresh queue/resources, create a separate authorized release without
rewriting the reviewed candidate, validate it and submit the three-stage chain.
No additional implementation or scientific-choice blocker was found in these
checks. Do not create repeated pre-test checkpoints for this evidence-only update.
