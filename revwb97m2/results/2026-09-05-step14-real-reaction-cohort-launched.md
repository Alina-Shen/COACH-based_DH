# Step 14 real-reaction cohort: fixed-energy gate passed and species run launched

Date: 2026-09-05 (America/Los_Angeles)

## Outcome

Step 14 is in progress. A frozen 20-reaction, 38-species real-data cohort now
covers all seven fitting property classes. The previously missing
coefficient-independent energy partition has an independently validated
Q-Chem fixed-orbital route. Slurm array `25615636` is generating the cohort
species through the complete Step-13 path plus that fixed-energy calculation.
At handoff, tasks 4--7 had completed with exit `0:0`, tasks 0--3 and 8--11
were running, and tasks 12--37 were held only by the intentional `%8` array
throttle. No Q-Chem rebuild or iterative SCF was used, and Q7 bulk production
remains unauthorized.

## Fixed-energy closure

The v6 292-column model needs
`E_fixed = E_nuclear + E_one-electron + E_coulomb + E_LR-HF` in addition to
the 292 fitted features. Q-Chem's existing scalar job reports short-range HF,
whereas a pure full-range HF print job on the same imported orbitals reports
full HF exchange and the other fixed components. The exact identity
`E_LR-HF = E_full-HF - E_SR-HF` therefore closes the partition without an SCF
optimization.

The frozen gateway contract is
`revwb97m2/manifests/reaction_features/step14_fixed_energy_gateway_v1.yaml`.
Array job `25615292` passed for cross-code `h2o_SW49` and fresh fitting
species `11_H2O_TA13`. The H2O fixed-energy cross-code error was
`2.5544e-8` hartree and every component was below the frozen `2e-6` hartree
tolerance. Both pure-HF reconstruction errors were below the frozen `2e-8`
hartree tolerance. Aggregate validation is frozen at
`revwb97m2/manifests/reaction_features/step14_fixed_energy_validation_v1.json`
(SHA-256 `43e3032943844535797185098e4ebe1987426a22bd10bb21d0fb8736ba82509b`).

## Frozen cohort

`freeze_step14_reaction_cohort.py` selects coefficient-fitting entries only,
requires two-term source stoichiometry, the Step-12 `small_mhg` tier, and a
memory class no larger than 7,500 MB, then ranks by summed orbital AO count
and training global index. Frozen quotas are BH/EF/ISO/INC/NC/TC/TM =
3/3/3/2/4/3/2. This is a deterministic scientific smoke, not a performance
assessment. The source stoichiometry is preserved exactly; zero charge change
is deliberately not required because charge-changing energy-difference
benchmarks are valid members of the fitting data.

The contract
`revwb97m2/manifests/reaction_features/step14_real_reaction_cohort_v1.json`
has SHA-256
`47ae84ce59cb174e679dd846024f5e536360e2ab60a2e0e12465d4002538f727`,
freezes the complete 38-species orbital trees before results, and explicitly
sets `bulk_submission_authorized: false`. Thirty-five cases request 8 CPUs and
14 GiB; three request 8 CPUs and 21 GiB.

## Generation and assembly implementation

- `run_step14_cohort_species.py` validates frozen authorities, reuses only a
  complete Step-13 boundary, otherwise runs the existing fresh Step-13 path,
  runs the pure-HF fixed-energy job on another isolated archive copy, checks
  termination/archive reads/reconstruction/source immutability, and atomically
  publishes a reaction-ready 292-vector, fixed energy, and two 292-column
  grid-difference vectors. Partial directories are preserved and rejected.
- `run_step14_real_reaction_cohort_v1.sh` uses the required module stack and
  runs array `0-37%8` on `mhg/mhg/normal`, 8 CPUs, 21 GiB, and four hours. The
  uniform 21-GiB request safely covers the three larger frozen cases.
- `reaction_assembly.py` applies the exact frozen stoichiometric coefficients
  to species feature vectors, fixed energies, and grid differences; it emits
  the 292-column design matrix and the fitting target
  `reference_energy - fixed_energy` and rejects missing, nonfinite, or
  malformed inputs.
- `assemble_step14_real_reactions.py` validates every reaction-ready boundary
  and hash and atomically publishes the 20x292 matrix, fixed/reference/target
  vectors, objective weights, reaction order, and both grid-difference
  matrices without overwrite.
- `validate_step14_real_reactions.py` independently reloads all 38 species and
  recomputes every stoichiometric sum, then checks exact target identity,
  reaction/reference/weight order, shapes, finiteness, and artifact hashes.
  The downstream contract was frozen while its output root was empty at
  `revwb97m2/manifests/reaction_features/step14_reaction_assembly_v1.yaml`
  (SHA-256
  `9d92713380386476cabded063ce3f40da8b177f548803be99f8797345d6d7342`).

## Verification and handoff

The fixed-energy parser/derivation tests pass, the three new reaction-assembly
tests pass, the pre-launch repository suite passed with 58 tests, cohort and
assembly authority/empty-output preflights pass, and `git diff --check`
passes. Four completed cohort tasks published all eight Step-13 boundaries
and their reaction-ready boundary with empty stderr. Their elapsed times were
5:01--8:00 and MaxRSS was about 1.25--1.85 GiB. Live tasks showed normal CPU,
memory, and archive I/O.

Completion trigger: after array `25615636` terminates, require all 38 tasks to
be `COMPLETED 0:0`, all 38 reaction-ready boundaries to validate, run
`assemble_step14_real_reactions.py`, run the independent validator, and only
then mark Step 14 complete. Do not infer or authorize Q7 bulk production from
this bounded cohort.
