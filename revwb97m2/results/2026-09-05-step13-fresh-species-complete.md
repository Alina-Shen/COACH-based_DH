# Step 13 fresh production-style Q-Chem species complete

Step 13 is complete.  Frozen Slurm job `25614541` ran the first fitting
species with no pre-existing Q3, Q4, or Step-9 gateway outputs through the
production-style Q-Chem path and published the active 292-feature R2 artifact.

## Frozen case and execution

- Species: `gscdb137/11_H2O_TA13`, closed-shell-singlet UKS, 10 electrons,
  132 orbital AOs, 287 auxiliary AOs.
- Selection: small robust water case in the frozen fitting population with
  nonzero PT2 and absent prior gateway results.
- Contract:
  `revwb97m2/manifests/production_generator/step13_fresh_species_smoke_v1.yaml`,
  SHA-256 `85a7f59a2188e8ea0bf7cbdd6713c2b4cbbe3b2373ae898b94aa787dbaa37be0`.
- Resources: `mhg`/`mhg`/`normal`, 8 CPUs, 14 GiB, 2-hour limit.
- Slurm result: `COMPLETED`, exit `0:0`, elapsed `00:01:28`, batch MaxRSS
  `1210836 KiB` (about 1.155 GiB).

The job verified and copied the complete 67-file, 60,776,002-byte orbital
tree; ran three fixed-orbital integratedDV Q-Chem jobs and separate
SR-HF/VV10 and frozen-core RI-MP2 jobs; published Q4 and Step-9 sources; then
published all eight immutable Step-13 boundaries and assembled
`R2_coachform_292`.  It ran no iterative SCF.

Measured Q-Chem wall times were 33.10 s (`250974`), 11.79 s (`99590`),
7.58 s (`75302`), 6.00 s (SR-HF/VV10), and 12.36 s (PT2).  Total runner wall
time was 80.20 s.

## Independent validation

`revwb97m2/scripts/validate_step13_fresh_species.py` independently re-parsed
and validated all three Q4 sources, the Step-9 scalar artifact, all eight
Step-13 boundaries, source immutability, exact Q4-prefix/Step-9-tail assembly,
and second-pass reuse without overwrite.  Every check passes.

The final vector SHA-256 is
`780c6fff72ebde299c7bfb4e71291a218007652d531c8bc66021168413234d82`.
Raw scalar features in hartree are SR-HF `-7.3392745332`, VV10
`0.0207884461`, PT2 `-0.333099176149695`, and D4-ATM
`1.435375685608962e-11`.

Aggregate validation:
`revwb97m2/manifests/production_generator/step13_fresh_species_validation_v1.json`,
SHA-256 `9d772136a3db0005e25abd180c62b647ed674bfa36318517440a6a60cd182da3`.

The immutable 2,799-species plan was regenerated as v3, plan ID
`b5b35aec6a065243`, and pins the fresh validation.  It remains explicitly
non-submitting.  Plans v1 and v2 remain unchanged.  All 56 repository tests,
the scientific-spec validator, and `git diff --check` pass.  No Q-Chem rebuild
was required.

The next scientific step is Step 14: freeze a small real-reaction cohort whose
complete stoichiometric species union can be generated and assemble reaction
feature vectors from the validated species artifacts.  Bulk production
remains gated by Q7.
