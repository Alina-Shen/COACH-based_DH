# Step 8 parent-SCF driver

The production parent driver combines one immutable Step 5 molecular record
with its validated Step 6 basis/ECP overlay, runs a PySCF UKS omegaB97M-V
calculation, and atomically publishes the checkpoint and density artifacts.
It never reads Q-Chem orbitals or `qarchive.h5`.

Every species uses UKS, including closed-shell singlets. The driver queries
the omega, short-range-HF, and long-range-HF fractions from PySCF at runtime,
reconstructs the parent energy from components, and refuses to overwrite any
published species directory. Specification v4 separates stability from
authoritative parent publication: selected gateway/model-critical or flagged
species may receive a timed diagnostic, but no alternative solution is
adopted automatically.

[`record_byte_offsets.csv`](record_byte_offsets.csv) provides a hash-checked
seek index into the immutable JSONL snapshot. This avoids reparsing all 17,658
records in every independent Slurm species task without copying or rewriting
the authoritative records. The independent
[`record_index_validation.json`](record_index_validation.json) confirms every
offset, length, species identity, record hash, and line number.

Before publication, the checkpoint is reloaded into a newly configured UKS
object. Alpha/beta density matrices and the selected Step 7 integratedDV
features on the `75,302` identity grid must be bitwise identical to their
fresh-SCF values. The validated checkpoint is then made read-only. A later
independent process audits that recorded bitwise proof and repeats the reload
with strict `1e-14` density and `1e-12` feature tolerances; cross-process BLAS
reduction order is not required to reproduce identical bytes.

The `h2o_SW49` gateway exposed that PySCF's internal stability response is both
expensive and incomplete for omegaB97M-V: PySCF warns that NLC is omitted from
`gen_response`. The diagnostic was interrupted after more than 30 minutes and
recorded as indeterminate; no alternative orbitals were adopted. The already
converged checkpoint was recovered without restarting SCF, then independently
passed density and feature identity. Specification v4 records this as the
rationale for making stability a separate, non-authoritative diagnostic.

Gateway commands:

```bash
/global/home/users/yaoshen/.conda/envs/coach/bin/python \
  revwb97m2/scripts/run_parent_scf.py --species h2o_SW49

/global/home/users/yaoshen/.conda/envs/coach/bin/python \
  revwb97m2/scripts/validate_parent_scf.py \
  --parent-dir /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/gateway/h2o_SW49
```

The machine-readable policy is
[`step8_parent_scf_v1.yaml`](step8_parent_scf_v1.yaml); the independent result
is [`validation.json`](validation.json).
