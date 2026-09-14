# Expanded WLS entitlement: bounded validation and scheduling override

User reports a new maximum of 20 concurrent WLS sessions and authorizes testing
and greater parallelism for pending revwb97m(2) jobs only. Running jobs and all
other projects, especially coach_mp2, are out of scope for mutation.

## Probe

`probe.py` starts three independent processes/environments with explicit WLS
credentials read privately from the existing license file. A barrier ensures
all three environments/models coexist, each solves a 300-variable quadratic
known-optimum problem, and a second barrier plus 15-second hold proves overlap.
No license values or raw exception messages are emitted. Models/environments
are disposed explicitly. The test sets five-minute token duration, then waits
330 seconds after disposal before permitting the scheduling override.

Job **25883613**, lr7 / lr_mhg2 / condo_mhg_lr7, n0150.lr7, 3 CPUs, 4GiB,
12-minute limit. Three solves passed with objective zero and 15.0214 seconds
overlap. The existing two discovery fits were also running. This demonstrates
more than two sessions; it is not a 20-session saturation test or independent
verification of the dashboard entitlement.

Gurobi documents that WLS tokens may remain occupied until both environment
closure and token expiry: [official guidance](https://support.gurobi.com/hc/en-us/articles/34567582787345-How-do-I-resolve-the-error-Too-many-sessions).

## Scheduling decision

Initial target is **10 running fits**, not 20. This gives a fivefold higher
dispatch ceiling while reserving headroom for retiring tokens within the
reported 20-session entitlement. An array throttle counts running jobs, not
license-dashboard tokens; it is not a strict token accounting mechanism. Rapid
repeated short failures or other license consumers could still exhaust that
headroom. Do not assume this reserves capacity for unrelated projects.

`raise_throttles.py` is a scheduler-only override for exactly two arrays:

| Array | Before | Initial target | Scope |
| --- | ---: | ---: | --- |
| 25801134 | 2 | 10 | Pending discovery dispatch; existing running tasks unchanged |
| 25802824 | 2 | 10 | Future selected-grid dispatch, only after its existing dependency succeeds |

The two phases cannot overlap under their existing dependencies. Build job
25802822 and grid job 25802823 remain unchanged. The script requires successful
probe/cooldown output and completed accounting before applying either update;
it checks array names, original routing, 16 CPUs, 32GiB, 2h30m and dependencies.
No job cancellation/resubmission, solver edits or manifest changes are needed.
Original frozen scripts still contain historical %2; this documented live
scheduler override supersedes it only for these two existing arrays.

## Partition review and remaining limitation

The partition helper script was unavailable, so live sinfo/sacctmgr/scontrol
and scheduler test-only requests were used. Eligible non-low-priority routes:
cm1/lr_qchem/condo_qchem, mhg/mhg/normal, lr8/lr_mhg2/mhg2_lr8_normal and
lr7/lr_mhg2/condo_mhg_lr7. All can physically accommodate the probe's 4GiB;
the original fits require 32GiB and 16 CPUs. Queue estimates favored lr7 for
the probe; cm1 was later, mhg/lr8 predictions much later. Availability snapshots
are not guaranteed start times. No *_lowprio QOS was used.

**Directly moving existing fitting jobs is unsafe:**
`revwb97m2/scripts/full1498_mio_v1.py:88` compares actual partition/account/QOS
against the frozen release, which specifies cm1. Runtime source/release hashes
and later readers also enforce provenance. lr7 is not even in the old fitting
route allow-list. Changing Slurm routing alone would fail before optimization.
Therefore retain cm1 for these pending jobs; more eligible parallelism does
not promise ten immediate running jobs when that partition is occupied.

Next recommended work: a separately versioned, tested multi-partition launch
and provenance scheme plus token-aware admission/cooldown, then migrate only
pending tasks while preserving complete discovery/grid/selected dependencies.
Do not patch frozen releases, spoof scheduler environment variables, change
running code, or cancel existing dependency parents to force routing.

## New files and follow-up

### Applied outcome

Probe 25883613 COMPLETED 0:0 in 5m52s (including token cooldown), batch MaxRSS
118432 KiB. At 2026-09-13 23:48 PDT the guarded override succeeded: both array
throttles changed from 2 to 10. Before/after verification confirmed identical
commands, routing, CPU/memory/time requests and dependencies. Initial pending
counts were 86 discovery tasks (38..123), 414 selected tasks and two dependency
jobs. No cancellation, resubmission or pending route change was made. Running
discovery tasks 36/37 and coach_mp2 job 25837199 were not modified.

Python syntax, shell syntax and scheduler-field parsing checks passed. The
script dry run validated both exact targets before mutation. All pre-existing
tracked revwb97m2 files remain unchanged; the only code additions are here.

- probe.py: safe synchronized license test and cooldown.
- probe.sh: isolated compute submission with reviewed route/resources.
- raise_throttles.py: narrow guarded live scheduling update and verification.
- README.md: experiment, rationale, limitations and next gate.

After adjustment inspect pending reasons, fresh Gurobi logs and eventual
results. Scientific settings, saved results and all other project jobs must
remain unchanged.

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/wls20_v1
git diff --cached --check
git diff --cached --stat
git commit -m "Validate expanded WLS access and add guarded campaign throttle override"
```
