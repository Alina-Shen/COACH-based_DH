# Approved100-entry MIO implementation: pre-test commit checkpoint

User approved the recommended September9 plan: K14/K40, discovery/constrained/
restart for each,300s/solve,16CPU/16GiB/45min serial pilot. No new scientific
decisions. Implementation is prepared and hash-frozen, **not tested yet**.
The previous186-test result predates these changes; do not claim it validates them.

## Added code

| File | Locations | Purpose |
| --- | --- | --- |
| `revwb97m2/pilot100_inputs.py` | check_matrix28,publish58,validate86 | Validates accepted numerical matrix/authorities/reaction metadata, creates a new strict fitter adapter referencing original arrays, and verifies saved adapter/loader readback. Does not overwrite accepted matrix. |
| `revwb97m2/scripts/run_pilot100_fit_v1.py` | readback31,run69 | Versioned copy of existing solve orchestration; unchanged model builder/objective. Adds Gurobi version, whitelisted resolved parameters, NodeCount/status/runtime telemetry; strengthens code/parent/gap/grid readback. |
| `revwb97m2/scripts/pilot100_mio_v1.py` | schedule21,release40,validate72,run107 | Exact approved six-solve dependency graph; commit/plan/test/resource gates, synthetic control, fail-fast execution, all100-row grid audit, no-solve resume/readback and hashed final publication. |
| `revwb97m2/scripts/freeze_pilot100_mio_v1.py` | main14 | Standard-library hash-only freeze; does not import new implementation or run tests. Refuses to replace an existing frozen plan. |
| `revwb97m2/slurm/run_pilot100_mio_v1.sh` | whole new file |16CPU/16GiB/45min launcher; cm1 template subject to live approved route override/review. dh Python/private WLS path; retained logs in approved data tree. |
| `revwb97m2/tests/test_pilot100_mio.py` | tests36 onward |11 offline cases including parametrization: adapter round-trip/no overwrite; marker/array/source/adapter tamper refusal; schedule/start lineage; disabled release; no incumbent; no-solve/no-write resume and changed contract; failed/stale warm starts. Mocks avoid WLS environment/solver work. |

No existing tracked source/config/driver files modified. COACH ridge/C0/scientific
hash/native tolerance/grid thresholds unchanged. No new test execution, Gurobi
environment, license read/contact, adapter publication, Q-Chem work or job
submission. `git diff --check` completed; that is not a test-suite pass.

## Frozen artifacts and execution gates

Created `revwb97m2/manifests/pilot100_mio_v1/plan.json` and `release_draft.json`.
Plan pins source modules, new tests/launcher/runner, old synthetic control/runner,
scientific authorities and environment lock files. Records matrix validation hash
and exact approved schedule/resources. Scope approval is recorded; execution
remains disabled. Release requires committed matching files, passing test report
with same commit/plan identity and fresh resource review. No artificial eight-task
cap; serial pilot is approved design, not a new global submission restriction.

Planned output parent:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/pilot100_mio_v1`.
One job-ID namespace contains adapter, synthetic control, six fit directories,
sanitized failure or validated completion. No planned output root created now.
Adapter references the existing pilot100_v1 matrix; does not relabel or rewrite
its numerical validation.99590 constrains all100 pilot rows;75302 diagnostic.
Raw and recomputed gap stay separate; TIME_LIMIT with incumbent is not optimality.
Slurm peak memory must be collected independently after eventual execution.

## Next actions after user commit

1. Verify commit and frozen hashes; run new offline tests and full suite, shell
   syntax and frozen-plan checks. Record test outcome with commit and plan SHA.
2. Exercise real adapter publication/readback in an isolated approved namespace;
   preserve exact matrix hashes. Any discovered fix requires an updated reviewed
   freeze and follow-up commit; do not hide identity changes.
3. Refresh live partition/account/QOS, resources, storage and duplicate-job checks.
   Create a new approved release only after tests pass; disabled draft preserved.
4. Submit approved single bounded job; synthetic control then six real solves.
   Independently audit post-job results/telemetry/Slurm usage before recommending
   larger scale. Failure stops dependent stages without automatic retries.

STOP now for pre-test commit. Explicit scoped commands supplied in conversation.
