# Step 8: manifest-driven parent SCF and checkpoint identity

## Outcome

Step 8 is complete for the closed-shell `h2o_SW49` gateway. The new
`revwb97m2/parent_scf.py` driver resolves a species from the immutable Step 5
record and validated Step 6 basis overlay, runs the frozen all-UKS
omegaB97M-V parent, validates the checkpoint against the fresh density and
Step 7 features, and publishes atomically without reading Q-Chem orbitals.

## Implemented workflow

- Hash-check the scientific specification, immutable JSONL/checksum manifest,
  Step 5 validation, Step 6 resolved records, and Step 6 validation before any
  SCF work.
- Seek directly to one immutable record using a generated, hash-checked
  17,658-row byte-offset index instead of reparsing the full JSONL in every
  species task.
- Require the immutable record to specify UKS and UMP2 with no exception path.
- Build the orbital molecule, ECP, and auxiliary molecule through the Step 6
  bridge and record definition hashes and AO dimensions.
- Apply the dataset-dependent parent grids, `conv_tol=1e-9`, maximum 200 SCF
  cycles, and runtime-query the range-separation coefficients rather than
  hard-coding the short-range-HF fraction.
- Save the PySCF checkpoint and alpha/beta density matrices, reconstruct the
  parent energy from nuclear, one-electron, Coulomb, semilocal XC, SR-HF,
  LR-HF, and native VV10 components, and record spin/gradient diagnostics.
- Reload the checkpoint into a separately configured UKS object and require
  bitwise-equal alpha/beta densities and selected `(64,154,166)` integratedDV
  features on the unpruned `75,302` grid.
- Refuse existing output directories, use a hidden temporary directory, write
  completion only after validation, rename atomically, hash every artifact,
  and make the validated checkpoint read-only.
- Provide a recovery path for a converged checkpoint when a later diagnostic
  is interrupted; recovery never restarts SCF and repeats component and
  checkpoint-feature validation before publication.

## Gateway result

The real `h2o_SW49` record is immutable-manifest line 17,625 and resolves to
10 electrons, 132 orbital AOs, and 287 auxiliary AOs. Observed results:

- UKS omegaB97M-V energy: `-76.43996767776265` hartree.
- Difference from the earlier accepted PySCF gateway: about `5e-14` hartree.
- Parent reconstruction error: `1.4210854715202004e-14` hartree.
- Runtime `(omega, SR-HF, LR-HF)`: `(0.3, 0.15000000000000002, 1.0)`.
- Spin contamination: `<S^2> = 7.895906151134113e-13`.
- Checkpoint alpha and beta densities: bitwise identical, maximum difference
  `0.0`.
- All 288 selected semilocal features across 67,952 grid points: bitwise
  identical, maximum difference `0.0`.
- Q-Chem orbitals and `qarchive.h5`: not used.
- Independent validator: all 13 checks passed.

The heavy gateway is at
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/gateway/h2o_SW49`.
The lightweight validation is
`revwb97m2/manifests/parent_scf/validation.json`.

## Stability limitation and recovery

The PySCF internal UKS stability calculation warned that the NLC contribution
is omitted from `gen_response` and remained CPU-bound for more than 30 minutes
after the parent had converged. It was interrupted and recorded as
indeterminate; no alternative orbitals were adopted. The converged checkpoint
and fresh densities were recovered without restarting SCF, independently
revalidated, and then published. This does not establish that the solution is
stable or unstable.

## Recommended plan updates

1. Replace the old Step 8 phrase "deterministic reference selection" with the
   already-frozen rule "UKS for every species without exceptions."
2. Pull checkpoint-stage resumability forward from Step 13. Complete and
   validate the parent checkpoint before stability, VV10/PT2, or full feature
   stages so later failures cannot erase converged SCF work.
3. Decide explicitly whether the universal stability requirement should be
   amended. PySCF's current result omits NLC and is very expensive. A reasonable
   alternative is a separate, timed diagnostic for gateway/model-critical or
   flagged cases, but changing the frozen policy requires a specification
   amendment.
4. Run remaining multi-species/open-shell gateways through Slurm and begin
   collecting wall-time/memory data now, feeding Step 12 instead of waiting
   until after all gateway engineering is complete.
5. Update Step 13's storage wording from full `180 x 96` matrices to the frozen
   selected `3 x 96` matrix unless a future scientific decision reopens
   channel-family selection. The current model fits new coefficients in rows
   `(64,154,166)` and does not need 177 unused rows.

The next implementation gate remains the open-shell parent/UMP2 and scalar
double-hybrid path. The stability-policy amendment is a user/scientific choice,
not something to change silently in production code.
