# Bounded100-entry grid-constrained MIO pilot — review proposal

Date:2026-09-09. Status: **proposal, NOT execution authorization**.

## Completed preparation

Verified clean commit `6c50dd65d9628f4c44a6c78d675e615c95fcf900` containing the
completed matrix integration. Fresh read-only preflight checked completion marker,
every exported artifact hash, recorded authorities, assembly-code hash, current
specification, exact source reactions, finite arrays, original weights and
target=reference-fixed. PASS100x292/224species/49groups. The seven loaded numeric
arrays occupy704000bytes; this is NOT a solver-memory estimate. Objective weights
range0.02–10000; retain them unchanged, do not normalize opportunistically.
Evidence: `revwb97m2/results/2026-09-09-pilot100-mio-preflight.json`.

Input root:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/matrices/pilot100_v1`.
Validation SHA256:
`4e22fc55ed9c78609865463c5e08fdef0283abc07d07112dfb508b3fe4791f18`.
Scientific SHA256:
`32c64b5d4cec1641c1b77e094e776a0aaa62fb20a9dd101c7736dfd92ac942fc`.

Reviewed `fit_inputs.py`, `scripts/run_v7_fit.py`, `mio.py`, `grid_selection.py`,
`solver_reporting.py`, prior real20 pilot25679856 and the approved September7
test/production plan. No solver initialization, license read/contact, native
calculation, Slurm submission or scientific/core-code change this turn.

## Important interface gap and implementation gate

The numerical matrix gate passed, but `fit_inputs.load_inputs` requires a fitter
`inputs.json` plus assembly-validation fields not emitted by the numerical
exporter's `validation.json`. No `inputs.json` exists yet. This is an adapter
publication task, NOT a need to regenerate chemical features or relabel old data.

After approval, add a separately versioned adapter builder that:

1. Repeats current marker/artifact/authority/source-reaction/spec checks.
2. Publishes manifest schema1/status validated/role coefficient_fitting, original
   COACH Cycle2 weight policy, ordered100 reaction IDs and approved energy values.
3. Links exact existing arrays by absolute path and SHA256; creates the required
   assembly-validation record with `scientific_specification_sha256` and
   `array_sha256`, anchored to the current matrix validation hash.
4. Preserves VV10's single-SG1 evaluation/zero difference explanation. Zero VV10
   columns do not demonstrate independent VV10 grid convergence.
5. Calls the existing strict loader and compares every loaded array with the
   audited source; refuses tampering, wrong role/spec, incomplete markers or
   changed references/weights. Writes to a new input-adapter namespace, never
   alters the accepted numerical matrix or its validation hash.

Add bounded orchestration and tests for commit/release identities, no-incumbent
failure, start lineage, resume-without-solve and tamper refusal. Retain existing
core objective/constraints and hash-pinned historical drivers. Record exact
Gurobi version, resolved parameters, source/start/result hashes and per-solve
status/incumbent/bound/raw+recomputed gap, runtime, NodeCount when available,
plus Slurm RSS. Credentials must not enter any manifest or diagnostic export.

Implementation checkpoint: prepare code/tests/frozen disabled draft, provide
explicit user commit commands; execute new tests only after pre-test commit.
Then check results and live resources before approved submission. This preserves
the established pre-test/pre-execution gate rather than launching an untested
new adapter. Do not change stale descriptive YAML status fields now: they are
hash-pinned scientific authority; current operational status belongs in STATUS.

## Recommended bounded schedule (requires approval)

| Stage | Size | Start and grid policy | Maximum solver time |
| --- | --- | --- | --- |
| Synthetic control | existing fixture | Existing grid-active/start/resume/tamper control;10s cap per solve | Small, separate from real100 evidence |
| Discovery14 | K14 | No grid constraints, no imported20-row start | 300s |
| Discovery40 | K40 | No grid constraints; independent initial solve | 300s |
| Constrained14 | K14 | Start from Discovery14; candidate union from both discoveries | 300s |
| Restart14 | K14 | Start from Constrained14; same frozen candidate union | 300s |
| Constrained40 | K40 | Start from Discovery40; same candidate union | 300s |
| Restart40 | K40 | Start from Constrained40; same candidate union | 300s |
| Post-job readback | both | Recompute all six audits; resume constrained/restart outputs without optimize | No additional solve |

K is an **upper bound on selected support**, not exactlyK nonzero coefficients.
The four mandatory scalar selections count towardK: K14 allows up to10 semilocal
selections, K40 up to36. K40 is an intermediate member of the declared scan;
it tests a materially larger model without pretending to test the K80 endpoint.
K14 connects to earlier20-row behavior, but different data/time budgets prevent
attributing any gap change solely to dataset size. Existing20-row starts are
incompatible input identities and must not be silently imported.

Recommend one serial job with16CPUs/16GiB/45min Slurm limit. Six real solves have
a nominal maximum1800s (30min), approximately8core-hours at16threads, plus
control/setup/readback overhead. TimeLimit is a cap, not a convergence/finish
prediction. The extra Slurm time is overhead allowance. Memory16GiB is provisional
headroom over the prior real20 allocation8GiB, not extrapolated from matrix bytes.
No automatic time/memory increase or resubmission on failure. One serial job is
a proposed pilot design for clear resource/start evidence, NOT reinstatement of
the removed eight-running-task cap or a global future concurrency restriction.

Route to be selected via fresh `$partition` review at submission; cm1, mhg or
lr8 with approved account/QOS may be used. No stale queue-time promise and never
lr_lowprio. Retained adapter/solver outputs/logs under approved
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2`; disposable scratch
under `/clusterfs/mhg-data/yaoshen/scf_read/revwb97m2`. Use dh and private WLS
license on compute node; do not copy/read credentials into notes.

## Frozen science and grid interpretation

Use R2/C0, omega0.3, gamma_ss0.01, VV10b5.5/C0.01;292 columns, all original weights.
Objective remains explicit weighted SSE +1e-10*sum(beta²). Save SSE and ridge
separately. Bounds/UEG/mandatory scalar support unchanged. Seed0,16threads;
FeasibilityTol/IntFeasTol1e-9, MIPGap1e-4, MIPGapAbs1e-10. No numerical solver
workaround, coefficient rescaling or objective normalization change by stealth.

Pass2 internal99590 limit0.014985kcal/mol; independent public audit0.015 with no
added slack.75302 remains diagnostic only. Existing selector verified to select
all100 rows: global top200 already covers the whole pilot. Consequently every
pilot row is constrained in pass2 regardless of discovery coefficients. Preserve
the COACH selection algorithm rather than reducing200 to force selection.
Real100 tests broader chemical feasibility, not >200-row subset selection or
full1498 conditioning. Existing >200-row synthetic checks cover selector logic;
larger/full numerical pilots still follow before bulk fitting.

## Acceptance and failure decisions

- Workflow PASS requires successful strict adapter loading and a saved audited
  incumbent from every scheduled solve, valid bounds/support/UEG, independently
  recomputed SSE/ridge/objective and selected-row identities. Require public99590
  compliance for constrained/restart candidates, not unconstrained discoveries.
- Check serialized artifacts/lineage and readback-only resume; evaluate99590 and
 75302 across all100 entries. Report training errors only as pilot diagnostics,
  not COACH full-development NER ranking or final model selection.
- TIME_LIMIT with an audited feasible incumbent is a workflow result, not proof
  of optimality. Preserve raw gap/null+state and recomputed absolute/relative gap;
  nonfinite or inconsistent gap remains a reported solver diagnostic, never
  silently repaired. Report stopping parameters and status separately.
- No incumbent, numerical/error status, failed independent audit, tampered input
  or failure of the public grid limit stops dependent stages. Preserve evidence
  and request review; no dropped constraints, row deletion, zero-fill, arbitrary
  tolerance relaxation or auto-retry. TIME_LIMIT alone does not prove infeasibility.
- After pilot: use measured RSS/runtime/incumbent/bound behavior to recommend
  next scale. Solver-gap concerns may persist even if chemical workflow passes.
  Neither full1498 feature generation, bulk scan nor final assessment is authorized
  by this proposal. No coefficient selection for the final functional here.

## Alternatives for user review

Recommended: K14/K40,300s per solve,16CPU/16GiB/45min serial job.
Lower-cost: K14 only (3real solves,15min nominal solver cap), but no larger-K test.
Stronger endpoint: replace K40 withK80, which is more demanding and should be
explicitly approved; not an assumption from the current “next step” request.
Approve the recommended plan before implementation/freeze and pre-test commit.
