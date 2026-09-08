# Staged full-training feature generation — proposed execution plan

Status: review-ready plan, not executable submission authority.
User approved retaining PCONF21_444 and PCONF21_99 in pilot100, subject to resource
review before submission. All1498 COACH Cycle-2 training entries/weights remain.

## Scientific dependency

Generate all292 candidate features for each of2799 unique training species, then
assemble1498 reaction rows. Even with sparse K-selected fitting, all candidate
columns are needed to let the optimizer choose. Fixed-orbital features do not
depend on the fitted linear coefficients, chosen K, solver gap or whether the
100-entry MIO pilot has finished. No new SCF. Existing compatible calculations
are reused, not regenerated merely because their entries recur.

The campaign also needs fixed energies, original reference/weight/stoichiometry
records, semilocal features on250974/99590/75302 and corresponding grid differences.
The primary292-vector is288 semilocal components plus SR-HF, VV10, totalPT2 and
D4-ATM. VV10 remains SG-1-only with the documented zero grid-difference columns;
75302 remains diagnostic. Each stage produces many values, not292 separate jobs.

## Why not submit all missing species immediately?

1. `v7_canary.py:36,119,166` fixes the scope to seven names; it is not a generic
   training-species batch driver. Silently changing the list breaks its contract.
2. `v7_canary.py:317` still uses exact292-vector equality. The accepted D4-only
   1e-12Ha tolerance/recovery exists in `scripts/recover_v7_canary_d4.py`, not yet
   integrated into the production publication/reuse/assembly contract.
3. Active plans hash all top-level package Python files (`v7_canary.py:100`).
   Preserve those files while jobs run; prepare isolated tooling or wait to
   integrate shared-code changes. This restriction does not prevent planning.
4. Metadata audit verifies source inputs/basis identities and recorded artifacts,
   not full restart-tree integrity or safe reuse of every partial native stage.
   Exact new-stage counts and storage/runtime costs therefore remain unknown.
5. Historical resource classes are not live allocation approvals. Large cases,
   including the two approved PCONF21 members, still need resource review.

Read-only accounting this turn:25680435 and25680436 RUNNING, elapsed5:03:13;
25680429/433 completed;25680434 historically FAILED with separately recovered
data. No fresh native numerical validation performed this turn. Two large
canaries remain unsubmitted according to current project records.

## Workload and prioritization

Baseline: training_preflight_v2 snapshot, not a fresh coverage certification.
41 of2799 species have verified recorded v7 evidence;2758 need generation or
further validation. Pilot100 uses224 species,39 evidence candidates and185 pending.
The remaining full-training workload contains2573 further pending species.

| Requested memory class (historical GiB) | Pilot pending | Full pending including pilot |
|---|---:|---:|
| 14 | 172 | 2109 |
| 21 | 8 | 294 |
| 35 | 3 | 185 |
| 62 | 0 | 107 |
| 117 | 0 | 29 |
| 227 | 2 | 26 |
| 557 | 0 | 8 |

These are species needing work/revalidation, not exact numbers of new Q-Chem jobs.
Recheck evidence at freeze time. Prioritize pilot species within ONE full-training
queue; preserve their artifacts for full assembly. Do not run separate redundant
pilot and full generation campaigns. The two pilot227GiB cases are PCONF21_444
and PCONF21_99 (1833 orbital AOs each).

## Proposed phases and deliverables

1. **Production contract and stage-reuse preparation now.** Build a new versioned
   generic driver/reuse contract covering the inventory, D4 tolerance and recovery
   manifests, one-electron zeroPT2, implicit ECP, supported input forms and storage
   separation. Audit unsupported cases explicitly; no bypasses. Test success,
   restart, partial publication, changed hashes, duplicate work and stale inputs.
   Keep active pinned dependencies unchanged; no original archive mutations.
2. **Freeze first pilot-priority tranche.** Validate complete restart trees, inputs,
   basis/ECP, scientific spec and raw reusable stages. Assign each species/stage:
   reuse-validated, generate, or blocked-with-reason. Include exact derived inputs,
   hashes, CPU/memory/wall requests, data/scratch paths and duplicate-job checks.
   Measure tree-copy bytes and filesystem headroom; do not interpret qarchive size
   alone as full orbital storage. Stop for user code commit and execution review.
3. **Reviewed-class release (proposed gate change).** After generic-driver tests and
   appropriate canary evidence, permit a first tranche of up to16 species in
   reviewed14/21/35GiB classes, with at most8 such jobs concurrently (normally8CPU
   each). Audit first tranche before expanding that class; this concurrency is a
   starting proposal, not a restored globaltwo-job limit or a current allocation.
   Existing work counts against approved shared resources. Release62/117GiB only
   after their canaries validate; review large canaries before227/557GiB work.
   Initially propose at most one large16CPU job concurrently, subject to live
   partition/account/memory review. Enforce CPU/memory limits, not job count alone.
4. **Expand approved classes across full training.** Pilot species first; then other
   species in the same cleared class. Review each tranche for common failures,
   memory/runtime/storage and correct output. Resource observations determine
   larger tranche sizes/concurrency; no full2758-species launch at once.
   Missing stages normally include three IDV grids, scalar SR-HF/VV10, fixed
   energy and PT2 (except one-electron cases); D4 is separate. Reuse validated
   stages and do not repeat all stages blindly. Stop common failures for diagnosis;
   no automatic retry, tolerance changes, archive deletion or new SCF.
5. **Pilot matrix and solver test in parallel with feature generation.** Once all
   required224 species validate, reconstruct100x292 A, fixed-subtracted target,
   weights and grid matrices; check numerical values independently. Run only an
   approved bounded MIO test. Its gap need not close before compatible feature
   generation continues. Pause affected generation if the test reveals a feature,
   units, assembly or scientific-spec error, not merely a weak solver bound.
6. **Full numerical preflight and fitting checkpoint.** Complete2799-species
   validation, reconstruct1498x292 A with targets/weights/grids, reject missing or
   stale data, check finite values/scales/correlations and independently reconstruct
   rows. Freeze validated data/code/spec and user commit/resources before bulk
   fitting. This is separate from permission to generate features.

The recommended reviewed-class release and continuing full generation alongside
MIO are proposals superseding the earlier strictly sequential schedule ONLY on
approval. Until then, existing all-seven-canary expansion gates remain in force.
Conservative option: wait for allseven to pass before the first expanded tranche;
even then there is no scientific need to wait for the MIO gap to close.

## Storage and estimates

Retained input/output/log/features:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2`.
Disposable scratch:
`/clusterfs/mhg-data/yaoshen/scf_read/revwb97m2`.
Use new versioned namespaces; user sets no additional quota beyond available
filesystem capacity. Check shared filesystem capacity once, without summing the
same free space twice. Preserve evidence still needed for validation; cleanup
requires an evidence-preserving policy, not automatic deletion.

No defensible total wall/core-hour estimate yet: exact missing-stage counts,
larger-class runtime measurements and restart-copy footprints remain unfinished.
The first executable tranche must include measured/estimated costs with explicit
uncertainty. Memory requests and72h/336h caps are not runtime forecasts.

This turn produced a plan and notes only: no driver edits, calculations, tests,
submissions, resource reservations, commits or scientific changes.
