# v7 implementation: stop before tests

Status: implementation added; NOT executed or validated. User must commit before
tests. No Q-Chem edits/rebuild, new chemical output, Slurm job or Git commit.

## Files and setting-to-code map

| File | Change |
|---|---|
| configs/archive/scientific_spec.v6.yaml | Byte-identical v6 archive; SHA256 5c7a03994f75ea0076188f20a679647b9cfc2e0ec1c72874b0cc463326a3212e |
| configs/scientific_spec.yaml | v7 pending-pretest status; b5.5, explicit full-SSE ridge1e-10, margin0.999, dh and COACH/user selection policy; omega0.3 retained |
| fit_spec.py | Frozen resolved settings with spec hash; rejects unsupported R2/C0/native-semantic changes; approved scientific contract checked against pinned baseline |
| mio.py | Explicit optional v7 settings; ridge over beta only; internal grid limit; independent public-grid audit; separate SSE/penalty/total reporting and shape checks |
| qchem_scalar_features.py | Explicit v7 derivation emits NL_VV_B550; old no-settings derivation retains1000 for historical contracts |
| scripts/prepare_v7_scalar_input.py | No-overwrite input/preparation provenance only; never runs Q-Chem |
| fit_inputs.py | v7 manifest/spec/array/assembly hashes, parameters, row shapes, role and grid-scalar checks; rejects old b10 inputs |
| scripts/run_v7_fit.py | One diagnostic solve; explicit settings, optional audited starts/grid-candidate union; code/parent/data hashes, strict gap reporting, success-only coefficient publication, resume/readback |
| scripts/validate_scientific_spec.py | v7 configuration-validation dispatch; historical v6 checks retained; does not claim chemical/solver gate completion |
| tests/test_v7_fitting.py | Unrun tests for settings, unsupported changes, ridge algebra, grid margin, b5.5/legacy derivation, independent700-row selection, manifest tampering, failure publication and solver objective coefficients |

Historical no-settings `build_model` and Step9/13 scalar entry points retain
their old numerical semantics. Use the explicit v7 entry points for new work.
Changing shared source hashes means rerunning an old strict provenance audit
against today's source may intentionally fail; historical recorded evidence is
not overwritten. Supported C0 bounds remain implementation constants guarded
by exact contract checks; unsupported scientific profile edits raise instead
of pretending they have been implemented.

## Data manifest needed for chemical tests

`run_v7_fit` requires an independently validated NEW assembly manifest, not an
old Step14 output directory. It must include schema_version1, status validated,
scientific_specification_sha256, role coefficient_fitting, weights_policy
coach_si_table2_final_cycle, ordered reaction_ids, energy_parameters
{omega:0.3,gamma_ss:0.01,vv10_b:5.5,vv10_c:0.01}, vv10_grid_policy
single_grid_zero_difference and its nonempty vv10_grid_zero_reason.

Its artifacts mapping contains path/sha256 records for feature_matrix, target,
objective_weight, grid_difference_99590, grid_difference_75302 and
assembly_validation. Relative paths resolve from the manifest directory.
Assembly validation must report passed=true, matching specification hash, and
array_sha256 mapping those five arrays to the same hashes. This is a publication
contract, not permission to manufacture validation evidence for old arrays.
The new chemical assembly validator/publisher still needs integration with
the refreshed b5.5 gateway data. Unit-test fixtures are synthetic only.

## After the user commits

First run config/unit checks (some solver tests need the configured license):

```bash
module load miniconda3
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate dh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python -m pytest -q revwb97m2/tests
python -m revwb97m2.scripts.validate_scientific_spec --json
```

No command above was executed during implementation. Fixes require review,
commit and affected reruns. A later chemical pilot, only after refreshing and
validating its data, uses `python -m revwb97m2.scripts.run_v7_fit` with explicit
--manifest, --output, --budget14, --seconds60 and --threads1 (the actual CLI
uses separate option/value arguments). A second pass supplies --grid-candidates
with all chosen pass1 result directories and optionally --start. A restart uses
--start plus a NEW output; --resume validates/reuses an already successful
identical output rather than restarting a failed solve.

## Remaining before production, not claimed complete here

- Execute tests only after commit; v7 validation report does not exist yet.
- Refresh b5.5 VV10 gateway and independent assembly publication; validate reuse
  and general recovery/fixed-energy integration before broad species work.
- Full1498-entry input data, larger pilot, memory/Slurm/resource approval.
- Production scan/restart scheduling and batch manifests. This runner is a
  bounded diagnostic building block, NOT an automatic bulk submission driver.
- Dataset-specific analysis/NER for final selection. Near-tie and qualitative
  trade-off TODOs remain deferred and do not block fitting candidates.
- No-ridge alternative is a future TODO, not a prerequisite to first ridge fit.

## Pre-test commit

Use the scoped staging recipe in
`results/2026-09-07-approved-fitting-test-production-plan.md`; include these new
modules, scripts/tests, config archive and this document. Review existing staged
and untracked changes. No `git add .`, force-add, raw solver arrays/logs, license
contents or private research_inputs.local.json. No commit was made by the agent.
