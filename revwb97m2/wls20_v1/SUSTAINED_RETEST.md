# WLS baseline update retest — 2026-09-14

User reports WLM now displays maximum baseline20 and requests a fresh test.
This turn authorizes testing only; no production migration or throttle increase.

## Test design and submission

New files sustained_probe.py and sustained_probe.sh create16 independent
processes, each with its own WLS environment and a300-variable known-optimum
quadratic model. All first solves must succeed before the concurrent360-second
hold; each process then resets and solves again. Explicit model/environment
disposal is followed by330seconds of token-expiry cooldown. Credential values
and raw error messages are never printed; only error type/code and any
recognized numeric active-session/baseline counts are retained.

Six minutes exceeds the requested five-minute token lifespan, but is not a
long-duration campaign test or an independent inspection of the server's
configured baseline. Sixteen test environments plus the two existing fits
target18 concurrent environments, leaving two slots of headroom within the
user-reported entitlement. This is not a full20-session saturation test.

Submitted job25895401:16CPUs,4GiB,20-minute wall limit. Initially on lr8 with
mhg2_lr8_normal; it was blocked by QOSGrpCpuLimit. Reviewed alternative routes
and moved only this pending test to cm1/lr_qchem/condo_qchem, where it started
on n0003.cm1. Updated only the new test wrapper's route fields; no resource
changes and no *_lowprio QOS. Python and shell syntax checks passed.

Artifacts:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/wls20_sustained_25895401.out`
and the matching `.err` file.

## Result

All 16 environments passed both solves (32 successful solves), each with
objective 0.0. Measured simultaneous environment overlap was 360.010516 seconds.
The report has `passed: true`, and stderr remained empty. No baseline-two
rejection was observed. The 330-second disposal cooldown completed, followed by
`PASS sustained WLS retest; cooldown complete`. Slurm reports COMPLETED, exit
0:0, elapsed 00:11:35, batch MaxRSS 315328K, node n0003.cm1.

This establishes working access at the tested concurrency and duration, not
an independently verified server baseline of 20 or a full campaign guarantee.
Recommended next step: complete the corrected compute-node adapter/readback
gate before activating multi-partition production dispatch. No activation was
performed by this retest.

## Scope preservation

Production tasks25801134_47/48 remained running. Discovery and selected array
ceilings remain2; dependencies and other-project jobs are not changed. Existing
uncommitted activation changes found in the worktree are preserved untouched.

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/wls20_v1/sustained_probe.py \
           revwb97m2/wls20_v1/sustained_probe.sh \
           revwb97m2/wls20_v1/SUSTAINED_RETEST.md
git diff --cached --check
git diff --cached --stat
git commit -m "Add sustained multi-session WLS retest"
```
