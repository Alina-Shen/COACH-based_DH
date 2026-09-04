# Step 12 measured feasibility and resource decision checklist

Step 12 converts the frozen scientific protocol into an executable, bounded
production policy. It does not choose coefficients or inspect final-assessment
errors. The gate closes only when decisions D12.1–D12.9 below are recorded and
the resulting pilot policy is internally consistent.

## Decisions and completion evidence

| ID | Decision still required | Recommended decision and required evidence |
|---|---|---|
| D12.1 | Classify terminal job `25431773` | Let the original `12:00:00` `mhg` run terminate unchanged. Record final state, elapsed time, last SCF cycle, convergence state, MaxRSS, disk I/O, and artifact status. A clean timeout/nonconvergence is valid upper-tail evidence; L14 is not a fitting gate. |
| D12.2 | Fix initial production scope | Generate only the locked coefficient-fitting population first: 2,799 unique species supporting 1,498 reactions. Do not initially generate all 17,452 energy-role species, the 13,907-species model-selection population, or BigNC. This is already decided scientifically and should be encoded in the production plan. |
| D12.3 | Freeze mandatory stage work | For each fitting species: validated fixed all-UKS omegaB97M-V parent, shared-density R1/R2 semilocal features on `250974`, `99590`, and `75302`, one VV10 evaluation, one frozen-core total RI-UMP2 evaluation, then hash-validated R1-78/R2-291 assembly. Retain independent restart boundaries; do not recompute a completed valid stage. |
| D12.4 | Define empirical resource tiers | Join the 2,799-species population to orbital AO count, auxiliary AO count, electron count, spin, ECP/GEN/ghost flags, atom count, and static three-center estimate. Sample every upper-tail/chemistry stratum. For each tier freeze CPUs, memory, walltime, block size, scratch, and partition. Static DF size is a routing predictor, not an observed-memory claim. |
| D12.5 | Set memory acceptance margins | For each stage/tier, require measured peak RSS plus a documented safety margin to fit strictly below physical node memory. Validate RI-MP2 scratch separately. The provisional stops (`orbital AO=1800`, `auxiliary AO=4500`, static DF estimate ≤ half requested memory) remain stop rules until stratified pilots justify replacements. |
| D12.6 | Set walltime and retry policy | Routine tier: one bounded attempt. Retry only after diagnosing the terminal record and changing an engineered cause (SCF strategy, stage split, memory/partition, or walltime). A `72 h` `mhg` retry is optional for later complete BigNC assessment, not coefficient-fitting production. Never repeat an identical timeout automatically. |
| D12.7 | Choose partition/account/QOS routes | Current CPU routes are `cm1/lr_qchem/condo_qchem`, `mhg/mhg/normal`, `lr8/lr_mhg2/mhg2_lr8_normal`, and low-priority `lr_bigmem/lr_mhg2/lr_lowprio`. Use CPU partitions. `cm1` has about 242 GB/node, `mhg` about 258 GB/node, `lr8` about 774 GB/node, and `lr_bigmem` about 1.55 TB/node. A chosen partition must have physical memory strictly above the request; final ranking must be refreshed immediately before scripts are generated. |
| D12.8 | Bound concurrency, storage, and failure handling | From the stratified pilot, calculate CPU-hours, peak simultaneous scratch, retained bytes/species, maximum array concurrency, and a submission throttle. Missing/corrupt/stale artifacts must be preserved and reported. A fitting species may not be silently skipped: either engineer it to completion or explicitly revise and re-freeze the training population before any fit. |
| D12.9 | Publish the sign-off artifact | Write a versioned Step-12 manifest containing tier predicates, exact resources, routes, retry limits, concurrency/storage budgets, pilot species/results, exclusions, and authority hashes. Validate with `sbatch --test-only` and a small real array. Only then set `production_submission_authorized: true` and allow Step 13 to emit executable production scripts. |

## What COACH does

The COACH paper/protocol supplies scientific and optimizer precedents, not a
Slurm production policy:

- It forms a weighted linear least-squares problem from fixed base-functional
  quantities and uses MIO/Gurobi for sparse selection.
- It constructs high-resolution and comparison-grid matrices and applies a
  `0.015 kcal/mol` grid-sensitivity constraint to selected sensitive cases.
  The released workflow uses blocked grid processing to bound memory.
- The manuscript method describes the `250974`/`99590` optimization comparison;
  the final functional is assessed on `75302` and `99590` grids.
- The released optimization description uses 16 CPU cores, a 1–2 hour Gurobi
  limit per sparsity value, one restart, sparsities 24–80, and estimates about
  3,000 CPU-hours per functional-form combination. These settings inform the
  later MIO pilot, not species-feature memory/walltime.
- COACH evaluates BigNC as an assessment/design domain and explains that its
  hybrid comparator needs D4-ATM for good BigNC behavior. Our revwb97m2 model
  deliberately has no D4/ATM feature, and BigNC remains outside coefficient
  fitting; therefore it cannot determine Step-12 production tiers.

## What the omegaB97M(2) paper does

- It uses fixed omegaB97M-V orbitals (xDH), frozen-core RI-MP2, def2-QZVPPD
  without counterpoise, a `99,590` semilocal grid generally, special
  `500,974` treatment for AE18/RG10, and SG-1 VV10 grids (special `75,302` for
  AE18/RG10).
- It separates 870 training, 2,964 validation, and 1,152 test points; trains
  candidate subsets on training data, ranks transferability on validation,
  and uses an independent test stage after RANSAC.
- Its cost study uses Q-Chem 5.0 with four threads on three examples and
  reports that RI-PT2 was not the bottleneck up to roughly 3,000 basis
  functions in those examples. That is useful plausibility evidence, but it
  is not a memory bound, scheduler tier, or guarantee for our all-UKS PySCF,
  per-species GSCDB bases, ghost systems, and much larger auxiliary spaces.

## Consequence for this project

Adopt the papers' scientific principles—fixed parent orbitals, RI-MP2,
well-defined grids, weighted fitting, strict data roles, sparse selection, and
independent assessment—but derive Slurm resources from our own stage-resolved
measurements. The six completed gateways establish correctness and small-case
behavior. Job `25431773`, stratified fitting-population pilots, and a small
array test establish the resource policy. Paper timings must not be converted
directly into production walltime or memory requests.

## Decision freeze update — 2026-09-01

- **D12.1 complete:** job `25431773` reached `TIMEOUT` at `12:00:01` after ten
  unconverged parent-SCF cycles. `MaxRSS=8,119,928K`; no completed parent or
  downstream artifacts exist. This is accepted walltime/convergence evidence,
  not OOM and not a fitting gate. The temporary checkpoint and logs remain
  preserved.
- **D12.2 complete:** the initial population is exactly 2,799 unique GSCDB137
  coefficient-fitting species supporting 1,498 reactions.
- **D12.3 frozen:** every species requires seven independently reusable logical
  boundaries: parent; semilocal `250974`, `99590`, and `75302`; VV10; total
  frozen-core RI-UMP2; and hash-validated R1-78/R2-291 assembly. Never
  recompute a completed, independently validated boundary and never silently
  skip a fitting species.
- **D12.4-D12.5 candidate frozen:** authoritative Q-Chem `MEM_TOTAL` creates
  two routing tiers. The 2,765 species at or below 60,000 MB use
  `mhg/mhg/normal`, 8 CPUs, and 72 hours. The 34 species above 60,000 MB use
  `lr8/lr_mhg2/mhg2_lr8_normal`, 16 CPUs, and 336 hours. Seven scheduler
  base memory classes use `ceil((1.25*MEM_TOTAL+4096)/1024) GiB`, followed by
  the user-requested 1.5x SBATCH multiplier and whole-GiB ceiling: 14, 21, 35,
  62, 117, 227, and 557 GiB. Every request still fits strictly below the
  smallest live node in its route.
- **D12.6 retry policy frozen:**
  never repeat an identical timeout automatically; one resubmission maximum.
  A relatively large `mhg` timeout moves to `lr8` for 336 hours. An OOM stays
  on the same partition with a 1.5x memory request, subject to strict physical
  fit. Any other failure or failed resubmission is written to
  `step12_failure_ledger_v1.csv` with job/input/output paths and brought to the
  user. The user confirmed that “relatively large on mhg” is exactly the
  `MEM_TOTAL=60000 MB` class (29 species). After either timeout or OOM these
  species move to `lr8` for 336 hours; OOM also raises 117 GiB to 176 GiB.
- **D12.7 candidate complete:** live 2026-09-01 checks confirmed both account/
  QOS associations. `mhg` had 4 idle nodes and 257,830-515,986 MB physical
  memory; `lr8` had no idle nodes at the snapshot and 773,569 MB per node.
  The partition skill helper was absent, so its documented manual procedure
  was used. Maximum requests of 117 GiB on `mhg` and 557 GiB on `lr8` retain
  strict physical-memory fit.
- **D12.8 candidate frozen:** initial concurrency caps are 16 on `mhg` and 1
  on `lr8`. The largest conservative static RI three-center predictor is
  1,017.46 GiB, so only one upper-tail large pilot runs at once. `/clusterfs`
  had 2.5 PiB available and no reported user quota. Failed, partial, stale,
  or corrupt artifacts are preserved and reported.
- **D12.9 pilot execution in progress:** all seven memory-class scripts passed
  shell validation and `sbatch --test-only`. The user approved the first three
  corrected `mhg` scripts after a pre-chemistry wrapper failure. Corrected jobs
  `25452149`-`25452151` started normally; at the ten-minute checkpoint,
  `25452149_0` had completed in 2m17s with all parent, semilocal, scalar, and
  assembly validations passing, while the other four tasks remained running.
  Production remains unauthorized. The non-authorizing candidate is
  `revwb97m2/manifests/step12/step12_resource_signoff_candidate_v1.yaml`.
  Final sign-off will be published only after the approved pilots validate
  the resource rules and the exact Step-13 seven-boundary executor passes a
  small real array.

## Corrected first-batch terminal review — 2026-09-01

- Corrected array tasks `25452149_0` and `25452149_1` completed and validated.
  Tasks `25452149_2`, `25452150_0`, and `25452151_0` completed their reusable
  parent and three-grid semilocal stages, then failed in RI-UMP2. They were not
  scheduler OOMs: PySCF rejected allocation of the full in-core `t2` tensor at
  configured limits of 3,750, 7,500, and 15,000 MB. Batch MaxRSS values were
  about 3.00, 5.52, and 10.44 GiB, respectively.
- The production feature is the total PT2 correlation energy; amplitudes are
  neither consumed nor retained. `scalar_features.py` now calls the supported
  PySCF energy-only path `kernel(with_t2=False)`, while still validating total
  equals same-spin plus opposite-spin correlation. A unit regression and a
  real recomputation of `3d4dIPSS_Ag_GS` passed; the energy-only PT2 differed
  from the prior amplitude-retaining value by only `-9.44e-15 Eh`.
- This is an engineered memory fix, not a scientific-policy change and not a
  reason to increase scheduler memory yet. Failed temporary scalar trees are
  preserved; retries publish under `scalar_energy_only_measurement_v2` and
  reuse completed parent/semilocal work.
- Step 12 remains open. Before sign-off, real execution must validate the
  three energy-only retries, the unmeasured 30,000/60,000/120,000/300,000-MB
  classes, and a small array using the exact Step-13 seven-boundary executor.
  All seven current pilot scripts pass `sbatch --test-only`, but no new jobs
  were submitted because the frozen policy requires explicit user approval.
