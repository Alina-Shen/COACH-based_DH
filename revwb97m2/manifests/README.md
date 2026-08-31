# Manifests

This directory holds small, version-controlled manifests defining expected
species, dataset membership, immutable source locations, and experiment input
sets. Large checksums, copied scratch trees, matrices, and logs belong under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2`.

The authoritative production manifest is in [`gscdb137/`](gscdb137). It is
generated from a pinned GSCDB Git commit and independently distinguishes the
137 benchmark datasets from the appended `SC74` and `OEEFD` auxiliary rows.
Rebuild it with:

```bash
python scripts/build_gscdb137_manifest.py --gscdb-root /path/to/GSCDB
python scripts/validate_gscdb137_manifest.py
```

The adopted final/Cycle-2 fitting manifest is
[`weights/coach_si_table2_final_cycle_training_weights.csv`](weights/coach_si_table2_final_cycle_training_weights.csv).
Its 49 SI rows and expanded 1,498-entry record are documented and validated in
[`weights/README.md`](weights/README.md). The older first-cycle transcription
is retained as historical evidence only.

The locked fitting, model-selection, overfitting-diagnostic, and external
final-assessment roles are in [`data_roles/`](data_roles). These manifests also
contain the exact unique species lists and non-orbital geometry/basis metadata
parsed from verified, hash-pinned Q-Chem input snapshots. The official GSCDB
AdditionalSets snapshot supplies BigNC, GDB9-W1-F12, and OPT inputs; no
geometry or basis metadata is inferred from orbitals.

The frozen all-UKS PySCF molecular-input policy and reproducible build commands
are in [`pyscf_inputs/`](pyscf_inputs). The 17,658-record immutable snapshot is
stored under the heavy-data authoritative-input tree; it preserves source
geometry, charge, multiplicity, basis/ECP blocks, ghost centers, dataset roles,
and hashes, but deliberately remains non-runnable until the step-6 basis bridge
is validated. That validation is now complete in [`basis_bridge/`](basis_bridge):
the immutable Step-5 records are unchanged, while the bridge supplies the
resolved PySCF orbital, auxiliary, and ECP definitions plus a 17,658-row audit
index and independent passing report.
