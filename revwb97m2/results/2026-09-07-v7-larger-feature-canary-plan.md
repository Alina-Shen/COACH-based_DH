# v7 larger-dataset feature-generation canary plan

Status: **proposal for user review; not executable or submission-authorized**.
No jobs, scientific code edits or commits performed while preparing this plan.

## Purpose and current evidence

The completed38species/20reaction v7 cohort validates VV10-only refresh and
bounded ridge/grid fitting, not fresh feature generation at larger scale.
The20row pilot supplies feasible audited incumbents, not convergence: rawgap
anomaly persists and75302 diagnostic exceeds0.015kcal/mol. Neither issue is
fixed or concealed by generating more features.

Initial production scope remains1498 fitting entries/2799species, existing
omegaB97M-V Q-Chem orbitals, targetomega.3, gamma_ss.01, VV10b5.5/C.01,
COACH semilocal basis, independent scalar coefficients and Cycle2weights.
No development/final-test leakage, new SCF or scientific model selection here.
Seven canaries test execution/resource classes; they are NOT seven complete
reactions and do not by themselves provide a100–300row fitting matrix.

## Proposed seven resource canaries

Retain candidates from `bulk_generation_approval_plan_20260907.json`, cross-
checked against `manifests/step12/step12_fitting_inventory_v1.csv`. Allseven
authoritative input files exist. This was not a fresh full orbital hash/quota audit.

| Species | Purpose | CPUs | GiB | Wall cap | Proposed route |
|---|---|---:|---:|---:|---|
| TMD01_H | smallest class, one-electron branch | 8 | 14 | 72h | mhg/mhg/normal |
| S22_06b | second memory class | 8 | 21 | 72h | mhg/mhg/normal |
| HR46_N-methylacetamide | intermediate memory | 8 | 35 | 72h | mhg/mhg/normal |
| HR46_toluene | intermediate memory | 8 | 62 | 72h | mhg/mhg/normal |
| 3019_41UracilPentane090_dim_S66x8 | largest mhg class | 8 | 117 | 72h | mhg/mhg/normal |
| BSR36_c4 | large lr8 class | 16 | 227 | 336h | lr8/lr_mhg2/mhg2_lr8_normal |
| MOR16_ed33 | largest lr8 class | 16 | 557 | 336h | lr8/lr_mhg2/mhg2_lr8_normal |

These are inherited conservative LIMITS, not runtime predictions. Total worst-
case allocation is13632core-hours if allseven exhaust their caps. The recent
VV10-only refresh times cannot predict full three-grid/PT2 feature generation.
Recommend small classes first, then explicit review before releasing the two
large cases. Maximumtwo jobs overall, at mostone per partition, no large-class
overlap. Recheck live capacity/QOS/wall limits and storage quota before launch;
do not silently shrink memory to fit an available node.

Coverage limitation: inventory reports six closed-shell species and one
one-electron doublet, no ECP/ghost centers. Keep existing open-shell/field/ECP
regression evidence, and add fresh-driver regression coverage before expanding
to such chemistry. This seven-case set is a resource smoke test, not exhaustive
chemical validation.

## Required implementation before execution

1. Preserve committed v7 refresh/scientific contract. `v7_refresh.py` is
   deliberately fixed to38legacy species/20reactions; do not simply enlarge
   its lists and treat missing features as reusable.
2. Add a separate versioned fresh-species orchestration path. Existing
   `scripts/run_step13_fresh_species.py:196` calls `derive_scalar_input` without
   v7settings (historicalb10). Explicitly supply v7 settings in the new path;
   do not silently change historical driver defaults or hashes.
3. Integrate authoritative saved-orbital preflight, isolated scratch copies,
   Q4 semilocal features on250974/99590/75302, SRHF/VV10b5.5, total frozen-core
   SS+OS PT2, pureD4ATM and field-aware fixed-energy publication. Reuse already
   validated compatible components when proven; calculate only missing stages.
   No newly optimized orbitals. Fresh features can require new PT2 evaluations,
   unlike the completed VV10-only cohort refresh.
4. Generalize the approved one-electron zero-PT2 route by validated electron
   count/input identity, with tests for TMD01_H as well as W4-17_h; do not rely
   on a single hard-coded species name. Test legacy SS/OS labels and scaling,
   field signs, ordinary print precision and incomplete-stage restart refusal.
5. Publish a common independently validated292vector/fixed/grid manifest with
   full source/spec/build/code hashes and per-stage completion boundaries.
   Preserve the38 completed v7 artifacts as immutable reuse candidates.

New proposed data namespace:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/v7_canary_v1`.
Must be checked absent before freeze; no directory created by this plan.

## Gates, tests and stop conditions

A. User reviews current validation checkpoint and this proposal. Approve the
new driver implementation and resource ceilings explicitly; this document is
not itself approval. Implement tests, then user pre-test commit before runs.

B. Unit/configuration tests; dry-run each input, verify b5.5, READ/zeroSCF,
spin/basis/field/core choices, and source/artifact hash refusal. Freeze seven
identities/resources. Measure copy/storage demand per stage, account for two
concurrent jobs plus retained failures; compare to user quota (df alone is
insufficient). Stop for a storage choice if capacity is insufficient.

C. After launch approval, run thefive smaller cases in increasing memory order,
one at a time; inspect all outputs and RSS/timing before thetwo large cases.
Run large cases sequentially only after review. No blind automatic retry.

D. Every canary must have normaltermination, verified original/working archive
identity, saved-orbital evidence, finite292features, correct zero/totalPT2 and
field reconstruction, independent published readback, all hash checks and
resource records. Reuse existing stage-specific tolerances unchanged; fixed
energy identities must not be relaxed to obtain a pass. Failures/partials are
preserved; source mutations, unsupported chemistry, parser mismatches or quota
concerns block further expansion. No fit-grid0.015 threshold imposed on an
individual raw feature vector: that test belongs to fitted reaction energies.

## From seven canaries to a larger fitting pilot

After allseven pass and user reviews cost, prepare a deterministic100–300
training-entry subset (recommend start100), selecting by dataset/category,
resource and chemical coverage, NOT observed fit residuals. Resolve the full
union of every reaction's species BEFORE launch; report exact species count,
validated reuse, missing stages and resource/storage totals for approval.
Preserve original Cycle2weights without convenience renormalization. Partial
reaction species sets must never be labeled complete rows.

Then bounded feature batches, independent matrix assembly, largerK resource
pilot and grid/start/resume checks. Select candidate/global grid rows without
forcing75302 into constraints. Report raw/recomputed gaps and coarse-grid
diagnostics separately. Larger data do not guarantee solver convergence.
Only after this evidence: propose full1498row feature generation, full-matrix
preflight and pre-bulk-MIO commit/resource approval. No automatic expansion
to the older draft's16mhg+1lr8 concurrency or full K scan.
