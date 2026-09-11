# COACH comparison and controlled search diagnostic — pre-execution checkpoint

## Evidence actually inspected

Read local main paper `coach/paper/COACH_2026MHG.pdf` p10 (Methods), p11 (design experiments), SI `coach/paper/SI_COACH_2026MHG.pdf` pp14–17 (objective, sparsity, solver budget, physical/grid constraints). Searched both complete documents for solver/restart/ridge/warm-start terminology. Inspected current local optimizer.py, constants, scientific_spec and revised mio.py; these local implementation files are not proof of the exact historical executable used for every paper run.

PDF extraction tools were absent. Installed pypdf6.18.1 with --no-deps into temporary `/tmp/coach-paper-parser.WIxe6X`, NOT into dh or coach environments. Temporary PDF extraction scripts are under /tmp; original PDFs unchanged. No third-party upload of papers.

## Differences and plausible effects

| Aspect | Paper / local COACH implementation | Our current implementation | What it could explain |
|---|---|---|---|
| Objective representation | Main p10 Eq5–6/SI p14 Eq50 state half weighted SSE. Local optimizer.py113–137 expands Q=X.T X+1e-10I with linear/constant terms. | Explicit1498 weighted-residual variables and full SSE+1e-10 norm². | Algebraically same ridge normalization (ours twice COACH's entire objective), but different variable counts, conditioning, presolve and algorithms. Expanded normal equations can also worsen conditioning; not presumed superior. |
| Sparsity encoding | Paper/SI Eq52 uses big-M and at-most s. Local optimizer.py140–143 uses SOS1(beta,iszero) for first288 variables and an equality on289 exclusion flags. | Big-M ±25z for all292 columns, sum z≤K, four mandatory scalars. | Different relaxations/branching/heuristics. Final COACH scalar flag is unlinked in local code; do NOT copy that counting peculiarity or describe encodings as identical. |
| Starting support | Local optimizer.py29 seed has indices0,1,96,192,288: semilocal exchange terms, same/opposite-spin correlation and SRHF. | Previous incumbent has only4 scalars, with UEG forcing SRHF1. | Search starts in a very different region. COACH-informed semilocal support is a concrete alternative to test, not evidence scalar-only start is infeasible. |
| Extra energy terms | SI p14:289 linear coefficients, base omegaB97X-V. |292 coefficients with independent VV10/PT2/D4-ATM; fixed omegaB97M-V orbitals. | More competing/correlated columns can affect search/conditioning. No measured causal link established. Approved scientific differences retained. |
| Physical constraints | SI p16 mesh constraints; local code exchange/one-electron/correlation bounds. | Reduced approved C0 set. | Different feasible geometry and relaxation strength. Fewer constraints need not mean easier MIO. Do not reintroduce removed constraints without scientific approval. |
| Size/start diversity | SI pp15–16:s24–80,16cores,1–2h/size,one restart. Local repeats loop perturbs starting vectors. | Stagnant run K14,one optimized scalar start,7200s,16cores. | We have not replicated COACH's size/start diversity. Two-hour run rules out simply blaming all symptoms on a ten-minute budget, not that more time could ever help. |
| Grid pass | SI pp16–17:first unconstrained, then top100 candidate deviations+200 row norms,0.015kcal/mol. | Same approved selective grid workflow, current K14 diagnostic unconstrained. | Not a reason the unconstrained search must stagnate; grid/restart gates remain after search diagnosis. |

The SI restates1–2h per s and one restart; it does not resolve whether the historical stated budget includes that restart, nor give exact parameter/version traces. The equations inspected do not explicitly show the small ridge or SOS1 form seen in code. No unsupported claim that paper guarantees convergence/small gaps.

## Implemented controlled diagnostic

New independent `scripts/search_diagnostic_v1.py`; prior code/plans/artifacts unchanged. Same full1498 matrix, ridge, physical constraints,bounds,K14 and audit thresholds. Every solve capped600s,16threads,32GiB,one3h Slurm job. Seven cases (maximum70solver-minutes plus setup):

1. `qp_dual`: full continuous relaxation,Method1.
2. `qp_barrier`: same relaxation,Method2,BarConvTol1e-12.
3. `root_auto`: original MIO with the audited scalar start,NodeLimit1.
4. `root_barrier`: same root-limited MIO,Method2/NodeMethod2/BarConvTol1e-12. NodeLimit1 is a root-focused bounded diagnostic, not proof only the root is processed with parallel workers.
5. `fixed_coach8`: continuous fit on exactly allowed columns `[0,1,96,192,288,289,290,291]`, i.e.exchange_w0_u0,exchange_w0_u1,same_spin_w0_u0,opposite_spin_w0_u0 and four mandatory scalars. Based on the explicit COACH built-in seed SUPPORT, not its fitted coefficients. UEG and scalar bounds retained. Eight allowed terms ≤K14. In exact arithmetic this support contains the feasible scalar-only point, so its best objective cannot be worse; actual output still audited.
6. `semilocal_auto`: sameK14 MIO,600s,from fixed_coach8 only if independently valid with genuinely nonzero semilocal coefficients.
7. `semilocal_barrier`: same start/budget withMethod2/NodeMethod2/BarConvTol1e-12.

If no valid semilocal start exists, dependent cases6–7 are explicitly skipped—not supplied a fractional/invalid/rounded substitute. Fixed-support candidate is never called the final functional and never auto-promoted to production. Changes in improvement between6 and7 compare algorithm settings with the SAME start; comparison with old run also changes start and wall time and must not be called a time-only experiment.

Capture effective Method/NodeMethod/presolve/PreQLinearize/MIQCPMethod and tolerance settings, sanitized algorithm/presolve/root/warning messages, numeric progress, model exports, coefficients/selections/residuals, quality metrics and independent continuous/discrete audits. WLS environment starts quietly; no license credentials logged. Reports distinguish NodeLimit/TimeLimit from optimality.

Official [Method/NodeMethod documentation](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html) requires compatible barrier node settings for MIQP. Automatic choice is not evidence of the actual internal algorithm. These parameter experiments are diagnostics, not a guaranteed repair. Expanded-objective/SOS1 reimplementation remains a later possible experiment if this narrower comparison fails; not silently added to production now.

## Files, validation and next handoff

- `scripts/search_diagnostic_v1.py`:release/commit/hash gates; controlled models; auditable sparse start; bounded execution/logging/publication.
- `scripts/freeze_search_diagnostic_v1.py`:hash-only manifest and disabled release.
- `tests/test_search_diagnostic_v1.py`:14 prepared offline cases for seven configs, support choice, valid start import, invalid start rejection and disabled release.
- `slurm/run_search_diagnostic_v1.sh`:16CPU/32GiB/3h placeholder cm1 route, to be live-reviewed before submission.
- `manifests/search_diagnostic_v1/{plan.json,release_draft.json}`:frozen scope and hashes; release disabled.

Hash-only freeze and bash syntax check completed. New tests/solves NOT run before user commit. No jobs submitted or production science changed. After commit: full tests, actual-data support witness/parameter preflight, live partition/resource review, tested release and submission; validate resulting objective/bounds/start, then decide existing K80/grid/restart gates. Keep previous untracked operational reports. No external Gurobi support message sent.
