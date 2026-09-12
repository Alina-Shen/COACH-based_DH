# Discovery-first expansion to every integer K14–82

User requested reorganizing discovery before grid selection, explicitly preserving
running jobs. Clarification:69model sizes require138discovery solves under the
approved two-repeat protocol, not69solves. No repeat reduction was inferred.

## Scheduler changes

- Kept **25796986** unchanged:14existing discovery tasks. Queue check after
  reorganization:tasks0/1stillRUNNING (~1h46m),12pending under%2.
- Cancelled **only pending**25796987 (old gridjob) and25796988 (old42selectedfits),
  using `scancel --state=PENDING 25796987 25796988`. Accounting confirms CANCELLED.
  No running jobs cancelled and no artifacts deleted. These old downstream jobs
  would have selected rows before the expanded discovery pool was available.
- Prepared, but did not submit, **124 additional discovery tasks**:62missingK
  values×two repeats. Proposed array0-123%2 waits afterok:25796986. This serializes
  arrays while allowing two simultaneous fits, respecting the two WLSsessions.

## Implementation and checks

Added `discovery_extension_v1.py`, dedicatedSlurmlauncher,freezeutility,fourtests
and disabledmanifest/release draft. Existing frozen production code and identities
are untouched. New runner calls the already-tested7200s/16thread discovery solve
and its scientific/publication/readback audits. It records exclusive per-task
execution receipts and provides combined independent readback of all138candidates.

Noise preservation:retain the old seven-K sweep and all seven original noise
draws; append missingKvalues in ascending order,continuing the RNGstream after
those seven draws. This is explicitly an extended sweep order,not a newly sorted
69K sweep that would change existing noise assignments. No warm-start results
are substituted for original/noisy seeds. All scientific/model settings unchanged.

Full suite **411passed in16.36s**;shellsyntax and freeze PASS. New release remains
disabled until code/manifest commit and postcommit checks. No new solver/WLS job
was launched. Gridselection and414selectedfits are NOT submitted yet.

## Next steps

1. User commit extension code/manifests;verify postcommit tests/hashes and refresh
   resources/expandeduserqueue before releasing/submitting the124taskarray.
2. Retain and validate all14old+124new discovery outputs. Existing candidates are
   reused only if their normal final audits pass. No need to rerun olddiscovery.
3. Prepare the new shared-row selection across ALL138candidates and new414fit
   selected-pass manifest/reader while discovery runs. Do not call the historical
   14candidate selector as though it covered138.
4. After discovery completion/readback,freeze sharedrows and release the selected
   pass with twoWLSsessions. Report all unselected99590 and75302 diagnostics and
   preserve finaluserreview/COACHmodelcomparison.

No tmux feeder needed: Slurm dependencies schedule the extension automatically
once released. Full138discovery baseline~138elapsedhours at twofull7200ssolves
throughout (5days18h from initialdiscovery launch,plusoverhead),not an ETA promise.
Full552fit baseline remains23daysplusoverhead before reuse/earlytermination effects.
