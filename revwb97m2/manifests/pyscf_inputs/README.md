# Immutable PySCF molecular-input manifest

Policy v1 freezes one PySCF molecular definition for every verified input:
17,452 energy-role species and 206 separate OPT geometry-assessment species.
Every definition uses `UKS`; `spin = multiplicity - 1`. Q-Chem inputs are read
only for geometry, charge, multiplicity, basis, auxiliary-basis, ECP, and ghost
centers. Q-Chem orbitals and `qarchive.h5` are forbidden.

The heavy snapshot stores complete records in JSON Lines and a lightweight CSV
index. Embedded Q-Chem basis, auxiliary-basis, and ECP blocks are preserved
verbatim. These records deliberately say that basis translation is pending:
Step 6 must validate aliases and translate generated blocks before the inputs
are considered runnable PySCF jobs.

Build into a new empty staging directory and validate independently:

```bash
python revwb97m2/scripts/build_pyscf_input_manifest.py --output-dir STAGING
python revwb97m2/scripts/validate_pyscf_input_manifest.py --snapshot STAGING --finalize
```

The builder refuses a nonempty destination. The validator reparses every
Q-Chem source, recomputes every record, then emits `validation.json`,
`MANIFEST.sha256`, and `IMMUTABLE.json` only on a complete pass.

The validated v1 snapshot was published read-only at:

```text
/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/authoritative_inputs/pyscf/revwb97m2_all_uks_inputs_v1
```

It contains 17,658 records: 17,452 species needed by at least one fixed-energy
role and 206 separate OPT geometry-assessment species. Its checksum-manifest
SHA-256 is `c4f2d596a5b779bc6bb25d6fb31a2ab79c285374af6388ec960b1461b40238bb`.
Two clean builds were byte-identical. All files are mode `0444` and the
snapshot directory is mode `0500`.
