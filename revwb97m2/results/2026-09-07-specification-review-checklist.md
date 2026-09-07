# Specification review: COACH constants, numerical policy and code mapping

LATEST UPDATE: user subsequently retained omega=0.3, so the omega=0.27
change/rebuild/exchange-recomputation requirements below are superseded.
VV10 b=5.5 remains intended. User approved the 0.999 internal grid margin
and final-model user review; ridge choice remains open. Main paper p4 explicitly
states final selection by lowest overall mean error subject to chosen constraints
and stability targets (73 linear parameters); no explicit final near-tie rule.
The prior draft audit below is preserved as history. See the
[latest project decision record](../../../codex_notes/projects/coach-based_dh/2026-09-07.chapters/08-omega-retained-ridge-and-paper-selection.md).

Status: pre-draft decision audit, NOT an executable or frozen v7 specification.
Date: 2026-09-07. No jobs, source implementation changes or rebuild authorized
by this report. Existing v6 is historical validation authority, not the approved
parameter set for a new scientific production fit after this amendment request.

## Approved direction and correction

The user requests final COACH nonlinear values while retaining fixed imported
omegaB97M-V orbitals. Local sources `coach/FunctionalCOACH/COACH.md:15,20,159`,
`coach_pyscf.py:19-23`, and `coach_css.py:21` agree on:

- target-energy omega = 0.27 bohr^-1;
- VV10 b = 5.5, C = 0.01;
- same-spin gamma = 0.01.

The assistant's previous claim that final COACH gamma_ss=0.2 was wrong.
It must not be used to justify changing gamma to 0.2. C and gamma_ss therefore
remain numerically unchanged from v6. The parent archive remains omegaB97M-V,
whose generating method has omega=0.3; target-energy omega=0.27 is a separate
quantity. No SCF regeneration is intended. This is not the published
omegaB97M(2) parameterization; R0 keeps its published constants unchanged.

## Artifact implications

- Native integratedDV source currently hardcodes omega=0.3 at
  `/clusterfs/mhg-data/yaoshen/qchem/trunk/libks/libks/exc_fxc/integrated_dv.C:111`.
  Change/parameterize the target-energy kernel and revalidate against the Python
  reference at 0.27; changing only Q-Chem REM or YAML is insufficient.
- Regenerate short-range semilocal exchange on all three grids and the SR-HF
  feature at 0.27. Regenerate VV10 at b=5.5. Build new versioned vectors/D matrices.
- Recompute fixed energy using E_LR(0.27)=E_full_HF-E_SR(0.27).
  The old fixed-energy total is not reusable unchanged. Validated full-HF,
  one-electron, Coulomb/nuclear and field components can be reuse candidates.
- Same-spin/opposite-spin correlation columns, canonical total PT2 and D4-ATM
  are scientifically unchanged when their inputs/settings match. Reuse requires
  hash and semantic validation, not blanket copying old completion markers.
- Old 38-species/20-entry gateway remains evidence for v6, not complete new-
  parameter readiness. Do not relabel old validations as v7 passes.
- Preserve source archives and all v6 artifacts. Rebuild is future gated work,
  using the user-provided module/configure/make instructions after confirming
  the implementation scope; none performed here.

## Numerical implementation: choices to make explicit

These are how a mathematical model is represented, solved, stopped and checked;
they are not additional physical assumptions unless the objective is changed.

1. Objective representation: current pilot uses explicit residuals
   r_k=sqrt(w_k)(A_k beta-b_k), minimizing sum(r_k^2), no penalty.
   Maintained COACH optimizer instead evaluates half*SSE + 5e-11*||beta||^2
   through X^T X + 1e-10 I. The ridge is tiny but can affect near ties; multiplying
   an objective changes absolute-gap units even when its minimizer is unchanged.
   Recommendation for review: retain explicit-residual unregularized SSE and
   document this deliberate numerical departure, rather than silently inserting
   ridge. User decision needed because 'otherwise COACH protocol' could mean
   retaining the ridge. Objective units are hartree^2; do not rescale without
   correspondingly reviewing absolute gap and saved diagnostics.
2. Explicit solver settings proposed from the pilot baseline: FeasibilityTol
   and IntFeasTol=1e-9; MIPGap=1e-4; MIPGapAbs=1e-10 in objective units; seed=0.
   Current pilot sets the first two and seed, but inherits gap defaults. Freeze
   all values and report version/default snapshot. These are recommendations,
   not proof that tighter tolerances improve conditioning or that the gaps will
   be achieved. Published COACH historic version/defaults are not inferred.
3. Independent audit: retain exchange equality check 1e-10 (stricter than solver
   feasibility), independently recompute objective/support/grid errors; fail
   publication if the audit fails. Review grid safety margin explicitly:
   maintained COACH uses 0.999*0.015; the current pilot uses 0.015 with numerical
   audit slack. Recommend adopting COACH's 0.999 internal margin and checking
   the public 0.015 limit independently, rather than silently accepting an
   above-threshold point as stable. This margin remains a review proposal.
4. Sparsity: current linked binary sum<=K counts four mandatory scalar slots;
   selected does not necessarily mean strictly nonzero (SR-HF includes zero).
   Record selected count and coefficient-magnitude counts separately. Do not
   silently restore the maintained COACH SOS1 bookkeeping or exact slot count.
5. Stop/restart: distinguish feasible TIME_LIMIT from optimal-to-tolerance;
   no-incumbent/infeasible/error cannot publish fitted coefficients. Save every
   incumbent, bound, raw/derived gap, audit, resolved config, seed and start.
   Recommendation: allow audited time-limited candidates in comparison with
   conspicuous uncertified-optimum labels; never require support's answer as a
   blanket fitting gate. Retain raw nonfinite-gap state rather than inventing
   a finite solver value. Meaningful repeat/warm-start schedule still needs a
   documented implementation; identical repeated seeded runs are reproducibility
   checks, not independent search evidence.
6. Proposed existing resources: 16 solver threads, 7200 seconds per solve,
   K=[14,24,32,40,48,64,80], two repeats, two grid passes. Define total launch
   count, concurrency, walltime overhead and resume identities in the execution
   manifest before submission; no total job count inferred from vague repeats.

Gurobi definitions checked against the official
[parameter reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html)
and [numerical guidance](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/numeric_parameters.html).

## Model selection: separate from coefficient fitting

For each K/repeat/pass, Gurobi fits coefficients to the same 1,498 weighted
entries. Model selection compares resulting candidates, including across K;
larger K can improve fitting loss without providing a better final functional.

Use declared GSCDB137 development coverage: 8,377 entries / 13,907 species.
Compute each dataset's prescribed error, divide by its frozen reference scale
to obtain NER, then report category and overall aggregates. This is not a second
training-weight application. Special O24/O24x5 and transition-metal evaluation
weights need explicit metric handling; plain universal RMSE from the maintained
analysis module must not automatically be treated as paper-equivalent. Add
hand-computed tests and freeze the metric mapping and aggregate denominators.

Report AE11/MB08-165/MB16-43 mean NER as a diagnostic, grid behavior, dense-factor
behavior, support, repeat stability and optimality evidence. These development
roles overlap training; they are not an untouched test set. Protect SC74/OEEFD,
BigNC/GDB9/OPT from tuning under the existing policy. COACH-derived fixed D4
damping itself has historical BigNC provenance, so do not claim independence
from all prior COACH development.

Maintained analysis code picks a representative within each K by overall mean
normalized RMSE, then median, then label. It does NOT define a fully automatic
final choice across K. Existing spec lists selection considerations but supplies
no final ordering, tie tolerance, dense-factor pass limits or trade-off rule.
Recommendation for review: produce a complete development comparison and
Pareto/accuracy-versus-size report; user selects final K/model at an explicit
review gate, with rationale recorded before final-assessment evaluation. Do
not invent a composite score or automatic 'one-percent plateau' rule.

## Housekeeping and setting-to-code checklist

Housekeeping means consistency/version/provenance repair, not changing science
under an administrative label. Every intended scientific change still needs a
new version and affected gates.

| Setting or contract | Current consumer/evidence | Required action before new production |
|---|---|---|
| Parent orbital authority | configs/scientific_spec.yaml orbital_source; manifests/qchem_orbitals | Preserve parent omega=0.3 and immutable archives; distinguish target omega |
| Target omega=0.27 | integrated_dv.py:29; native integrated_dv.C:111 | Parameter plumbing, native rebuild, three-grid independent parity |
| gamma_ss=0.01 | integrated_dv.py:31; native .C:208; COACH.md:159; coach_css.py:21 | Correct prior explanation; retain value and pin sources |
| SR-HF/VV10 constants | qchem_scalar_features.py:97-104 | Separate target 0.27 and b=5.5 from parent method; verify emitted REM and parsed values |
| Fixed LR partition | qchem_scalar_features.py:246-271; step14_recovery_v2.py | Reassemble from full HF minus new SR; preserve field correction tests |
| PT2/D4 reuse | qchem_scalar_features.py; scalar/fixed manifests | Verify unchanged inputs/settings; versioned dependency-aware reuse |
| 292 layout / selected rows | configs/scientific_spec.yaml; mio.py feature_names | Schema/shape/hash gates; reject old full-vector reuse as new model |
| Objective / ridge | mio.py:62-65; coachopt/optimizer.py:114-139 | Resolve no-ridge versus COACH ridge; implement approved option explicitly |
| C0 / binary budget | mio.py:49-61 | Load from spec; reject unsupported profiles; round-trip audits |
| Tolerances / gaps / seeds | mio.py:42-48; solver_reporting.py | Explicit resolved settings and independent audit thresholds |
| Grid rows / margin | grid_selection.py; mio.py:66-74 | Preserve two passes; resolve 0.999 margin; >200-row multi-candidate tests |
| Weights / roles | manifests/weights; manifests/data_roles; reaction_assembly.py | Keep final-Cycle-2 entries and weights; assert row order and sqrt weighting |
| Scan / repeats / restarts | scripts/run_step15_pilot.py | Production spec-driven driver and restart/failure-injection tests |
| Paper metrics / final ranking | coach/2_optimization/coachopt/analysis.py; no revised analysis entrypoint | Dataset-specific metric mapping, fixtures and explicit user-selection gate |
| dh environment | environment/DH.md; stale YAML project.runtime_environment | Reference validated dh baseline; preserve coach historical provenance |
| Gate metadata | stale YAML native pending markers; Q3/Q4/Q6 evidence | Distinguish completed v6 tests from pending changed-parameter tests |
| R0 comparator | published_wb97m2 manifests/evaluator | Preserve published constants separately; regression remains historical comparator |
| Source of truth | configs/scientific_spec.yaml; scripts/validate_scientific_spec.py | Archive v6, version candidate only after decisions, remove hardcoded-v6 assumptions |
| Units / paths / hashes | spec; mio.py grid conversion; environment manifests | One conversion constant, valid paths, new artifact identities, old data immutable |

## Decision gate

Not all settings are unambiguous. Do not claim a ready-to-freeze v7 yet.
Recommended next approval: documented final-COACH constants (including corrected
gamma=0.01), explicit-residual no-ridge objective, proposed explicit solver/audit
controls and COACH grid safety margin, and a user-review final model-selection
gate. After the policy decisions, prepare versioned review YAML and implement
the checklist in separately authorized work. Resources remain a submission gate.
