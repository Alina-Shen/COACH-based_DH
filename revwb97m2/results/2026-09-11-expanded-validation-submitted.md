# Expanded validation release and submission

- Tested commit: `5d096e1ae888d791a14ce50ef729adebaa391a92`.
- Full suite: 350 passed in 16.66 s.
- Compute construction preflight: 25790945 COMPLETED 0:0 in 20 s; real source/hash/data, WLS, K14/K80 grid model and start assignment passed. No optimization in this preflight.
- Source direct objective 1.9078853301994663; expanded evaluation 1.9078853301996332, within existing tolerances.
- Reports: `2026-09-11-expanded-validation-tests.json` and `2026-09-11-expanded-validation-preflight.json` in this directory.
- Enabled release: `revwb97m2/manifests/expanded_validation_v1/release_20260911.json`.
- Solver job **25790995**, cm1/lr_qchem/condo_qchem, 16 CPUs/32 GiB/90 minutes. Live review found five idle cm1 nodes, empty user queue, adequate storage; no low-priority route.
- Six serial 600-second stages: discovery14, discovery80, constrained14, restart14, constrained80, restart80. About one hour solver budget plus initialization/readback, capped by 90-minute allocation; earlier gate failure can stop execution.
- Normal startup confirmed: discovery14 incumbent 1.9078853301994059, bound 1.5215136050583302, 413728 nodes at 157.44 solver seconds; stderr empty.
- No implementation source changes. Operational reports and release added only.

Next: independent completed-artifact readback, objective and grid feasibility checks, K80 and restart comparison. Full99590 advancement remains mandatory; 75302 monitoring only. Source candidate is not grid-feasible. Big-M retained, SOS1 deferred, production scan not yet authorized.
