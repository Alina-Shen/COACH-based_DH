# Longer SCIP comparison — 2026-09-13

User committed the isolated alternative at `5aed899` and authorized the next
recommended experiment. All previously tracked revwb97m2 files remain unchanged
against that commit. Only this report and `run_long_comparison.sh` were added.

## Execution

Array **25858089**, cm1 / lr_qchem / condo_qchem, three independent tasks:

| Task | Reference / start | Solve limit | Question |
| --- | --- | --- | --- |
| 25858089_0 | discovery14 / original simple | 7200 s | Can independent SCIP search approach the saved K14 fit? |
| 25858089_1 | discovery14 / saved Gurobi incumbent | 7200 s | Can longer SCIP continuation improve the saved fit or bound? |
| 25858089_2 | selected80 / saved Gurobi incumbent, 349 rows | 600 s | Does longer selected-grid optimization retain feasibility and improve? |

Each requests one CPU, 8 GiB, 2h20m scheduler limit; all three were RUNNING on
n0003.cm1 at 13:09 PDT. Gurobi remains on n0001.cm1, explicitly excluded.
No lr_lowprio partition, WLS session, new Gurobi solve or existing-job mutation.
Expected duration after start: approximately 2h plus validation for K14 and
10m plus validation for K80, bounded by the scheduler limit.

Nine unit tests passed again before submission (0.22 s); bash syntax and Slurm
test-only submission passed. The wrapper repeats tests per task, records Git
HEAD and code hashes, runs the unchanged committed SCIP runner and independent
readback, and exits nonzero for a scientifically rejected result. Outputs are
separate and existing output directories cannot be overwritten.

Data root:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/scip_alternative_v1/long_25858089/`.
Logs:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/scip_long_25858089_<task>.out` / `.err`.

## Interpretation and follow-up

Time limits match saved Gurobi references, but one-CPU SCIP is not matched to
the Gurobi hardware/thread allocation. Warm-start tests do not measure cold
discovery performance. The unchanged runner's generic comparison caveat still
says 'short SCIP test versus saved longer Gurobi run'; for this experiment
that phrase is superseded by the actual matched time limits above and the
numeric runtimes in each result. No solver mathematics/settings were changed.

After completion, require terminal accounting, result.json passed=true,
publication/source-hash validation and independent scientific/objective audits.
Compare objectives, bound/gap progress, nodes and grid diagnostics against
the 60-second SCIP baseline and saved Gurobi results. A feasible time-limit
result is not an optimality certificate. Do not switch the production campaign
based solely on successful execution. No final results claimed at submission.

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/scip_alternative_v1/run_long_comparison.sh revwb97m2/scip_alternative_v1/LONG_COMPARISON.md
git diff --cached --check
git diff --cached --stat
git commit -m "Add longer isolated SCIP comparison jobs"
```
