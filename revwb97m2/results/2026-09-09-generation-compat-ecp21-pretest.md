# Generation compatibility and21-ECP reference review: pre-test checkpoint

Verified clean user commit6d32f98. Implemented the recommended versioned
compatibility path and reviewed all21 ECP cases. **New implementation is untested**
pending user pre-test commit. No native execution, Q-Chem rebuild, new SCF,
scientific parameter/basis/spin change, cleanup or submission.

## Completed reference review

All21 authoritative inputs are byte-identical to production inputs in
`/clusterfs/mhg-data/yaoshen/wb97m_os/GSCDB/wb97m_os_rimp2/work`.
All21 production outputs terminate normally; no Q-Chem fatal markers. Reported
alpha/beta counts agree with the bridge. All use embedded28-core ECPs,
BASIS GEN/ECP GEN/PURECART11111/SCF_GUESS READ/N_FROZEN_CORE FC. Full blocks
contain multiple element definitions; preserve them, not only the active element.
Uppercase ECP labels are matched case-insensitively without rewriting inputs.

| Element/state | Explicit electrons | Spin=alpha-beta |
| --- | --- | --- |
| Ag GS/GS+ |19/18|1/0|
| Cd GS/GS+ |20/19|0/1|
| Mo GS/GS+ |14/13|6/5|
| Nb GS/GS+ |13/12|5/4|
| Pd ES/GS/GS+ |18/18/17|2/0/1|
| Rh GS/GS+ |17/16|3/2|
| Ru GS/GS+ |16/15|4/3|
| Tc GS/GS+ |15/14|5/6|
| Y ES |11|3|
| Zr ES/GS/GS+ |12/12/11|4/2/3|

Evidence: `revwb97m2/results/2026-09-09-ecp21-production-reference-review.json`
includes exact input/output hashes, paths, rem blocks and bridge/electron data.
Successful old production is input/reference evidence, not proof that the new
six-stage feature gateway has already run. No uncertain scientific choice was
invented; reviewed production values are preserved exactly.

## Added implementation files

| File | Main locations | Explanation |
| --- | --- | --- |
| scripts/generation_compat_v1.py | dependency comparison9,contract14,native loader29 | Accepts exact historical dependency bytes plus only the known hash-pinned pilot100_inputs.py addition. Rejects changed/missing/unreviewed files; retains original scope/science/build/bridge/path checks. No global monkeypatch or old-manifest rewrite. |
| scripts/corrected_canary_evidence_v2.py | registry23,components73,large loader101,large validator127 | Separate corrected evidence reader through compatible plan loading, preserving native-stage/source/Q4/fixed-energy readback. Uses original immutable artifacts and stage validators. |
| scripts/ecp21_inputs_v1.py | count16,inputs45 | Exact21 source-hash allowlist, pinned successful references, atom/core/spin/representation checks; preserves all embedded blocks across six no-SCF inputs. Ordinary inputs delegate to old logic. Does not enable arbitrary embedded ECPs or override existing accepted Y pair. |
| scripts/generate_training_features_v3.py | hashes30,freeze59,load116,release152,run198 | New generation path uses explicit compatibility and ECP input helpers; pins full-training source metadata, preserves native validation/tolerances, requires explicit ECP gateway release authority. No implicit eight-job proposal. |
| slurm/run_full_training_features_v3.sh | whole launcher | Requires explicit frozen plan/release; array0-0 placeholder without percent throttle. Reviewed submission must override array/resource class/route; never submit placeholder as full cohort. Modules/native resources preserved. |
| scripts/freeze_generation_compat_v1.py | main20 | Hash-only preparation of compatibility contract and nonexecuting selection/release drafts. Does not import/run new validators or tests. |
| tests/test_generation_compat_v1.py | whole file |7 cases for exact additive acceptance, changed/missing/unknown dependency refusal and no historical override. |
| tests/test_ecp21_inputs_v1.py | whole file |24 cases: all21 preserved input sets and wrong source/core/spin rejection. No native calculations. |

Paths above are relative to `revwb97m2`. All are NEW files; historical tracked
source/config/driver files are unchanged. This fixes compatibility through a new
explicit reader; intentionally does not make old glob-based validators silently
accept additions. Old APIs still reject the expanded glob; new pipeline will be
validated after commit. Prior197-test pass predates these31 new cases.

## Prepared manifests and remaining work

Hash-only freeze produced under `revwb97m2/manifests/generation_compat_v1`:
`contract.json`, `full_training_selection_draft.json`, `release_draft.json`.
Confirmed unchanged historical hashes and exactly one added top-level module.
git diff --check passes; no new tests or native checks run.

Full2799 species partition:224 accepted pilot species +6 additional canary reuse
candidates +2548 ordinary candidates +21 ECP gateway candidates. Ordinary group
counts by existing requested memory:

| GiB | Candidates |
| --- | --- |
|14|1916|
|21|286|
|35|182|
|62|106|
|117|28|
|227|23|
|557|7|

These are frozen SELECTION drafts, not native execution plans. Six canaries are
held for raw revalidation instead of blind regeneration. Source orbital tree
hashing, reuse acceptance, full copy/storage headroom and current resource review
remain before exact execution manifests.21 ECP cases are14GiB/8CPU candidates;
propose their126-stage bounded gateway array after tests/release review. No
arbitrary spin/core extrapolation or unrestricted full-ECP production release.

## Next gate

STOP for user pre-test commit (explicit scoped commands supplied). After commit:

1. Run31 new tests and full suite, shell/frozen contract checks.
2. Revalidate all seven corrected canaries through the new reader and confirm
   unchanged vectors/fixed/grid values; recheck pilot matrix authority. Test
   rejected dependency changes, not just acceptance of the known addition.
3. Freeze exact ECP gateway and ordinary generation manifests with original
   orbital-tree hashes, unchanged resources and accurate copy/storage estimates;
   preserve namespace separation and all older evidence.
4. Provide execution-manifest commit commands; live partition/account/QOS and
   resource review before approved submissions. No lr_lowprio, no artificial
   eight-running cap. Further large-case resources remain explicit review items.

No release or new calculation is authorized merely by these draft files. Full
1498 numerical matrix/preflight and pre-bulk fitting gates remain downstream.
