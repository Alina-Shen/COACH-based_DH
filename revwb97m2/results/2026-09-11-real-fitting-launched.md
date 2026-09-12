# Real fitting launched: approved 56-solve campaign

## Authorization and actions

User explicitly approved launch and reserved both WLS sessions. Verified clean
evidence commit `3cfdfeabc71112c078be4c3d3d368ab370cca165`; execution commit remains
`a67a7ed2d6c1458fae78258bad308208a00384d7`, matching the407-test report. Created
separate authorized `manifests/production_multistart_v1/release_20260911.json`,
preserving the disabled reviewed candidate. Release/source/test hashes, WLS
reservation and a fresh output directory all passed the release checks.

Used partition manual fallback: cm1fiveidle48CPU/241732MiBnodes,correctassociation,
emptyuserqueue;lr8/mhg also available. Selectedcm1; no low-priority QOS. Shared
filesystem2.5Pavailable. No solver code, scientific settings or task graph changed.

Submitted the guarded three-stage chain at2026-09-11 19:44:58–59PDT. The submitter
recorded exact commands/responses, checked expanded queue counts against998,
disabled automatic requeue and attached afterok dependencies. Slurm confirmed
the two-session throttles and dependencies. First two tasks started19:45PDT.
Initial health check: both firstK14solves emitted finite incumbent/bound progress
and24–25solutions at~62solver seconds; stderr files empty. This demonstrates
active search, not final independent candidate acceptance.

## Submitted jobs

| Job | Tasks and purpose | Resources per task | Dependency / concurrency |
|---|---|---|---|
| 25796986 |14discovery fits;K14,24,32,40,48,64,80,each original/noisy simple seed |16CPU,32GiB,2h30m;7200s solver |array0-13%2;no predecessor |
| 25796987 |Audit all14discovery results and freeze shared99590gridrows |16CPU,32GiB,30min;noWLS |afterok:25796986(alltasks) |
| 25796988 |42selected-grid fits;eachK has3starts×2repeats |16CPU,32GiB,2h30m;7200s solver |array0-41%2;afterok:25796987 |

All use partitioncm1/accountlr_qchem/QOScondo_qchem. Two simultaneous fits consume
32CPUs and64GiB total requested memory. There are57Slurmtasks including the
gridjob,not57optimization runs. Dependencies allow no pass overlap. No automatic
failed-job retries; invalid downstream dependencies are configured for cancellation.

Kordering is `[14,24,32,40,48,64,80]`. For zero-based Kpositioni, discovery indices
2i,2i+1 are original/noisy. Selected indices6i..6i+5 are simpleoriginal/noisy,
matchingKdiscoveryrepeat0original/noisy,matchingKdiscoveryrepeat1original/noisy.
Kcounts selected feature slots including the four mandatory DH scalar slots.

## Science and validation plan

Use all1498training entries and292features with frozen COACH-cycle2weights,
fixedwb97m-vorbitals,omega0.3,approvedDHterms,expandedweightedSSE+ridge1e-10,
bigMselection and approvedconstraints. NoSCForfeaturegeneration occurs here.
Noise is the frozen Gaussian sigma0.05 vector added to each ORIGINALstart;
repeat1 is not a restart fromrepeat0. Solver suggestions may be infeasible;
accepted final coefficients must pass strict audits.

Discovery is ungridded. All14published valid candidates feed the union of their
top100absolute99590differences,then200highestL1REMAININGrows. This frozen union
is shared by all42pass2fits; its size is not assumed to equal historical349.
Pass2retains allthree matchingKstart sources,even duplicate candidates.

Selected99590rows are enforced with approved internal margin. Full99590
unselectedviolations and75302diagnostics are reported for review,not silently
converted into extra hard constraints. Time-limit incumbents may pass; solver
gaps are retained and do not establish globaloptimality. No final model is
automatically selected by this campaign.

After completion: verify per-task publications and fresh objective/support/
constraint/grid/gap readback for all56; assemble results byK/start/repeat;
perform approved COACH-style dataset-awareNER/model-size comparison with protected
assessment roles respected; resolve only deferred ranking choices needed for
actual selection; ask user to approve final model; archive coefficients/support/
metrics/provenance. Preserve failures for targeted diagnosis rather than blind
resubmission. Lean28schedule,preceding-incumbentrestart,SOS1 and unregularized
explicit-residual formulation remain futureTODOs.

## Timing and locations

If all fits use7200s and both slots stay occupied: discovery~14hours,selected
pass~42hours,total~56elapsed solver-hours plusqueue/setup/grid/readback. Nominal
full-limit baseline reaches earlySeptember14PDT from this launch,not a guarantee.
Slurm2h30m is a job safety limit,not the optimizer search time.

Heavydata:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/production_multistart_v1/coach_noisy56_20260911`.
Logs: siblingdata`logs/production_<arrayid>_<index>.out/.err`; grid-onlyjob uses
`production_25796987_4294967294` for the non-array index token.
Slurm schedules the rest automatically; no tmux feeder or manual batches needed.
Keep both WLSsessions reserved and do not change frozen source/release files
while queued tasks still depend on them. STATUS contains the current full plan.
