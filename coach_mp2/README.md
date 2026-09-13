# COACH MP2

Step 1 is complete: the 18-step index and scientific specification v1 are frozen
and validated. The initial M2-total model uses fixed COACH Q-Chem UKS orbitals,
fixed target omega=0.27 bohr^-1, and the current revwb97m2 fitting protocol.
The optional outer omega scan is deferred until functional-design choices are
fixed. Native chemistry and runtime release remain pending.

## Contents

- [Scientific specification and rationale](docs/scientific_specification.md)
- [Authoritative specification v1](configs/scientific_spec_v1.json)
- [Frozen step index](configs/step_index_v1.json)
- [Mutable step progress](manifests/progress.json)
- [Step 1 report](results/step1_complete.md)
- [Storage policy](docs/storage_layout.md)
- [Live project plan](../../codex_notes/projects/coach-based_dh/COACH-based_mp2.md)

## Current structure

```text
coach_mp2/
├── README.md
├── configs/
│   ├── scientific_spec_v1.json       # Authoritative scientific choices
│   ├── step_index_v1.json            # Permanent 18-step IDs and exit gates
│   └── mirror_contract_v1.json       # Earlier preparation guide; v1 spec takes precedence
├── docs/
│   ├── scientific_specification.md   # Equations, rationale and validation boundaries
│   ├── storage_layout.md            # Three-root write contract
│   └── mirror_preparation.md         # Historical preparation/port guide
├── manifests/
│   ├── scientific_spec_v1.freeze.json # Immutable scientific artifact hashes
│   ├── step_index_v1.freeze.json     # Index identity, frozen first
│   ├── step1_sources_v1.json         # Read-only reference/source identities
│   ├── revwb97m2_reference_v1.json   # Earlier preparation snapshot
│   └── progress.json                # Mutable progress against fixed IDs
├── scripts/
│   ├── build_scientific_spec_v1.py   # One-time non-overwriting spec builder
│   ├── validate_scientific_spec.py   # Read-only semantic/source/freeze checks
│   ├── freeze_scientific_spec.py     # One-time test and hash publication
│   └── publish_step1_notes.py        # Scoped notes/storage README synchronization
├── tests/test_scientific_spec.py     # 17 adversarial contract/path tests
└── results/
    ├── step1_complete.md            # What changed, why and remaining work
    ├── step1_database_comparison.json # Three authoritative metadata tables
    ├── step1_inheritance_audit.json  # Independent comparison with reference choices
    ├── step1_tests.json              # Test evidence
    ├── step1_tests.log
    └── step1_validation.json         # 50-check post-freeze report
```

Recheck without chemistry, solver/license use or bytecode writes:

```bash
python3.9 -B coach_mp2/scripts/validate_scientific_spec.py
python3.9 -B -m unittest discover -s coach_mp2/tests -p 'test_scientific_spec.py' -v
```

Code/settings/important lightweight results stay here. Heavy data lives under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2`; Q-Chem scratch lives
under `/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2`. Project notes are the
explicit write exception. All original COACH/revwb97m2/GSCDB sources remain
read-only, including their Python bytecode/cache directories.

A scientific freeze is not a runtime or submission release. The GSCDB137 and BigNC source paths are recorded in
[orbital locations](manifests/orbital_source_locations_v1.json); directory/sample
archive readability passed, while full inventory, method validation and copying remain pending.
No Git commit is performed by the freeze scripts. Maintain these descriptions
when directory structure or artifact purposes change.

## September 12 source locations and solver research

Added [orbital_source_locations_v1.json](manifests/orbital_source_locations_v1.json)
and [open-source MIO comparison](results/2026-09-12-open-source-mio-solvers.md).
The [notes publisher](scripts/publish_solver_research_notes.py) records this update.
SCIP is recommended for the first benchmark; no solver installed or frozen
scientific setting changed. The existing directory purposes are unchanged.

## Step 2 native baseline pilot

[Progress and limitations](results/step2_progress.md), [validation protocol](configs/step2_validation_protocol_v1.json),
[native pilot results](results/step2_pilot_v1.json), and [runtime/input/source hashes](manifests/step2_pilot_v1.json).
The two-system diagnostic is explicitly user-authorized; the frozen scientific
contract's original runtime/submission flags do not authorize bulk production.
Solver selection remains deferred. Update the live project-notes plan table after
every future progress increment.

The Step 2 baseline test needs the existing dh environment:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /global/home/users/yaoshen/.conda/envs/dh/bin/python -B -m unittest discover -s coach_mp2/tests -p 'test_step2_baseline.py' -v
```

`runtime/` is the project-local temporary location for lightweight Python audits;
`inputs/step2_pilot_v1` and `slurm/` retain pilot inputs and submission settings.
Native output/scratch use the dedicated external coach_mp2 roots.

## Step 2 complete

[Completion report](results/step2_complete.md) and [44-check native audit](results/step2_fixed_v3_validation.json).
The validated fixed-orbital route requires NO_ORTHO TRUE with the older SCF driver
and MP2_RESTART_NO_SCF TRUE. MO files remain byte-identical; density reconstruction
is independently validated at roundoff. The v2 failed integrity attempt is retained.
Next stable step is 3; full-domain runtime readiness remains a later gate.

## Step 3 complete

[Data roles and metrics](results/step3_complete.md) are frozen in
[the Step 3 manifest](manifests/step3_freeze_v1.json). The project-local
`manifests/data_roles_v1/` contains source tables, ordered role CSVs, weight
transcription and metric policy; it does not certify orbital or input chemistry.
All 79 semantic checks and 18 tests pass. The metric evaluator reproduces all
137 published development NERs. Solver choice remains deferred; pause before
backend-dependent work. Next stable step is 4.

## Step 4 complete — 2026-09-12

All 17,452 energy-role input templates now match the pinned molecular and basis authority. See [work list](results/step4_complete.md), [snapshot](manifests/step4_snapshot_v1.json), and [validation](results/step4_validation.json). Original/derived input tar and detailed audit live in the heavy root `step4_inputs_v1/`; these are scientific templates awaiting stage-specific execution controls. Next: Step 5 archive inventory and basis compatibility. Solver choice remains deferred.

## Step 5 in progress — 2026-09-12

[Work list and remaining gates](results/step5_progress.md): 14,077 structurally passing archives are being hash-verified into the heavy root `step5_import_v1/`; four cases are quarantined and 3,371 GDB9 archives are missing. Run `python3 -B coach_mp2/scripts/step5_status.py` from the workspace parent for copy counts. Structural imports are not production-ready archives. Solver choice remains deferred.

GDB9 scheduling update: the user deferred the 3,371 final-only COACH archives to a future TODO before Step 17; this does not block current development. See [deferral policy](configs/step5_gdb9_deferral_v1.json). No assessment species are dropped.

## Active basis amendment — ISOL24_i8e

User approved `def2-QZVPP` in place of `def2-QZVPPD` for ISOL24_i8e only. [Amendment](configs/input_basis_amendments_v1.json) and [active input](inputs/basis_exceptions_v1/ISOL24_i8e.in) supersede that species in the frozen Step 4 snapshot. Use `scripts/active_input_authority.py` to read current metadata; future input extraction must apply `input_overrides` from the amendment. Auxiliary basis remains RIMP2-def2-QZVPPD. The 1,884-AO count matches the source; exact generating-basis identity/native compatibility still need validation. No other species or frozen evidence changed.

## Step 5 import audit and completion chain

All 14,081 available imports (178,586 files; 805.6 GB) are audited. Isolated NoSCF orientation-fix build 25827268 passed; five native cases pass and ISOL24 is running. Audit 25827432 and guarded finalization 25828053 follow native job 25827314. See [work list](results/step5_continuation_20260912.md) and [progress](manifests/progress.json) for current state. Completion requires all six native checks; MP2/full production remain separate.

## Step 5 available-source scope complete

All 14,081 supplied species are imported and audited; six native regressions pass with the project-local no-SCF orientation bypass. Use [runtime authority](configs/step5_runtime_authority_v1.json) and [completion evidence](results/step5_complete.md). Next Step 6. GDB9 3,371 remains deferred before Step 17; no full-domain/MP2 production pass is claimed.

## Step 6 accuracy gate open

See [findings](results/step6_findings.md): water passes; carbon approved auxiliary fails the RI accuracy criterion. Diagnostic auxiliary inputs are not production authority. Source/MO/COACH Fock checks and seven tests pass. Next step remains 6; no solver decision required.

## Step6 complete with explicit carbon accuracy deferral

Approved auxiliary basis retained by user; AutoAux not adopted. Use [runtime contract](configs/step6_runtime_authority_v1.json) and [completion report](results/step6_complete.md). Raw carbon numerical failure remains recorded. Next required Step8; Step7 optional.

## Step8 native feature gateway complete

All twelve fixed-orbital native cases and six independent three-grid feature comparisons pass at omega=0.27. Six 292-column pilot vectors and four grid-difference vectors are published. Use [Step8 runtime authority](configs/step8_runtime_authority_v1.json), including its isolated libks.so, and [complete work list](results/step8_complete.md). Carbon RI accuracy remains explicitly deferred with the approved basis. Next Step9; no solver decision required for Step8. Earlier progress sections are historical.

## Step9 constraint implementation complete

Solver-neutral C0/UEG/support/scalar/selected-grid matrices and independent audits pass eight tests. [Work list and scope](results/step9_complete.md). Actual production row selection waits for validated discovery fits; solver binding waits for Step14. Next Step10.

## Step10 resource pilots in progress

[Work list and status](results/step10_work.md). Three native size-tier jobs submitted; await measurements/accounting and capacity review. No solver dependency or bulk release.

## Separate SCIP pilot installed

SCIP10.0.2 / PySCIPOpt6.2.1 / SoPlex8.0.2 installed in the project data environment. [Work list, budget and validation](results/scip_pilot_installation.md). Production backend unchanged; full adapter remains Step14. No Gurobi comparison in this project requested.
