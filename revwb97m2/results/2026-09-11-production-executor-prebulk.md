# Production executor implementation checkpoint

Base commit: `f673c905f0e7ad5eb14d09720c874b8309abb2d3`.
Production submission remains disabled. No jobs or new solver runs were submitted.

## Implemented

- `production_multistart_v1.py`: 56 independent 7200-second, 16-thread solves using the approved expanded SSE+ridge/big-M model. Discovery has 14 tasks; selected-grid pass has 42 tasks. K values, starts and Gaussian noise come from the unchanged committed preparation graph.
- Starts retain the original-plus-noise coefficients without clipping or projection. Start feasibility is diagnostic only. Final results must pass strict scientific, selected-grid, objective and finite-gap consistency audits. Time-limit incumbents may pass; passing does not establish global optimality.
- All 14 discovery publications must validate before selecting and publishing the shared 99590 rows: union of each candidate's top 100, then 200 highest-L1 remaining rows. Pass 2 uses the simple seed and BOTH matching-K discovery candidates, each with original/noisy repeats. No deduplication or preceding-repeat restart.
- Per-task source/start/grid/model/result artifacts have hashed publications and completion markers. Readback reconstructs starts and grid rows, checks solver metadata and independently recomputes scientific reports without modifying artifacts. Unselected 99590 violations and all 75302 diagnostics remain review information.
- `production_submit_v1.py`: read-only command preview and separately gated submission. Dependencies are discovery array -> shared grid job -> selected-grid array. Exclusive run directories and intent/response journals prevent blind duplicate retries. No automatic requeue; failed dependencies cancel dependent work. Partial submission failures require review, not automatic retries.
- Submission checks the expanded all-project queue before each submission against the 998-task cap and retains a local reservation floor for newly submitted tasks. Independent simultaneous submitters still need coordination. No lr_lowprio route is allowed.
- Slurm template proposes 16 CPUs, 32 GiB and 2h30m per solve job (7200 seconds optimizer time plus setup/readback allowance); grid-only job gets 30 minutes. These are draft resources, not a completed live review. The cm1 route in the disabled draft is only for preview.
- Frozen additive execution manifest inherits and verifies existing scientific/source hashes. Release requires committed identities, a matching post-commit test report, resource review and explicit pre-bulk authorization. Historical scientific overlays and the preparation graph remain unchanged.

## Verification performed

- Full suite: **405 passed in 18.27 seconds**, including 15 new execution tests and six existing planner tests.
- New tests cover noisy infeasible suggestions, mandatory scalar selection, 7200-second override, artifact/failure gates, disabled release, array dependencies, queue limits, forbidden route, wrong-K source rejection and the full 14-candidate barrier.
- Real matrix loaded and validated: **1498 x 292**. All seven original discovery starts pass the ungridded audit. All seven noisy discovery starts fail that diagnostic, as expected for dense noise and the approved suggestion-only policy.
- Existing source job **25792248**: both `constrained80` and `restart80` pass fresh v2 independent readback, retaining unselected-grid warnings.
- Shell syntax and diff checks pass. Freeze succeeds; submission preview shows the intended three-stage dependencies without contacting Slurm or submitting.

These checks do not yet validate the new runner end-to-end on a compute node or claim that Gurobi accepts every noisy suggestion. A solver may repair or reject an infeasible suggestion; its final candidate must pass the normal audits.

## Next checkpoint

1. User reviews and commits this implementation.
2. Validate the committed identities/tests and perform compute-node model/start-import preflight using the real arrays and WLS, without launching the full scan. Review live partitions and WLS concurrent-session capacity before selecting release resources/concurrency. No new scientific-choice gate is being introduced.
3. Record the evidence and resource decision; provide the pre-bulk commit commands and obtain explicit release authorization before submitting the 56 solves. If preflight requires code changes, commit and retest those changes first.
4. After all solves, perform full readback and COACH-style model comparison with the retained final user-review gate. NER/role-aware ranking is not automated by this executor.

Future alternatives remain deferred: lean 28-solve schedule, restarting from the preceding fitted solution, SOS1 selection and explicit-residual unregularized SSE.
