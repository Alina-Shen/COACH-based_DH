# Approved simple seed and 56-task preparation graph

User approved completing COACH's simple seed with validated25792248constrained80VV10=.99999999,PT2=.027300022669629182,ATM=.99999999. These are starting guesses only. Updated review proposal,leaving bulk_authorized=false.

Added `production_multistart_plan_v1.py`:fixed7Klist,14pass1/42pass2taskgraph;each originalstart has raw and Gaussian0.05noisy repeats,not incumbentrestart. Eachpass resetsdefault_rng(0);noise precomputed overfixedK/startorder,includingall292coefficients,withoutclipping/projection. Pass2pool issimple+bothmatchingKpass1results,no deduplication;all14discoveryoutputs feed sharedrow-selectionbarrier. Noise/start suggestions may be infeasible;accepted-fit auditing remains separate.

Added sixplannerregressions coveringcounts,poolmatching,dependencybarrier,noise reproducibility/per-passreset,originalstartsemantics,scalar-onlysourcecopy and absenceofclipping. Targeted6testsPASS0.20s;full390testsPASS16.21s;gitdiffcheckPASS.

Revalidated actualsource25792248 withselective_readback_v2 and builtnew simple seed. K14ungriddedscientific/selectionauditPASS;seedfitsallplannedKbudgets. Savedsourcecoefficient/publicationSHA,proposal/plannerSHA,fullseed,seed audit,56taskrecords/noisevectors in `revwb97m2/manifests/production_multistart_preparation_v1/task_graph.json`.

This is a NON-SUBMITTING preparation artifact,not finalproductionexecutionrelease. production_executor_implemented=false and submission_authorized=false. NoWLS/newfits/jobs. Nextimplementversioned7200sproductionexecutor,noisy-startimport,audit-awarepublication/dependencyorchestration usingthisgraph;regressions/preflight,prebulkcommit/resource/scanrelease stillrequired. Historicalrunners/scientificspechashes untouched. FutureTODOslean28andincumbentrestartretained.
