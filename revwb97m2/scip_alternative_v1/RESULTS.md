# SCIP alternative implementation and bounded tests — 2026-09-13

## Work performed

1. Inspected the existing coach_mp2 SCIP installation, original revwb97m2
   expanded-objective/big-M implementation, scientific audit and saved result
   readers. Reused SCIP 10.0.2 / PySCIPOpt 6.2.1 unchanged.
2. Added `backend.py`: weighted expanded SSE+ridge quadratic epigraph, all 292
   coefficient/selection pairs, mandatory scalars, scalar bounds, K, UEG and
   explicit selected-grid rows. Preserved the existing scientific semantics.
3. Added `runtime.py`: read-only dependency bridge and explicit Gurobi import
   prohibition. Neither dh nor the SCIP environment was modified.
4. Added `runner.py`: load/audit frozen saved Gurobi references; import original
   or fitted starts; solve only with SCIP; save separate artifacts; independently
   validate coefficients/objectives/grid feasibility and hashed readback.
5. Added `tests.py`: nine tests including a known-optimum 292-column model.
   Passed locally (0.45 s) and on the compute node (0.64 s).
6. Added `run_pilot.sh`: serial three-case, 60-second-per-solve compute pilot.
   Reviewed lr8/mhg/cm1 scheduling; cm1 provided an available start on a node
   separate from the Gurobi allocation. Submitted only SCIP job **25857266**:
   cm1 / lr_qchem / condo_qchem, n0003.cm1, 1 CPU, 8 GiB, 20-minute limit;
   n0001.cm1 explicitly excluded. No existing jobs cancelled, changed or rerun.
7. Added `README.md`, this report, package marker and `protected_baseline.json`.
   The aggregate SHA256 of all 996 previously tracked revwb97m2 files is
   unchanged: `f4396a8474da0223b919a57054f46a6b2443bf3add234a272815a17c4b253812`.
   Unrelated coach_mp2 live-log and user spreadsheet changes were preserved.

## Numerical results

Results are under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/scip_alternative_v1/25857266/`.
The runner records independent residual-form objectives rather than trusting
only the solver's epigraph value. Lower is better.

| Full 1498-entry case | Independent SCIP objective (Hartree²) | Saved Gurobi objective | Audit/readback |
| --- | ---: | ---: | --- |
| K14, original simple start | 2.827583148829 | 1.889511627689 | Pass |
| K14, saved incumbent start | 1.889511627688 | 1.889511627689 | Pass |
| K80, saved selected-grid incumbent | 0.630022123770 | 0.630022123775 | Pass |

Job 25857266 completed with exit 0:0 in 3m57s; batch MaxRSS was 694824 KiB
(about 679 MiB). All three solves reached their 60-second time limit with a
scientifically accepted candidate and passed separate artifact readback.
No Gurobi module was imported. All saved reference file hashes were unchanged.

All three dual bounds remained zero: the common primal-normalized gap is
100%. SCIP's log shows Inf (its API returns the finite infinity sentinel
1e20, retained verbatim in `scip_raw_gap`). Thus no optimality certificate or
useful bound improvement was obtained. Nodes processed: 97 for original K14,
129 for incumbent K14 and 1 for selected K80. These observations do not identify
an internal solver cause; longer-time and formulation diagnostics remain open.

The discovery case found ten nonzero semilocal coefficients; discovery does
not constrain grid rows. Its full-grid diagnostic failure does not invalidate
discovery-stage acceptance. The K80 case explicitly enforces the saved 349
selected rows, without changing row-selection policy.

The saved Gurobi references used 7200 seconds (K14) and 600 seconds (K80).
Sixty-second SCIP runs cannot establish a speed ranking. Matching an imported
incumbent is evidence of compatible import/feasibility, not a new discovery or
meaningful improvement. These are feasibility/integration tests, not proofs
of optimality or production migration approval.

## Recommendation

Keep the running Gurobi campaign unchanged. Review the isolated implementation
and commit it. The next useful experiment is a longer SCIP-only comparison
with the same saved starts and selected rows, retaining separate output roots;
compare against existing Gurobi data, never launch new Gurobi reference runs.
Before broad migration, establish useful bounds/search progress and add a
separate reviewed multi-start/row-pool/campaign orchestration layer. This turn
implements the solver and comparison route, not an automatic campaign switch.

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/scip_alternative_v1
git diff --cached --check
git diff --cached --stat
git commit -m "Add isolated SCIP alternative and real-data comparison pilot"
```
