# Full-data optimizer integration and validation proposal

Date: September 10, 2026. **Prepared for review; no submission or bulk approval.**

## Verified checkpoint and work performed

Verified clean commit `12080b846242339f6f065244d9459298f371d4d6` containing
the accepted full1498 matrix integration. Ran a fresh strict numerical/input
readback: source/publication hashes, metadata roles/weights/references, finite
arrays, target identity and exact100 pilot-row agreement all PASS.

Matrix directory:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/matrices/full1498_v1`.
Validation SHA: `493a6a465ea71539e291501645d6a186ffd86f1bd597174035d6fe7c1675eef8`.
Input manifest SHA: `8d9f0ddd0282598f05aa25f22b54c8b361f949453c438d396c3519e00817242e`.
Spec SHA: `32c64b5d4cec1641c1b77e094e776a0aaa62fb20a9dd101c7736dfd92ac942fc`.

Reviewed the existing strict matrix adapter, generic model builder, pilot solve
driver/orchestrator, grid selector, accepted100 pilot report, scientific spec,
and September7 fitting plan. Added only a solver-free diagnostic script:
`scripts/preflight_full1498_mio_v1.py` (inspect at line11; CLI at line41).
It records dimensions/ranges, weighted-feature singular values, fixed global
grid rows and immutable identities. No Gurobi environment, WLS license read,
network call, optimization, Slurm submission or scientific-code change occurred.
No new optimizer unit tests were run: executable orchestration is not yet changed.
Existing256-test acceptance remains the preceding committed checkpoint's evidence.

Fresh [preflight JSON](./2026-09-10-full1498-mio-preflight.json) records:

- 1,498x292 features, all2,799 species; unchanged weights0.02–10000.
- Five fitter arrays total10,521,952bytes (~10.03MiB), not a solver-memory estimate.
- Before presolve:292 coefficients,292 selection binaries,1,498 residuals:
  2,082 variables and2,088 nongrid linear constraints. Each selected grid row
  adds two inequalities. Dimensions derived from current model code, not a
  newly instantiated/licensed model; validate against actual model telemetry later.
- Weighted A numerical rank290 using tolerance2.7401e-11; largest/smallest
  singular values82.3794/7.3305e-13. This is a diagnostic of near dependence,
  not exact algebraic rank, MIQP conditioning, infeasibility or solver-gap cause.
  Do not drop columns, change weights, normalize the objective or increase ridge.
- The fixed global grid selection contains200 distinct rows. Candidate-dependent
  rows cannot be frozen until the full-data discovery solves exist.

## Integration checklist before any new solver execution

The matrix already has a valid `inputs.json`; no new energy adapter or feature
generation is needed. The solve driver accepts arbitrary row counts, but the
existing pilot orchestrator is intentionally100-specific. Do not repoint or
modify its frozen plan and historical results.

| Item | Existing capability | New full-data work needed after approval |
|---|---|---|
| Matrix identity | Full assembler validates all source/artifact identities and real loader inputs | New orchestration must pin full validation/input hashes and invoke strict readback, not merely load any schema-compatible file. |
| Mathematical model | R2/C0 explicit weighted residuals, ridge, binaries, bounds, UEG and grid constraints | Reuse unchanged; capture actual model dimensions and resolved parameters. |
| Solve/start/readback | run_pilot100_fit_v1.run supports arbitrary n and strong lineage | Reuse its callable core with a separately versioned full-data entrypoint; retain frozen module bytes. Reject100-entry starts because input hashes differ. |
| License handling | Compute-node private WLS path and quiet error reporting | Full entrypoint opens WLS only for actual solves; readback/resume must branch before license initialization. Existing pilot CLI initializes WLS even on --resume, so do not use that CLI for license-free readback. |
| Grid row audit | Stable global200 + candidate100 union selector | Replace the orchestrator's hardcoded arange(100) assertion with exact independently reconstructed full-data selection. Save row IDs and candidate hashes. |
| Schedule/release | Pilot has committed code/plan, tests and route gates | Add separate frozen full1498 plan/launcher/release, disabled by default; verify commit, test evidence, resources and matrix before work. |
| Failure/resource records | Existing per-solve telemetry and fail-stop behavior | Capture memory, status/incumbent/bound/gaps, full-grid violations and unchanged-output readback; no automatic retries or dropped constraints. |

After plan approval: implement separate orchestration/entrypoint/launcher and
unit tests, freeze a disabled plan, then stop for **pre-test user commit** with
commands. After that commit run unit/configuration/synthetic and real read-only
adapter checks. Review live resources using `$partition`, respecting <999 active
user tasks and no lr_lowprio. Only then prepare the approved bounded release.
Keep code outside the native top-level dependency glob; never mutate frozen
historical source contracts to accommodate a new integration file.

## Recommended bounded full-data schedule — approval requested

All six solves use all1,498 training rows, R2/C0, the existing scientific spec,
seed0 and16threads. **600s per solve**, serial execution in one job.

| Solve | K | Grid constraints | Start |
|---|---:|---|---|
| Discovery14 |14|None|None|
| Discovery80 |80|None|None|
| Constrained14 |14|Frozen union from both discoveries|Discovery14|
| Restart14 |14|Same frozen union|Constrained14|
| Constrained80 |80|Same frozen union|Discovery80|
| Restart80 |80|Same frozen union|Constrained80|

K is the maximum selected support including four mandatory scalar selections;
it is not necessarily the number of numerically nonzero coefficients. K14/K80
tests the low and high endpoints instead of repeating only the earlier K40
case. It is not a complete K scan or final model selection. Seed0 is retained;
warm-started repetitions are not independent statistical random-seed replicates.

Recommend **16 CPUs,32GiB,90min** Slurm allocation. Six600s caps sum to60min
nominal solver time/16core-hours, plus startup, synthetic control, model building,
readback and output. A TimeLimit is not a convergence forecast; actual elapsed
can exceed nominal solver time.32GiB is provisional headroom above the accepted
100-entry pilot's1.55GiB peak, not a linear extrapolation or guaranteed ceiling.
No automatic extension or memory escalation if insufficient. Live partition,
account and QOS remain undecided until release review. No job is submitted now.
One serial job is this test design, not a new global job concurrency restriction.

Retained outputs/logs go under the approved heavy-data root, in a new
full1498-specific namespace; temporary scratch goes under the approved scratch
root. Do not overwrite pilot/full matrix inputs. No license content in reports.

Alternative: K14/K40 for a less demanding intermediate check, but it leaves K80
resource/feasibility behavior untested. Recommend the endpoint plan above.

## Grid semantics and pass/failure gates

For two discovery candidates, the stable union has200–400 rows (overlap can
reduce it), not all1,498. For the100-entry pilot, global200 already selected
everything; that pilot could not exercise real-data subset behavior.

- Optimization enforces only the declared union, with internal99590 threshold
  0.014985kcal/mol. Independently reconstruct its indices and check its public
  0.015 threshold without extra slack.
- Evaluate99590 and diagnostic75302 on **all1,498 rows**; record maxima and all
  violating reaction IDs, including selected/unselected membership. Discovery
  is intentionally unconstrained and does not need to meet the grid threshold.
- Recommended advancement gate: constrained/restart candidates must also pass
  the public99590 limit across the entire training matrix before this bounded
  checkpoint clears bulk release. If an unselected row fails, distinguish a
  mathematically valid selected-constraint incumbent from failure of this
  broader validation gate. Stop and ask; do not silently add rows, relax limits
  or convert75302 into a constraint. This is a proposed acceptance gate, not a
  change to the scientific model's selected-row constraint definition.
- Each solve needs a saved independently audited incumbent: support, UEG,
  coefficient bounds, SSE and ridge separately, solver-objective agreement,
  selected-grid checks when applicable, parent hashes and resume idempotence.
  TIME_LIMIT with a valid incumbent is workflow evidence, not optimality.
- No incumbent, numerical/error status or failed source/objective/constraint
  audit stops dependent work. Preserve evidence. A600s failure to find an
  incumbent does not demonstrate chemical infeasibility.
- Report raw and recomputed absolute/relative gaps and nonfinite state faithfully.
  Weak bounds may persist at full scale. Dataset size alone does not guarantee
  that the gap issue disappears. No unsupported diagnosis or parameter workaround.

Unit tests must cover full-data hash pinning,100-vs1498 start refusal, >200-row
stable union reconstruction, unselected-row reporting/advancement failure,
no-incumbent fail-stop, release/commit tampering, exact resources, output
preservation and license/optimize-free resume. Run existing synthetic active-grid
control on compute node before real solves; budget it within job overhead.

## Later bulk fitting proposal — separate approval and commit

Retain the declared coarse K=[14,24,32,40,48,64,80],16threads,7200s per solve,
two grid passes and two solves per K per pass (initial + warm-started restart).
That is28 solves,56 nominal solver-hours serial/896core-hours. This scan IS bulk
fitting, not another preparatory test. All discovery solves precede pass2.
Propose freezing the pass2 row union from all14 audited discovery outputs,
including restarts; use each K's validated discovery restart to seed pass2,
then its pass2 initial output to seed its pass2 restart. Save all candidates.
Candidate-pool and repeat interpretation require explicit review, not inference.

Initial solver concurrency1 is recommended until measured full-data RSS and WLS
behavior are reviewed; it is not a standing user queue cap. Provisional per-solve
request16CPU/32GiB/3h (2h solver cap plus overhead), to be revised from this bounded
test and live partition review. No walltime/queue completion promise now.

The seven-K project scan is not COACH's exhaustive integer24–80 exploration.
Full24–80 would require a versioned expansion of the currently restricted spec
and affected tests, plus approval:57K x4 solves=228 solves/456 nominal solver-hours
/7,296core-hours. Recommend the declared coarse scan first, then reviewed
refinement if justified by declared development metrics. Do not expand silently.

Pre-bulk release needs passing bounded full-data evidence, an exact executable
scan/start/candidate plan, resources, code/spec/matrix hashes, user commit and
explicit approval. NER/development-domain feature coverage and Step16 analysis
remain required before final scientific ranking, not before initial fitting.
Retain COACH lowest overall mean NER among eligible candidates and final user
review; do not select solely by training SSE, smallest K, or solver gap. Deferred
tie/trade-off decisions stay deferred until needed. Protected final-assessment
sets must not influence this scan or refinement.

## Decision requested

Approve the recommended K14/K80 six-solve600s schedule,16CPU/32GiB/90min
allocation, and full-training public-grid advancement gate for implementation.
Bulk schedule/resources remain a later separate release decision. No new
license key, feature generation or Q-Chem rebuild is needed for this step.
