# Production preparation: COACH cross-check and review gate

Commit reviewed: a61434fa332f1ac5fa4d1a0740062fbcd4412906; initially clean worktree. User explicitly requested no immediate implementation changes if mismatches are found. This is a non-submitting review proposal, not an executable production manifest. No solver/config/source changes.

## Sources inspected

Local COACH is the supplied maintained/cleaned script-first implementation; it is not assumed byte-identical to the scripts used for every historical manuscript experiment.

- `coach/2_optimization/coachopt/optimizer.py`: SIMPLE_WARM_START line29, warm-start pool lines71-93, expanded objective/selection lines112-143, physical/grid constraints lines146-168, nested start/repeat loops lines199-223.
- `coach/2_optimization/coachopt/analysis.py`: all-candidate loader lines25-50; RMSE normalization lines160-168; within-size representative selection lines200-209.
- `coach/2_optimization/coachopt/select_diff_constraints.py` lines29-56; CLI and README; `templates/run_mio.yaml`; `run_mio.py` defaults.
- `coach/paper/COACH_2026MHG.pdf`: pp8 and10; `SI_COACH_2026MHG.pdf`: pp14-17 and24-25 (sections3.2/3.3/3.4/4.2).
- Current scientific_spec v7, selective recovery schedule, validated expanded/selective overlays, previous production outline and STATUS.

## Review-required production mismatches

### 1. Restart semantics

SI p15 says1–2hours per subset size and one restart, but does not specify how to initialize that restart. Local COACH code repeats EACH original warm-start vector; on repeat_index>0 it adds independent Gaussian noise with sigma0.05 to that original vector. It does not take the preceding fitted solution as the second start. Our tested recovery imports preceding fitted coefficients/selection unchanged. These are distinct search protocols; neither should be described as identical to both sources. Current scientific_spec says repeats_per_warm_start=2 while the proposed28-solve plan treated that as an incumbent restart.

Recommendation for review: keep the experimentally validated incumbent-restart approach as an explicit project adaptation, not silently claim original-code repetition. Literal COACH noisy repeats are an alternative. If chosen, they need adapted DH seed handling and regression checks: perturbing coefficients can violate coefficient/scalar/UEG constraints, and our current start validator requires ungridded feasibility. Do not bypass scientific checks by assumption.

### 2. Warm-start pool and total solve count

COACH always retains its built-in simple seed and adds EVERY saved matching-K pass1 vector for pass2. Our proposal uses a bounded candidate/previous-result route,not that full pool. Under7sizes,repeats=2,one initial seed per size and two saved pass1 vectors per size:pass1=7x2=14solves;pass2=7x(1+2)x2=42;total56,not28. At7200s each this is112solver-hours/1792allocatedCPU-hours at16CPU before overhead,vs56solver-hours/896CPU-hours for28. This is conditional arithmetic for these explicit settings,not a claim the historical paper ran56jobs;code default repeats=1 and default time3600.

Recommendation: explicitly choose either the proposed28solve lean incumbent-restart schedule or literal multi-start repetition (56in this example). Exact 292-column DH seed/start routing and preservation of candidates require approval before freeze. A K80 candidate cannot be imported into smaller K without support-compatible selection;acceptedK14 can seed K>=14 after audit. All declared discovery outputs (not just two diagnostic candidates or only final winners) should participate in production grid-row selection.

### 3. Model-size coverage and time

Paper/SI say scan24–80; reviewed passages do not establish exact increment/all integer values. Code requires an explicit list;README example24,32,40,48 and template24,32,40 are examples,not proof of the manuscript full scan. Our approved coarse list14,24,32,40,48,64,80 is not an exact reproduction;14is outside the stated range. Retain current list unless user requests expansion;do not infer57integer sizes. Current7200s at every K is the paper's upper time limit,not proof of its size-dependent1–2hour allocation.600s remains validation-only.

### 4. Ranking metric: original code versus paper

Local analysis code divides each dataset's RMSE by its supplied standard error,then averages these ratios;within each K it picks lowest mean,then median,then label. SI3.4 p17 describes GSCDB137 assessment using MAE for most datasets plus dataset-specific MARE/regularized/weighted metrics. The mean-of-ratios principle is shared;the metric numerator is not universally the same. Our spec says lowest overall mean NER among eligible candidates,with protected-assessment exclusions and deferred tie decisions. Blindly reusing COACH's RMSE helper would not automatically implement those dataset-specific definitions.

Recommendation: preserve existing paper/GSCDB-aware NER policy and protected-role exclusions;report RMSE-based legacy score separately if useful. Freeze exact production ranking implementation before final selection;tie details can remain deferred as already approved,not a new prerequisite for launching search. This does not change weightedSSE+ridge fitting objective.

## Known source inconsistencies / already approved differences

- Paper/SI big-M and sum(z)<=s vs local code SOS1/iszero equality with last HF scalar omitted from SOS links. Our big-M/counting policy deliberately follows the paper and user decision;SOS1 remains deferred. Equality of iszero indicators should not be read as forcing every eligible beta nonzero.
- Our292DHfeatures (PT2 and fitted VV10/ATM coefficients),four mandatory scalar selection slots,fixedwb97m-v orbitals,omega0.3,no orbital refitting and reduced physical constraints are approved scientific differences from the289parameter COACH baseline. No proposal to change them or regenerate features.
- COACH objective0.5SSE+5e-11||beta||² vs ourSSE+1e-10||beta||² are a positive factor2 apart:equivalent minimizers,not a ridge mismatch. We now use expanded form as approved. Relative gaps invariant under this factor;absolute objective/gap units differ.
- Current stricter scientific feasibility tolerances are explicit project settings;COACH optimizer sets time/threads/output but does not explicitly set those tolerances. Do not reset them to library defaults.
- COACH selector implementation uses200FROM REMAINING,while README shorthand says global200union. Our new selector matches executable code;historical helper stays frozen. Our approved full-grid report/review policy agrees with selective SI discussion;not all-entry enforcement.
- Main p8 says(200,974),Methods p10 and SI say(250,974). Keep existing250974reference. Main p8 broad guarantee wording is qualified by SI's default experiment452selected/10remaining violations,609expansion study,then retention of smaller default procedure. Those counts are not universal settings.
- Base scientific_spec still labels representation explicit residual and old grid selection;new overlays implement approved expanded and remaining-row policy. This is preserved historical provenance,not permission to silently overwrite base hashes. Production needs an explicit versioned effective spec binding approved overrides and v2reader,with runtime7200rather than recovery600.
- The paper discusses multiple historical database/cycle versions;our1498training rows and COACH final-cycle weight authority are already approved/validated. No reassembly/weight change proposed in this scan audit. This review is not a new species-level feature audit.

## Non-submitting production outline

Preserve validated matrix/source/feature identities. Once user resolves restart/start-pool choice,freeze exact K-specific starts,per-stage repeats and candidate retention;parallel discovery jobs may run by K,then a barrier for union selection over the declared full discovery pool;parallel selected-pass branches by K with explicit repeat/restart dependencies. Keep expanded objective,big-M,349not hardcoded (production pool changes row count),COACH remaining-row selector,selected-only acceptance,full outlier reporting and versioned v2readback. Review live partitions/memory/concurrency (<999active user tasks,no lr_lowprio) before release. User pre-bulk commit and scan/resource approval remain mandatory.

Review gate: do NOT generate/release an executable production plan or alter current code until user chooses restart/start-pool semantics. No jobs submitted or tests rerun during this source/documentation audit. Detailed bounded evidence remains valid;discovered production-protocol ambiguity is not a reason to repeat the chemical/solver pilots.
