# Reader fix verified; solver-gap interpretation and production handoff

## Implementation and evidence

New `revwb97m2/selective_readback_v2.py` is a read-only versioned reader. Report floats use math.isclose with rtol1e-12,atol1e-15;types,keys,IDs,counts,booleans remain exact. Hashes/start arrays/selection/rows remain exact. Scientific feasibility is freshly recomputed and required BEFORE summary comparison,with existing thresholds unchanged. Existing frozen v1 implementation and historical run artifacts are untouched. v2 compares nested start/candidate/gap/final reports and checks files remain unchanged during readback;it does not optimize or access WLS.

New `revwb97m2/tests/test_selective_readback_v2.py`:14regression cases cover observed last-bit ridge difference,meaningful numeric differences,nonfinite values,type/structure/identity/decision mismatches and selected-grid infeasibility rejection. Initial full-suite attempt383passed/1failed due duplicate exclusive creation of a temporary test fixture;removed redundant fixture write. Final FULL SUITE384passed in16.08s. git diff --check passes.

Existing25792248 successfully re-read with v2:constrained80/restart80 PASS. All hashes,source imports,349row identities,parameters,coefficient constraints,objectives,gaps and selected-grid checks verified. Artifact unchanged checks pass. Full99590violations9/11 remain reported,not relabelled feasible. Evidence `2026-09-11-selective-readback-v2.json` records new reader SHA and policy tolerances. No new solver jobs,orbital work or scientific changes.

## Solver gap explained

For minimization,U is the incumbent objective (best feasible candidate found),L is solver lower bound. Subject to valid solver numerics,the unknown optimum is betweenL andU. Gurobi relative gap=abs(U-L)/abs(U). Restart80 U=0.6142645146012455,L=0.4397736612074823;gap28.4064681%,absolute gap0.1744908533937632. This measures remaining uncertainty in optimality,not percentage error in coefficients/chemical predictions,not probability of correctness,and not a promise of28.4%improvement with more time. Current candidate could already be optimal with a weak bound. Gap can shrink through better feasible candidates or stronger bounds alone. Formula/source: https://docs.gurobi.com/projects/optimizer/en/current/reference/attributes/model.html#attrmipgap .

Both fits ended at600seconds,statusTIME_LIMIT;configuredMIPGap1e-4 is a0.01%target,not achieved. Finite consistent gaps are acceptable for current bounded workflow;global optimality/finalmodel quality not certified. Bound and gap refer only to the specified K80 model/349constraints/weightedSSE+ridge,not unselected grid behavior,other model sizes or transferability.

## Production preparation outline (not released)

Bounded fitting/readback validation is now complete under approved selective policy,combining historical K14 and new K80/restart evidence. No further generic diagnostic fits proposed. Preserve both K80 candidates:restart improvesobjective2.50%but larger unselectedgrid maximum0.05899vs0.03239kcal/mol. User model review retained.

Next prepare exact versioned production expanded/COACH-selective execution plan:K=[14,24,32,40,48,64,80],two solves per K per grid pass,7200s/solve,28solves total (56solver-hours if all time out;896allocatedCPU-hours at16CPU,excluding overhead). Discovery per K can run independently;freeze full declared discovery-candidate union before second-pass selection;selected pass per K and its restart have explicit dependencies. Freeze starting candidate routing,repeat/restart semantics,candidate pool,reader version/config/source hashes,and live resource/concurrency policy before release. These details require actual production implementation/review,not silently extending the600s K80 overlay. Keep no lr_lowprio and<999active-user-task policy. Prepare pre-bulk commit commands and obtain scan/resource release before launching. Approval of selective outlier reporting is not automatic final-candidate approval. This document is preparation,not a production manifest or authorization.
