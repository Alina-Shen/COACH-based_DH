# Full138-discovery shared-grid /414-fit workflow implemented

Base commit86db7403b307f32c47d6a910cc2fe0c89947ac18 verified clean. No active
discovery files, frozen manifests, scientific settings or scheduler jobs changed.

## Changes and explanation

| File | Purpose |
|---|---|
| `selected_full_v1.py` | Versioned552-task graph retaining all138discovery definitions, including original noise; creates414pass2tasks acrossK14–82. Validates all discovery sources, snapshots published artifacts under heavy-data storage, freezes common99590rows, runs selected fits and independently reads all414results. |
| `selected_submit_v1.py` | Read-only preview and gated two-job submission with exclusive intent/response journal. Gridjob depends on25796986AND25801134;selectedarray0-413%2depends ongridjob. Checks expandeduserqueue<=998before eachsubmit;no blind retries/requeue. |
| `slurm/run_selected_full_v1.sh` | Shared launcher,16CPU/32GiB/2h30m selected jobs; grid submission overrideswalltime30min. QuietWLSinitialization only for fitting;grid/readback license-free. |
| `scripts/freeze_selected_full_v1.py` | Freezes inherited/newcode and upstreamrelease hashes, deterministic graph and disabledrelease draft. Does not require future discovery outputs to prepare the plan. |
| `tests/test_selected_full_v1.py` | Sixregressions:138/414coverage,allmatchingKsources,noisedeterminism,preserveddiscoverydefinitions,Slurmdependencies/throttle,disabledrelease,incomplete-source rejection before snapshot. |
| `manifests/selected_full_v1/` | Frozenplan and disableddraft;not a release or completedgridpublication. |

Pass2starts reset RNGseed0 once and enumerate K14..82 ascending, each with
simple/discoveryrepeat0/discoveryrepeat1 sources and original/noisyrepeat.
Gaussian sigma0.05 suggestions remain unprojected; strict finalscientificaudit
unchanged. Noisyrepeat is not a preceding-incumbentrestart. Discovery retained
its alreadyfrozen seven-K-prefix/extension order; no existing seed is modified.

Thegridjob first performs full independent138sourceaudit,then copies published
source directories into a fresh heavy-data root and audits copied artifacts.
Original sourcepaths/publicationhashes are recorded. Allselectedfits reconstruct
sharedrows from the138snapshotcandidates and check source/copyidentity. Snapshot
failure cannot release the dependent array;no partialpool or fallback old349rows.
Selectedrows are uniontop100percandidate plus up to200L1remainingrows,not
necessarily all1498andnotafixedcount. No actualproductionrows selected this turn.

Heavyoutputroot:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/selected_full_v1`.
All414fits retain7200ssearch,16threads,expandedSSE+ridge,bigM,approvedselected-only
acceptance and full99590/75302diagnostics. Finalmodelcomparison/NER/userselection
remains separate;thisexecutor does not automatically choose a finalfunctional.

## Verification and next gate

Fullsuite **417passed in16.52s**. Freeze,Slurmshellsyntax andread-onlysubmission
previewPASS. No Gurobi/WLSsession,optimizer,Slurmquery or submission was made.
Full138source snapshot and414fit realend-to-end readback are not yetvalidated:
most discoveryoutputs do not exist yet. Tests verify logic,not futuredata.

Nextusercommit;postcommitidentities/tests and proportionate real-data/build
checks,live resource review before release. Pending jobs may be queued behind
discovery after appropriate releaseapproval,or submission may wait for actual
138sourcevalidation;in either casegridexecutionmustwaitforall138validresults.
Thelargerpool may produce moregridrows thanhistorical349;review construction
and snapshot/runtime/storage overhead before release. Keep bothWLSsessions
reserved and immutableupstreamfiles unchanged whiletheirjobsremainactive.
