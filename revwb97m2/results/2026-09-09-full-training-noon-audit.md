# Full-training noon status — September9,2026

Snapshot12:21:01PDT: **2499/2548ordinary species COMPLETED and validated;
49unfinished =7running +42pending.** Zero failed/unknown/unsubmitted. Separate
21ECP gateway species remain21/21complete. Previous08:59unfinished725 is historical.

| Remaining class | Running | Pending | Total unfinished |
| --- | ---: | ---: | ---: |
| 14GiB | 0 | 32 | 32 |
| 227GiB | 5 | 10 | 15 |
| 557GiB | 2 | 0 | 2 |

All21/35/62/117GiB classes are complete. All42pending tasks are oncm1;
10large wait forResources and32small wait forPriority. The227GiB jobs occupy
almost all memory of their nodes, leaving insufficient room for14GiB jobs.
Allotherordinary submissions finished. The controllerheartbeat12:20:22PDT
records2520complete/49active/all2569submitted, nohalt/unresolvedintent.

## Finished-result audit

- Fresh all-species Slurm accounting/queue reconciliation and independent
  publication audit: **2520/2520published species PASS** (2499ordinary+21ECP).
- Checked completion/plan/species/specification identities, exact artifact sets,
  hashes, feature and grid-difference arrays shape292 and finiteness, fixed-HF
  reconstruction and PT2 scaling identities. Zero failures. MaxHF5.10e-9Ha
  below2e-8; maxPT2identity1.000002e-10Ha below5.2e-9.
- Eight freshly selected representative raw readbacks passed, spanning every
  memory class plusECP:3d4dIPSS_Zr_GS,TMB26_T1,RG10N_KrKr_2p600,G21IP_IP_72,
  MOR33_pr28,HR46_cytosine0+,MOR28_pr09,2915_28BenzeneUracilpipi090_dim_S66x8.
  These recheck originalrestart identities, native stages and reconstructed
  vectors/fixed/scalars/grids; not a full raw reconstruction of all2520species.

## Slow jobs and revised outlook

- **MOR32_pr24,25731104_5 (actualJobID25731367):** first250974stage completed
  normally10:08:12PDT after27860.49s=7h44m20s. Now75302stage; totaljob~10h.
  Thus the earlier silent stage was progressing, not demonstrably stuck.
  Latesttelemetry CPU6d06:54:01 and reportedRSS~39.9GiB, below557GiB allocation.
- **MOR10_ed09,25731104_1 (actualJobID25731106):** finalscalar stage after
  ~10htotal; CPU6d10:41:48 andRSS~295.5GiB, below557GiB. Otherfive557GiB jobs
  completed in6h35m–8h50m. Neither remainingjob has a recorded failure.
- Arraynotation in a combinedsstat query resolved incorrectly; reran with actual
  JobIDs above. This telemetrylookup issue was not a jobfailure.
- **227GiB:**8complete,5running,10pending. PCONF completed peers4h17m–4h55m;
  at roughly5simultaneous jobs, expect about10–15morehours for this group,
  conditional on unchanged capacity/runtime. Runningjobs have mixedelapsedtimes.
- **32small14GiB cases:** computation is short but allremainqueued oncm1. The
  morning1–3h small-job forecast no longer applies to these queue-bound cases;
  their waitingtime can extend with thelargejobqueue.

**Overall planning window:24–48morehours, lowconfidence**, roughlySeptember10
noon–September11noonPDT, potentially longer. MOR32_pr24 is the major unknown.
For scale only, itsdensegrid is~5.6times the1.39h grid ofMOR09_ed07; applying
that ratio to the6.59h peer total suggests~37htotal/~27hremaining. This is an
uncalibrated heuristic, not a solverprogress estimate:PT2 and scalar do not
necessarily scale like thegrid, so a tighter deadline would be unjustified.

Recommendation: keep running; consider a separate live-resource review to move
the32pending14GiB jobs offcm1, potentially also pending227GiB work. Such changes
require reviewed release/job routing and duplicate-safe cancellation/resubmission;
none performed for this status-only request. No productioncode/science changes,
newSCF or rebuild. Controllercontinuesmonitoring within998cap.

[Detailed evidence](./2026-09-09-full-training-noon-audit.json).
