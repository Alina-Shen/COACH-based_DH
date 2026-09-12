# Full selected workflow queued with deferred build gate

## Completed work

1. Verified clean commitd57e25e243b6bbf5e4667c1f3368979b8ff31777. Fullsuite417PASS
   in17.27s. Verified114committed source/planidentities,138/414taskgraph and
   real1498x292matrix. Maximumpossiblegridrows1498 gives3586linearconstraints,
   584variables,292binaries,zeroSOS. This is a sizing check,not a completed build.
2. LiveSlurm: discovery25796986tasks2/3running,tasks4–13pending;extension25801134
   pendingdependency. BothWLSslotsoccupied,so no third environment was opened.
3. Used partitionmanualfallback(helpermissing). cm1fouridle48CPU/241732MiBnodes,
   supported account/QOS and unchanged32GiBrequest. Test-onlyschedulerchecks
   accepted preflight and414array. Their predictedtimes are not dependency ETAs.
4. Added operational maximum-row preflight harness/wrapper underresults. It waits
   for bothdiscoveryarrays,validatesall138results,then uses ONEquietWLSsession
   to build K14/K82 with original/noisy simple starts andall1498rows. Checks
   dimensions,startassignment,7200s/16threads;never calls optimize. Allrows here
   are construction upper-bound fixtures,NOT production rowselection.
5. Recorded committedtestreport and separate authorizedrelease with preflight
   harnesshash. No frozen production/discovery source or scientific policy changed.
6. Submittedthreejobs with exclusive intent/responsejournal under heavydata
   `fitting/selected_full_v1_submission`. Expandedqueue counts checked<=998
   beforeeachsubmission. Grid dependency strengthened to include buildjob in
   addition to bothdiscoveryarrays,without modifying frozen submittercode.
7. Verified liveSlurm IDs,dependencies,resources and%2throttle. Allnewjobs pending
   Dependency,asintended. No runningjobcancelled;no newWLSsession used thisturn.
8. Updated projectchapter/index and STATUS executiontable.

## New jobs (submitted2026-09-11 22:13:35–36PDT)

| Job | Purpose | Resources | Dependency |
|---|---|---|---|
|25802822|138sourceaudits +four maximum-row build/start checks;nooptimization|cm1/lr_qchem/condo_qchem;16CPU,32GiB,30min;oneWLSsession|afterok25796986AND25801134|
|25802823|Audit/snapshot all138discoveries;select/freeze actualshared99590rows|same route;16CPU,32GiB,30min;noWLS|afterokbothdiscoveryarraysAND25802822|
|25802824|414selected-gridfits across69Kvalues;three sources×two repeats|same route;16CPU,32GiB,2h30m/task;7200ssearch|array0-413%2;afterok25802823|

Entireactiveworkflow: original14discoveries ->124extensiondiscoveries ->buildgate
->sharedgrid ->414selectedfits.138+414=552optimizationruns;build/grid addtwo
non-fittingtasks. Oldcancelledseven-Kdownstreamjobs are not reinstated.

## Honest status and next steps

The417regressiontests and committed/input checks have passed. Thedeferredbuild,
full138sourceaudit,snapshot andselectedfits have NOTrun/passed yet. Any failed
predecessor blocks/cancelsdependentwork;no automaticfailed-jobretry. TwoWLSlimit
is respected by sequencing and%2;maintainreservedslots outside thiscampaign.

No manual batch submissions should be needed. At status checks,validate completed
discoveries;after25802822inspect its report,after25802823inspect actualrowcount/
snapshotpublication,andafterselectedfitsrunindependentreadbackbeforeCOACH-style
comparison/finaluserreview. Fullfresh552solve two-slotbaseline23daysplusoverhead
remains a budget estimate,not a guaranteedfinishdate.

Buildreportroot:data`revwb97m2/fitting/selected_full_v1_build_preflight`;
scientificsnapshot/fits:data`revwb97m2/fitting/selected_full_v1`;
logs:data`revwb97m2/logs/selected_build_25802822.out/.err` and
`selected_full_<job/array>_<index>.out/.err`.
Keep sourcefiles/releases/preflightharnessunchanged while jobs are queued.
