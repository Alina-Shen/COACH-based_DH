# Continuous K14 diagnostics — September 11, 2026

## Execution and checks

- Verified committed checkpoint `a74b286`; no scientific/source code changes this turn.
- Full suite: 288 tests passed in 15.31 s. Real full1498 matrix identity and both analytic feasibility witnesses passed. See dated JSON test/preflight records.
- Reviewed live cm1/mhg/lr8 capacity, cm1 account/QOS and empty user queue. cm1 had five idle 241732 MiB nodes; 32 GiB fits. Scheduler dry-run passed. No lr_lowprio.
- Created hash-bound `manifests/continuous_k14_v1/release_20260911.json` after gates. Submitted job **25783741**, cm1 / lr_qchem / condo_qchem, n0001.cm1, 16 CPUs, 32 GiB, 90-minute wall limit, 600 s per continuous solve.
- Started 08:44:44 PDT; Slurm FAILED exit1:0 after 27 s, batch MaxRSS181764K (~178 MiB). Both solves completed; rejection was an audit gate, not timeout/OOM. stderr empty; no callback errors.
- Heavy outputs: `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/continuous_k14_v1/25783741`; logs in sibling project `logs/continuous_k14_25783741.{out,err}`.

## Results and independent readback

| Diagnostic | Solver result | Independent numerical checks |
|---|---|---|
| Fixed four scalars | OPTIMAL, 0.066 s, objective4.429743141174115 | All checks pass; UEG error0, max residual identity error1.50e-12 |
| Full K14 continuous relaxation | OPTIMAL, 0.907 s, objective1.1272947778883566 | Reject: UEG error5.608e-10 >1e-10; residual identity error7.214e-8 >1e-9; 55 fractional selections |

Fixed scalar coefficients in SR-HF/VV10/PT2/D4-ATM order: `[1,2.0882753976524575e-8,0.7815442682950514,0.9999999787409273]`.
Compared with previous MIO start objective32.19152576324623, this is about86.24% improvement within the same four-term support. It establishes that the earlier unchanged incumbent was not the optimum even on its selected support. It does not establish the internal cause of MIO stagnation or validate a final functional.

The committed readback validator additionally rejects exact dictionary equality (`solution audit changed`): recomputed SSE/ridge/objective differ only at ~1e-15 from saved values. All Boolean check results reproduce, including the genuine relaxed rejection. This is a distinct readback robustness defect, not grounds to loosen scientific tolerances. No source fix or rerun was performed this turn.

Next recommendation: correct floating-point readback comparison with explicit tight tolerances and regression tests while keeping discrete/check/hash fields exact; separately prepare a numerically improved continuous-relaxation diagnostic without changing scientific acceptance thresholds. Audit/import the fixed-support solution as a future MIO start only through a separately approved checkpoint. No automatic promotion, retry, or bulk release.

## Four-scalar support and search time

Support means selected/allowed feature columns, not training species or entries. Here all288 semilocal columns are disabled; four mandatory scalars multiply short-range HF, VV10, total PT2, and three-body D4-ATM features. With semilocal exchange zero the UEG equality forces SR-HF=1, leaving three adjustable scalars. All1498 training entries remain. K14 counts these four scalars and allows up to10 semilocal terms; the four-scalar diagnostic is not the intended final model.

The current [scientific specification](../configs/scientific_spec.yaml) sets7200 s (2 h) **per solve**,16 threads, two repeats per warm start. The proposed seven-K/two-solve/two-grid-pass scan has28 solves, nominal56 serial solver-hours /896 core-hours at full caps with one start per slot. Additional starts change that count. Queue/setup time is extra; early stopping is possible; the cap does not guarantee a small gap. Exact production launch/resources remain unapproved.

COACH's [methodology](../../coach/Optimization.md) describes1–2 h per subset size, depending on size, one restart,16 CPU cores. Its [code](../../coach/2_optimization/coachopt/optimizer.py) and [template](../../coach/2_optimization/templates/run_mio.yaml) default3600 s per solve; the [example](../../coach/example/README.md) uses600 s. These distinguish documented methodology, shipped defaults and demonstration settings; they do not establish every historical paper run's exact settings. Our current600 s cap is diagnostic-only; production specification remains7200 s.
