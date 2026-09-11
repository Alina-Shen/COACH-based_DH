# Full-training progress and completed-result audit — 2026-09-09

## Snapshot: approximately 08:58:39 PDT

The 2,548 ordinary species exclude the 21 ECP gateway species, which have all
completed successfully. All ordinary species have now been submitted.

| Ordinary-species status | Count |
| --- | ---: |
| Slurm COMPLETED and publication audit passed | 1,823 |
| RUNNING | 212 |
| COMPLETING | 1 |
| PENDING | 512 |
| Unsubmitted | 0 |
| Failed/unknown in this snapshot | 0 |
| **Not yet scheduler-completed** | **725** |

The filesystem scan followed the Slurm snapshot: 1,835 ordinary publications
passed by scan time, including12 that were not yet COMPLETED in the earlier
scheduler snapshot. Do not mix these two clocks; the conservative headline is
1,823 complete /725 unfinished. Controller continues updating these counts.

| Memory class | Total | Complete | Running/completing | Pending |
| --- | ---: | ---: | ---: | ---: |
| 14 GiB | 1,916 | 1,217 | 200 | 499 |
| 21 GiB | 286 | 286 | 0 | 0 |
| 35 GiB | 182 | 182 | 0 | 0 |
| 62 GiB | 106 | 104 | 2 | 0 |
| 117 GiB | 28 | 28 | 0 | 0 |
| 227 GiB | 23 | 5 | 5 | 13 |
| 557 GiB | 7 | 1 | 6 | 0 |

## Result checks

- Reconciled every submitted index/species against fresh Slurm queue/accounting.
  No failed, cancelled, timed-out or unknown task in the snapshot. All1,823
  scheduler-completed ordinary tasks had matching publications;21/21 ECP too.
- Independently checked all1,856 available publications (1,835 ordinary +21ECP):
  plan/species/specification identities, exact artifact set and SHA256 hashes,
  feature and both grid-difference array shapes292, finite values, fixed-HF and
  PT2 scaling identities. **Zero audit errors.**
- Maximum fixed-HF reconstruction error **5.10e-9 Ha**, below2e-8 tolerance.
  Maximum PT2 scaling identity error **1.000002e-10 Ha**, below5.2e-9 tolerance.
- Eight deeper independent native `validate` readbacks passed:3d4dIPSS_Zr_GS,
  TMB26_T1,3d4dIPSS_Sc_GS,G21IP_26,MOR33_pr28,HR46_cytosine0+,MOR09_ed07,
  2915_28BenzeneUracilpipi090_dim_S66x8. These cover ECP and every memory class,
  checking original restart-tree identity, stage/input/output hashes, saved-MO
  and electron/spin evidence, reconstructed292-vectors/fixed/scalars/grids.
  This is full raw reconstruction for8 samples, NOT for every finished species.
- Verified actual tmux process on **n0001.scs00**, PID3021682, pane alive;
  heartbeat and all2,569 submissions (includingECP) recorded. This inspection
  session is on n0002.scs00; its absent local tmux socket did not mean failure.
  Existing controller remains running; no settings, jobs or routes changed.

## ETA and exceptions

**Planning estimate: another24–48 hours, low confidence; longer remains possible.**
This means roughly September10–11 morning PDT, not a promised deadline.

- Small/medium remainder: roughly1–3hours if current queue movement persists.
  Recent ordinary throughput rose sharply: about1,191 completed in the hour
  before08:54 and974 in its final half-hour; extrapolating this to the large
  tail would be misleading. Some small jobs may wait longer behind reservations.
- **227-GiB tail:**13pending and5running oncm1. Completed peers took4.4–6.6h,
  including PCONF21_114 at4.92h. At roughly5 simultaneous memory-fitting jobs,
  the remaining waves suggest about15–24h, conditional on unchanged capacity.
  Pending Slurm start estimates near"now" despite resource waits are not useful
  deadline predictions. More available nodes could shorten this substantially.
- **557-GiB tail:**MOR09_ed07 completed in6h35m31s. Of six running peers, three
  have completed PT2 and are in scalar, two remain in PT2, while **MOR32_pr24
  (25731104_5)** is still in its first250974 grid after about6.5h.
- MOR32_pr24 has4,979 basis functions, versus2,849/2,893 in completed/further-
  advanced peers, so it is not a like-for-like runtime comparison. Its output
  has been quiet since02:26 at read-orbital grid evaluation, but two Slurm CPU
  samples grew from4d03:40:47 to4d05:02:12, consistent with active multithreaded
  computation. Observed MaxRSS254.0GiB is below its557GiB request; no fatal error
  or restart was detected. This does NOT prove eventual success or a precise
  completion percentage. Its remaining stages are uncalibrated and dominate
  uncertainty in the24–48h planning window.

Recommendation: keep the healthy campaign running; recheck MOR32_pr24 in1–2h
for its first-stage completion and review the227GiB pending queue then. If waits
remain large, consider explicitly reviewed redistribution of pending227GiB work
to another eligible route. No cancellation/resubmission is authorized by this
status-only request, so none was performed.

Detailed snapshot, species mapping and sample readbacks:
[JSON evidence](./2026-09-09-full-training-progress-audit.json).
No production-code edits, scientific changes, newSCF, rebuild or new submission
were performed by this inspection. Existing authorized controller continued.
