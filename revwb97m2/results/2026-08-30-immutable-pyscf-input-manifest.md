# Immutable all-UKS PySCF molecular-input manifest

## Outcome

Plan step 5 is complete. The frozen snapshot is:

```text
/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/authoritative_inputs/pyscf/revwb97m2_all_uks_inputs_v1
```

It contains 17,658 sorted, unique records: 17,452 fixed-geometry energy-role
species plus 206 separate OPT geometry-assessment species. Every species uses
PySCF UKS and post-SCF UMP2, including closed-shell singlets; no exceptions are
allowed.

## Frozen contents

- Cartesian geometry in Angstrom, charge, multiplicity, and
  `spin = multiplicity - 1`.
- Orbital-basis, auxiliary-basis, and ECP source labels plus verbatim embedded
  Q-Chem blocks where present.
- Fitting, model-selection, overfitting-diagnostic, and final-assessment roles.
- Q-Chem source-input, molecule-block, geometry, normalized PySCF atom, and
  complete-record SHA-256 hashes.
- All 2,771 authoritative counterpoise ghost centers in 50 BigNC species.
- Explicit declarations that Q-Chem orbitals and `qarchive.h5` were not used.

The records intentionally have
`runnable_status = blocked_pending_step_6_basis_bridge_validation`. Step 5
freezes input evidence; it does not claim that Q-Chem basis labels or generated
blocks are already valid PySCF definitions.

## Validation and immutability

The independent validator reparsed and rehashed all 17,658 source inputs and
passed every check. Two builds in new empty directories were byte-identical for
all seven snapshot files. The published files are mode `0444`, the directory
is mode `0500`, and the builder refuses a nonempty destination.

- `MANIFEST.sha256` SHA-256:
  `c4f2d596a5b779bc6bb25d6fb31a2ab79c285374af6388ec960b1461b40238bb`
- `pyscf_input_records.jsonl` SHA-256:
  `2e17d35d5b75a5d282ccb9b9f6619e4f6c13327e8ee9d3b5e5db63cc59905bf0`
- Snapshot size: approximately 62 MiB on the heavy-data filesystem.

## Next gate

Proceed to plan step 6: implement and validate the Q-Chem-to-PySCF basis
metadata bridge. The manifest audit found 593 embedded orbital-basis blocks,
one embedded auxiliary-basis block, 97 embedded ECP blocks, and 3,446
energy-role species without a source auxiliary-basis assignment. Those 3,446
cases need an explicit, validated PySCF auxiliary-basis policy; they must not be
silently inferred during production runs.
