# Separate SCIP alternative, v1

This is an additive backend and bounded comparison runner, not a replacement of
the running Gurobi campaign. No existing revwb97m2 source, specification,
manifest, environment or job is modified. Existing readers are imported only
for data loading and independent scientific validation. A runtime import guard
blocks gurobipy. No new Gurobi solve is performed.

## Model and scope

`backend.build` supports the full 292-column matrix, arbitrary valid K and an
explicit selected-grid row list. It retains weighted SSE plus the approved
ridge, big-M=25 links, mandatory HF/VV10/PT2/D4-ATM selections, scalar bounds,
support budget, UEG equality and selected-grid constraints/internal margin.
K counts all selected coefficients, including the four mandatory scalars.
No SOS1 reformulation or scientific-tolerance relaxation is introduced.

The expanded objective is beta'Q beta - 2 l'beta + c. Because PySCIPOpt accepts
linear objectives, this backend minimizes t subject to that quadratic <= t.
There are 585 variables (292 binary) and 591 + twice the selected-row count
constraints. The additional variable/constraint implements the objective, not
an additional physical restriction. See the [official expression tutorial](https://pyscipopt.readthedocs.io/en/stable/tutorials/expressions.html).

The generic backend is available independently of the CLI. The CLI deliberately
limits comparisons to two frozen, previously validated saved references; it is
not yet a 69-size production campaign scheduler or a replacement for the
discovery/row-selection/selected-grid/restart orchestration.

## Environment and settings

Use the existing installation (neither environment is changed):

```bash
SCIP_PYTHON=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/environments/scip_pilot_v1/bin/python
```

SCIP 10.0.2, PySCIPOpt 6.2.1, SoPlex 8.0.2. `runtime.py` appends the existing
dh Python 3.11 site-packages for missing YAML/readback/test dependencies, after
the SCIP environment's own packages. Bytecode and pytest cache writes are
disabled in the wrapper. No Gurobi license is read or session created.

Backend defaults: 7200 seconds, 32768 MiB solver memory, thread ceiling 16,
relative gap 1e-4, absolute gap 1e-10, SCIP feasibility tolerance 1e-9 and the
existing scientific-spec seed. Ordinary `optimize()` is not a guarantee of
16-thread parallel solving. The independent existing scientific audit remains
unchanged, including its stricter UEG test.

Pilot overrides: 60 seconds/solve, one thread, 8192 MiB. The 20-minute Slurm
allocation also covers source checks, model construction and readback. It
excludes the node hosting the Gurobi fits at submission. Review live resources
before reusing the wrapper; this exclusion is a snapshot, not a dynamic rule.

## Tests and comparison

`tests.py` checks expanded/residual objective equivalence, model dimensions and
bounds, a known optimum with all 292 columns, invalid row lists, gap accounting
and blocked Gurobi imports (nine tests).

`run_pilot.sh` runs those tests then three serial real-data checks:

| Case | Start | Purpose |
| --- | --- | --- |
| discovery14_original | Saved original simple seed | Exercise independent SCIP optimization |
| discovery14_incumbent | Saved Gurobi K14 coefficients | Check incumbent import and continuation |
| selected80_incumbent | Saved constrained K80 coefficients, 349 rows | Check selected-grid enforcement and continuation |

Saved sources are `production_multistart_v1/coach_noisy56_20260911/p1_k14_simple_r0`
and `selective_recovery_v1/25792248/constrained80`, under the existing fitting
data root. The runner validates and hashes them before use and checks their
hashes again afterward. It does not write to those directories.

Outputs are exclusively new directories beneath
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/scip_alternative_v1/`.
Existing output directories are refused. Each case saves starts, coefficients,
selection, rows, model CIP, SCIP log, model parameters, independent audit,
saved-Gurobi comparison, source hashes and hashed publication receipts.

```bash
"$SCIP_PYTHON" -B -m revwb97m2.scip_alternative_v1.runner validate \
  --output /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/scip_alternative_v1/JOB_ID/discovery14_original
```

`result.json:passed` is the scientific/objective acceptance gate. A process
exit of zero means diagnostics were produced successfully, not that every
candidate passed that gate. No-solution or scientifically invalid candidates
are retained as diagnostics, never silently approved for production.

SCIP's native gap and a common |primal-dual|/|primal| value are both recorded;
native solver gaps must not be equated without checking definitions. Short
SCIP runs versus longer saved Gurobi runs do not establish relative speed.
Incumbent-start tests are not independent discovery-performance comparisons.

## Next gate

Review real-data acceptance first. Then agree on a larger bounded SCIP pilot
and fair comparison budget using saved Gurobi data. Production migration,
multi-start scheduling and grid-pool publication remain separate future work;
the existing Gurobi campaign must continue unchanged.
