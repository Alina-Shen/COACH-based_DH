# Step 13 Q-Chem boundary adapter and identity smoke

The Q-Chem Step-13 adapter is implemented and the bounded closed/open-shell
identity smoke passes.  This step promoted the already validated Q4
integratedDV artifacts and Step-9 same-archive scalar artifacts; it did not run
a new SCF, invoke Q-Chem, submit Slurm work, or rebuild Q-Chem.

## Implementation

- `revwb97m2/qchem_step13_stages.py` implements eight immutable boundaries:
  `qchem_archive`, three `integrated_dv_*` grids, `vv10`, `ri_mp2`, `d4_atm`,
  and `assembly`.  Every boundary is atomic, hash-pinned, identity-pinned, and
  independently reusable only after validation.
- The adapter rejects mixed species, authoritative inputs, and Q-Chem archive
  identities across Q4 and Step 9.
- `assembly` publishes only the scientifically active
  `R2_coachform_292`: the 288 Q4 features on grid `250974`, followed by raw
  SR-HF, VV10, total frozen-core PT2, and D4-ATM.  It also records grid
  differences for `99590` and `75302`.  It deliberately does not invent the
  nonlinear-incompatible R1 block.
- `scripts/run_step13_qchem_identity_smoke.py` promotes the frozen
  closed-shell-singlet UKS `h2o_SW49` and open-shell-doublet UKS
  `12_NH2rad_HNBrBDE18` gateways.
- `scripts/validate_step13_qchem_identity_smoke.py` independently revalidates
  all 16 boundaries and checks exact Q4-prefix and Step-9-tail assembly.

## Results

Artifacts are under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step13/qchem_identity_smoke_v1`.
Both species pass all eight boundary checks.  The final vector hashes are:

- `h2o_SW49`: `5e6247ec8c195370e6d94bf2af136a24619dc813eb35aa6c785fa177317483f5`
- `12_NH2rad_HNBrBDE18`: `a06eb64fd2842b86cd2102ada8c98d80e1563cfa8093832f6db8062d7b4a2a32`

A second driver pass reused all 16 boundaries without rewriting them.  The
aggregate validation is
`revwb97m2/manifests/production_generator/step13_qchem_identity_smoke_validation_v1.json`.

The immutable, non-submitting 2,799-species plan was regenerated as v2 with
plan ID `37485e77512d2154`.  It pins the Step-9 validation and Step-13 adapter,
marks the scalar and R2 assembly implementations validated, retains the
conservative Step-12 resources, and keeps `submission_authorized: false`.
The prior v1 plan was preserved unchanged.

Verification: all 54 repository tests pass, the scientific specification
validator passes, and `git diff --check` is clean.

## Remaining Step-13 gate

This smoke validates artifact promotion, identity, assembly, and resume
semantics using existing gateway calculations.  Step 13 remains in progress
until a fresh production-style species runner executes the Q-Chem archive-copy,
three integratedDV, and two scalar jobs for a species without pre-existing Q4
and Step-9 outputs.  Bulk production remains unauthorized under Q7.
