# Expanded full-data validation — approved implementation/pre-test checkpoint

## Implemented changes

User approved progressing with expanded quadratic,big-M and existing K14/K80/grid/restart validation. Added versioned execution overlay `configs/expanded_validation_v1.yaml` rather than editing the hash-frozen base scientific_spec.yaml. The overlay explicitly supersedes only the objective representation for THIS validation stage,retains fullSSE/ridge/big-M and selects bounded600s/16threads. The original v7 spec remains the immutable science/matrix provenance; production default remains unchanged until a separately reviewed production release. This avoids invalidating historical manifests and does not claim v7 itself was edited to expanded form.

`expanded_adapter.py` loads/validates overlay against base spec identity,builds expanded584-variable model with existing bounds/UEG/big-M,adds selected99590 grid inequalities,then audits original weighted residual SSE+ridge directly. Selected rows use approved0.999 internal margin and unchanged public0.015kcal/mol check.75302 is monitored only. Source/start audits enforce integrality/linkage/budget without clipping coefficients or rounding fractional solutions.

`scripts/expanded_validation_v1.py` implements six bounded solves and fresh readback:

| Stage | Budget | Start | Grid constraints |
|---|---:|---|---|
| discovery14 |14|Accepted expandedMIO candidate from25787337|None|
| discovery80 |80|Same accepted K14 source (feasible under larger budget)|None|
| constrained14 |14|discovery14|Frozen union selected from discovery14/discovery80|
| restart14 |14|constrained14|Same frozen rows|
| constrained80 |80|discovery80|Same frozen rows|
| restart80 |80|constrained80|Same frozen rows|

This preserves prior full-data schedule,except discovery now has an audited semilocal start and all stages use expanded representation. Restart here is an explicit new solve from preceding accepted coefficients,not continuation of the old branch tree or an SCF cycle. This checks restart plumbing;it is not a claim of literal COACH perturbed-repeat replication.

Grid row selection reuses existing deterministic top100 deviations/candidate plus200 globalL1 rows. Each constrained stage must pass selected-row feasibility AND existing full1498 99590 advancement gate before downstream execution. If unselected rows still violate,the run stops for review;no automatic enlargement/retry. Starting discovery coefficients may violate newly added rows:that is recorded,not falsely declared feasible;Gurobi may repair/reject that start.

Source handling verifies job25787337 publication/artifact hashes,source release and independent discrete/objective audit. Exports preserve starting coefficients/selections,selected row indices,effective model parameters,MPS,progress,objective,bounds/gaps and audits. Final `validate` performs read-only fresh array/provenance/constraint/restart/grid recomputation without WLS and without rewriting artifacts. No fractional source promotion or grid-feasible claim for the original unconstrained candidate.

## Tests and execution gate

Added12 prepared offline cases:stage dependencies,valid/nonvalid starts,K80budget,selected/unselected grid violations,75302monitor-only,frozen rows across restart,disabled release. Tests are NOT yet run at user pre-test commit gate. Hash-only freeze and shell syntax completed; no optimizer/model-build jobs this turn.

Frozen plan includes execution config,code,base inputs and accepted source publication identity. Release draft disabled. Launcher16CPU/32GiB/90min,6x600s maximum60solver-minutes plus setup/readback;cm1 placeholder route requires fresh live review before submission. Failures preserve partial outputs and stop dependent stages;no automatic retries or bulk scan.

New code: `expanded_adapter.py` settings11/build25/audit42/start58;runner schedule16/release23/source38/inputs53/solve62/audit93/validate112/run125;freeze helper6;new launcher/tests/config. All prior solver source,scientific spec and artifacts unchanged. Existing untracked operational records preserved and included in suggested commit.

## Next

User commit → full tests → real-data and compute-model preflight (includingK80/grid dimensions and start/readback path) → live partition/queue/storage review → tested release/submission → independent result review. If six-stage validation passes,prepare pre-bulk production config/scan/resources and commit using7200s per solve. Current600s is validation only;no new zero-gap rule. Big-M retained,SOS1deferred;fixedCOACH8repair remains optional,not a prerequisite.
