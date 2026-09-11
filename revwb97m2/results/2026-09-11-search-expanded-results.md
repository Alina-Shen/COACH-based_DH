# Search/expanded results: progress with expanded objective and big-M

## Independent review

Verified both releases/commits,plan identity,publication digests,all listed artifact hashes,result-summary identity,recomputed acceptance/objectives/integrality and gaps using actual full1498 matrix. Saved readback in `2026-09-11-search-expanded-independent-review.json`. No source/config edits or jobs this turn; temporary read-only `/tmp/audit-search-expanded-results.py` produced audit report. QP 'selected' count in that raw report counts z>.5 only and is NOT a discrete support: QP points remain fractional and are not MIO candidates.

25787336 SlurmFAILED1:0 in4m52s,~456MiB RSS,not resource failure:QP dual endedNUMERIC,status12,no solution; fixed_coach8 failed acceptance,so two dependent semilocal-start searches were correctly skipped. No callback errors. Other independent cases completed and remain informative.

25787337 SlurmCOMPLETED0:0 in20m25s,~2.24GiB RSS;all three case audits pass. Both MIOs reached600s time limit;expandedQP0.240s. Neither indicates global optimality.

| Case | Objective (direct fullSSE+ridge) | Outcome |
|---|---|---|
| Residual QP dual | none | NUMERIC after19.94s |
| Residual QP barrier |1.12729476992601|OPTIMAL0.96s,accepted fractional reference |
| Root automatic |4.42974314117410|228s/node limit1,scalar start unchanged,bound3e-26,gap100% |
| Root barrier |4.19158151222244|8.42s/node limit1,3nonzero semilocal terms,bound1.17566411,gap71.95% |
| Fixed COACH-informed8 |2.74116223962481|SolverOPTIMAL but rejected:UEG1.206e-9 >1e-10,residual1.336e-9 >1e-9 |
| Residual MIO control |4.42974314117410|600s,49nodes,one unchanged start,gap100% |
| Expanded QP |1.12729476992599|Accepted;solver objective differs by5.22e-8,within existing objective-comparison tolerance |
| Expanded MIO |1.90788533019947|600s,1,834,287nodes,10solutions,14selected terms/10nonzero semilocal terms,bound1.58973907917,gap16.6753% |

Expanded MIO improved objective~56.93% from the SAME four-scalar start under same big-M,bounds,weights,ridge,K14,time cap and defaultMIO parameters as residual control. Objective solver/direct discrepancy~6e-14. This demonstrates useful sparse fitting without SOS1 or a special semilocal seed. The standalone QPs agree in direct objective to~2e-14,which supports algebraic consistency. Keep direct-residual audits:expanded form can have cancellation (visible in QP's5.22e-8 reported objective discrepancy).

## What this explains (and does not)

The automatic residual root log explicitly says `Root relaxation: numerical trouble` and warns a variable was dropped from basis. Barrier root log reports objective1.127296 after~0.90s and quickly finds improvement. This is direct evidence of numerical difficulty in this residual/simplex path,not merely a hypothesis that10minutes was too short. Expanded representation performs much better on this tested full-data model. We have not isolated every internal presolve/conditioning mechanism or proved a Gurobi defect; default root paths and standalone QP behavior need not coincide. More time alone did not solve the earlier residual problem.

The COACH-informed starting-support attempt did not produce an accepted start,so its two dependent MIO experiments were NOT performed. Do not claim that a COACH seed solved the issue. Its independent scientific purpose is partly superseded by the valid expandedMIO semilocal candidate; repairing it may remain optional rather than another mandatory gate.

## Why this is not the final functional

New expandedMIO candidate was fitted WITHOUT grid constraints. Independent maximum energy differences:

-99590 vs250974:0.1449649521kcal/mol (~9.66x0.015 target).
-75302 vs250974:2.0143902512kcal/mol (additional monitored grid).

The approved selective99590 grid-constrained second pass is therefore genuinely needed.75302 remains a monitored audit;do not silently add it as a new training constraint. Some coefficients/scalars lie at allowed boundaries (one semilocal=-25,SRHF0,VV10near1),which warrants planned factor-domain/grid checks,not ad hoc bound changes. This is one useful unconstrained training candidate,not evidence of transferability/optimality/final selection.

## Recommended next (requires approval)

1. Adopt expanded quadratic **as the preferred implementation for the next validation stage**, retain big-M and SOS1deferred. Version the representation change in config/adapter with samefullSSE/ridge/scientific feasible set. Preserve independent direct-residual objective/constraint audits and original exports. No automatic production switch this turn.
2. Use the validated expandedMIO candidate as one warm start. Complete the existing bounded full1498 workflow:K14/K80 coverage,repeated-start/restart handling,and COACH-style selected99590 grid second pass. Recompute/reaudit warm-start residuals where needed. The unconstrained candidate need not be feasible for the added grid rows;let the solver repair it and validate accepted output,do not relabel it grid-feasible.
3. Initially retain a bounded validation budget (e.g.the existing600s envelope);after workflow checks,freeze reviewed production scan/resources and use already specified7200s per solve. Gap16.68% is informative,not a requirement to reach zero. Avoid a new generic diagnostic ladder now that a working formulation exists.
4. Optional/deferred:fixed_coach8 numerical repair, deeper residual/simplex/Gurobi support investigation,SOS1comparison. None should block the next expanded-bigM grid/restart validation merely for completeness.

Success for next stage:valid nontrivial candidate,consistent direct objective and restart/provenance readback,selected-grid constraints pass,larger-support path works,and gaps/runtime recorded. No new chemistry generation required.
