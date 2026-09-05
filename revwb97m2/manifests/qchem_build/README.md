# Q2 Q-Chem build and provenance

`q2_qchem_build_v2.yaml` is the completed in-place build record. It pins Q-Chem
revision 48798, libks revision 1666, the five-file local diff, the executable
and installed-libks hashes, and the successful archive-read runtime probe.
`q2_qchem_build_v1.yaml` remains as history for the earlier isolated build
request whose four-file implementation compiled but was not on the active
runtime dispatcher path.

The completed installation is the user-directed in-place trunk build. Feature
jobs must set `XC_FXC 3` to select the libks XC Fock engine, in addition to
`MAX_SCF_CYCLES 0`, `GEN_SCFMAN FALSE`, and
`QCHEM_PRINT_INTEGRATED_DV=1`. The selector changes the numerical XC engine,
not the functional or imported density.

The historical v1 Slurm request could be submitted with:

```bash
sbatch revwb97m2/slurm/run_q2_qchem_build.sh
```

No build submission is now required. Q2 completion does not itself authorize
the Q3 smoke matrix or production.

Revalidate the live source, installed binaries, dependencies, and retained
runtime-probe record with:

```bash
python revwb97m2/scripts/validate_q2_qchem_build.py \
  --output revwb97m2/manifests/qchem_build/validation_v2.json
```
