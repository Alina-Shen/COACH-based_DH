# Corrected fixed-energy parser checkpoint submitted

## Queue move following user request

Moved pending job25702574 in place from mhg to **cm1**, accountlr_qchem,
QOScondo_qchem. Held it temporarily, updated the scheduler route, verified2CPU/
14GiB/1h unchanged, then released. Last check:PENDING oncm1, reason(None).
No duplicate submission, cancellation, scratch cleanup or frozen-file edits.
The same job ID and log/output paths apply. Both lr8 andcm1 had enough physical
memory; cm1 had twoidle241732MiB/48CPU nodes versus oneidle lr8 node at review.
Idle-node counts do not guarantee immediate start. The on-disk launcher/contract
retain historicalmhg defaults to preserve their hashes; the actual job route is
the explicit scheduler override above. Partition skill used with manual queries.

## Original submission

Submitted job **25702574**, `r2_fixed_checkpoint`, under the user's explicit
approval. Last scheduler check: PENDING, not yet running; no output files yet.
Do not mistake test-only planner job number25702552 for a submitted job.

Resources: mhg/accountmhg/QOSnormal,2CPU,14GiB,1h cap. Direct partition review
confirmed physical capacity/association; no duplicate checkpoint job at submission.
Partition helper missing, manual workflow used. One hour is not an ETA.

New files:

- `scripts/fixed_energy_checkpoint.py`: isolated corrected parser preferring
  final Nuclear Repu. breakdown, fallback to Nuclear Repulsion only if absent;
  independent five-species raw-stage/Q4/scalar/fixed/source readback twice;
  D4-only1e-12 comparison and unchanged2e-8HF identity check; separate candidate
  feature/fixed/grid artifacts with hashes and checkpoint completion marker.
- `tests/test_fixed_energy_checkpoint.py`:five cases for both spelling orders,
  repeated breakdown lines, fallback and missing-data rejection.
- `slurm/run_fixed_energy_checkpoint_v1.sh`: verifies frozen contract, runs full
  regression suite, then audits retained canary outputs; does not run Q-Chem.
- `manifests/production_generator/fixed_energy_checkpoint_v1.json`: pins code,
  launcher, all test files and historical canary contract; not production release.

Local fullsuite149 passed7.55s, shell syntax and sbatch test-only passed. Historical
top-level parser/canary plans remain unchanged; this isolated checkpoint is not
yet adoption into production. No SCF/native rerun/rebuild and no large-canary
submissions. No commit performed. Preserve these newly pinned sources while job
is pending/running.

Logs:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/fixed_checkpoint_25702574.out`
and matching `.err`.
Candidate recovery/checkpoint root (created only after audits pass):
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/fixed_energy_checkpoint_25702574`.

Next: inspect scheduler/test outcome, checkpoint.json/artifact hashes and
per-species fixed-energy changes. If all pass, prepare reviewed production
parser/recovery adoption and new frozen large-canary contract; stop for user
commit with explicit command lines before large launches. Do not claim the
checkpoint or dimer recovery passed merely because the job was submitted.
