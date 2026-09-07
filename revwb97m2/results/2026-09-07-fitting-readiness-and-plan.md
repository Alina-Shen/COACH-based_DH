# Fitting readiness, grid gateway and bulk approval proposal

## Outcome

No bulk generation submitted. Grid test `25667476` passed on real data. Step 15
remains in progress and Step 16 remains pending; this report defines concrete
remaining acceptance checks rather than treating Gurobi support as a blanket gate.

## Feature inventory

[Machine inventory](production_readiness_20260907.json) enumerates every planned
fitting species and every missing training entry. Scan scope is
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2`, matched by exact
species path component to the frozen fitting inventory. It is not a cluster-wide
search for arbitrary aliases or external projects.

| Classification | Species | Meaning |
|---|---:|---|
| Recorded reaction-ready evidence rechecked | 38 | Vector hashes, input/identity, markers, ordinary manifest hashes and grid-prefix/difference checks pass; publication preflight still required |
| Partial/unvalidated candidates | 10 | Some relevant files exist; not permission to reuse without stage validation |
| No matching feature candidates | 2751 | No relevant vector/grid/scalar/fixed artifact matched in scan scope |
| Total fitting scope | 2799 | 1498 fitting entries |

Only **20/1498 entries** have all required species in the conservative ready set.
The existing 20-reaction arrays pass their recorded hashes. The planned
`species/production` root does not yet exist. Raw file counts (72 vectors, 238
semilocal arrays, 49 scalar manifests, 41 fixed-energy files) include duplicates
and non-fitting diagnostics; they must not be summed as completed species.

The ten partial/unvalidated species are MOR33_pr28, MOR32_pr24, 11_H2O_TA13,
3d4dIPSS_Ag_GS, CUAGAU_Au01N0_H,
IHB100x10_11.002_CH-Oa__ethene--oxalate_100, RG10N_KrKr_2p200, MOR26_pr05,
MB16-43_42 and TMB28_C1. For example 11_H2O_TA13 has validated Step-13 features,
but no corresponding reaction-ready fixed-energy publication in that run.

Audit limitations: no new SCF or Q-Chem parsing/calculation was run for this
inventory; recorded Step-14 provenance was used conservatively. Full canonical
archive/build/provenance validation and recovered fixed-energy revalidation
must precede migration into a frozen production publication. Failed/stale old
boundaries are preserved, not overwritten. The seven-case recovery adapter
must be generalized before unrestricted production execution.

## Real-data grid test

- Two 60-second R2/K=14 repeats, one thread, seed zero; WLS/dh. Warm starts
  include both pass-1 coefficients and binary selections from `25658936`.
- Top-100-per-candidate plus top-200-global-L1 rule selects all 20 available
  rows. This tests the real constrained fit, not large-cohort selection coverage.
- Job **25667476**, COMPLETED `0:0`, **2:08**, `n0030.mhg0`, batch MaxRSS 56544K.
- All source/parent/code/selection hashes and incumbent audits pass. Independent
  Python sorting reconstructs selected rows; direct `(A+D)c-Ac` agrees with `Dc`.

| Metric | Pass 1 | Pass 2 |
|---|---:|---:|
| Max 99590 difference, kcal/mol | 0.01588468 | **0.00987085** |
| Max 75302 difference, kcal/mol | 0.05390945 | **0.08640701** |
| Weighted SSE, hartree² | 3.5112109563e-07 | 1.4774750066e-06 |

Both pass-2 repeats have identical support-14 incumbents, TIME_LIMIT status,
and consistent finite reported/derived gap 1.0. No convergence proof. Practical
grid meets the frozen 0.015 limit; coarse grid is unconstrained and worsened.
Do not describe this as universal grid stability or infer that constraints
fixed the prior gap anomaly. SSE differences are between bounded incumbents,
not a measurement of the exact optimal cost of imposing grid constraints.
VV10 grid difference is zero under the frozen single-grid-evaluation policy;
SR-HF/PT2/D4 differences are zero as specified. Full VV10 multi-grid sensitivity
was not tested.

Evidence: [pilot](step15_grid_25667476/pilot_results.json),
[readback](step15_grid_25667476/readback_audit.json),
[independent grid check](step15_grid_25667476/independent_grid_readback.json).

## Step 15 completion checklist — R2 C0 scope

| Item | Status | Concrete acceptance evidence |
|---|---|---|
| Named R2, independent scalar bounds, mandatory support and UEG | Done for pilot | Existing model tests and incumbent audits |
| WLS and finite/strict-JSON gap reporting | Done operationally | Compute-node probes; retain anomaly state and separate derived gap; no unjustified optimality label |
| Real pass-1 to pass-2 grid path | Done on 20 rows | 25667476 + independently reconstructed selection/energy differences |
| General selected-row coverage | Pending | Fixture with more than 200 rows and multiple candidates; verify union/dedup/ties independently, plus reject bad dimensions/nonfinite inputs |
| Production runner controls | Pending | Manifest-driven scan [14,24,32,40,48,64,80], 16 threads/7200 s, two repeats per warm start, saved pass-2 starts, resumable immutable outputs; no automatic launch |
| Failure/status handling | Pending end-to-end | Inject infeasible/no-incumbent/timeout/stale-input cases; never mark failed outputs complete; preserve partial outputs |
| Larger real-data gateway | Pending | Use available approved 100–300 reaction cohort when assembled, both grid passes, finite objective/constraints/restarts and recorded bound/gap; tolerances frozen in advance |
| Constraint and factor audit | Pending | Dense-domain exchange/correlation factor evaluation with reproducible extrema/locations; C2/C3 optional, not mandatory for first C0 fit |
| Scope decision | Explicit | R1 features are not a prerequisite for R2-only C0 fitting; do not claim validated R1 fitting without separate features |

## Step 16 completion checklist

1. Implement a project-owned analysis entry point consuming frozen feature/data-role
   manifests, without launching fits or Q-Chem. Unit-test direct fixed+feature
   predictions and hartree/kcal conversion.
2. Implement dataset-specific errors, NER normalization using frozen
   `Standard_errors.csv`, category/overall aggregation and the three-dataset
   overfitting diagnostic. Test hand-computed small fixtures, missing/zero
   denominators, duplicate entries and declared treatment of weights.
3. Freeze the ranking/tie-break policy before scientific candidate selection;
   record parameter count, objective/gap/stability, both grid metrics and dense
   factor diagnostics. Do not invent an unapproved composite score.
4. Enforce roles: model selection uses **8377 reactions / 13907 species** over
   all 137 GSCDB137 datasets, not just coefficient-fitting data. Final SC74,
   OEEFD, BigNC, GDB9 and geometry assessment must not tune candidates. These
   broader features are outside this 2799-species approval request.
5. Validate R0/parent comparator joins and end-to-end report on a bounded cohort;
   characterize training-only vs selection coverage honestly. Preserve diagnostic
   pilot coefficients as diagnostics, not selected final candidates.

## Bulk-generation proposal — approval requested, not executable yet

[Machine proposal](bulk_generation_approval_plan_20260907.json) includes all
2761 remaining targets, 38 reuse candidates and deterministic canary choices.
Remaining means **2751 with no candidates plus 10 requiring validation/completion**,
not necessarily 2761 full recomputations.

| Memory class MB | Remaining | Slurm GiB | CPUs | Partition | Time limit |
|---:|---:|---:|---:|---|---|
| 3750 | 2110 | 14 | 8 | mhg | 72 h |
| 7500 | 295 | 21 | 8 | mhg | 72 h |
| 15000 | 186 | 35 | 8 | mhg | 72 h |
| 30000 | 107 | 62 | 8 | mhg | 72 h |
| 60000 | 29 | 117 | 8 | mhg | 72 h |
| 120000 | 26 | 227 | 16 | lr8 | 336 h |
| 300000 | 8 | 557 | 16 | lr8 | 336 h |

Retains conservative Step-12 resource requests; these time limits are **not runtime
predictions**. mhg uses account mhg/QOS normal; lr8 uses lr_mhg2/mhg2_lr8_normal.
Live checks show appropriate physical memory and associations; recheck scheduling
and account quotas at submission. Shared filesystem free space does not establish
user quota or capacity for all archive copies; storage preflight remains open.

### Proposed stages and approval boundary

**A — Implementation and preflight, no bulk:** integrate approved legacy-spin
scaling, one-electron zero PT2 and field-aware fixed energy into the generalized
driver, with regressions covering the seven recovered species. Freeze the full
reaction-ready contract including fixed energy (not just Step-13's eight feature
boundaries), revalidate the 38 reuse candidates and 10 partial species, calculate
archive-copy footprint/quota, and freeze code/build/input hashes. No new parent SCF.

**B — Seven representative cases, then STOP for review:** TMD01_H (3750), S22_06b
(7500), HR46_N-methylacetamide (15000), HR46_toluene (30000),
3019_41UracilPentane090_dim_S66x8 (60000), BSR36_c4 (120000), MOR16_ed33 (300000).
Chosen as lowest AO count among remaining species per class. At most **one mhg
and one lr8 job simultaneously**. The one-electron case also exercises the
approved zero-PT2 path. Measure scalar/fixed-stage resources before expansion.

**C — Separately approve wider batches after reviewing B:** batches up to 256
mhg species; **16 mhg jobs total across all five memory classes**, and **one lr8
job total across both large classes**. Maximum 17 jobs/144 CPUs, not seven
independent full-size arrays. Stop on common systematic failures, source mismatch,
quota concerns or unexpected resource demand. No blind retries; at most one
engineered retry per species after diagnosis and approval. Preserve failed runs;
no automatic deletion/overwriting.

**D — Validate and assemble:** independent species/fixed/grid checks and complete
1498-entry reaction assembly. Scientific fitting scans and 13907-species
model-selection coverage require separate plans/approval; do not launch them as
implicit follow-ons to feature generation.

**Recommended approval now:** stages A and B only, with C requiring a new review.
No Q-Chem bulk scripts were submitted or production root created this turn.
No trustworthy total runtime/storage estimate is claimed until preflight and
class canary measurements are available.
