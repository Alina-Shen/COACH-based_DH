# Step 6: validated Q-Chem-metadata-to-PySCF basis bridge

## Outcome

Step 6 is complete. A separate overlay resolves all 17,658 immutable Step-5
molecular records into runnable PySCF orbital-basis, RI auxiliary-basis, and
ECP definitions. The Step-5 snapshot was not modified, and no Q-Chem orbitals
or `qarchive.h5` files were read.

## Implemented translations

- Mapped all observed named orbital-basis labels to PySCF, including the
  `AUG-CC-PCV5Z` H/He convention (`aug-cc-pV5Z`).
- Parsed all 593 embedded Q-Chem/Gaussian orbital-basis blocks.
- Parsed all 97 embedded Gaussian ECP blocks and explicitly attached standard
  def2 ECPs for 367 named-def2 records where Q-Chem applies them implicitly.
- Used hash-pinned Q-Chem RI library files for 14,005 named-source auxiliary
  assignments, avoiding missing heavy-element coverage in PySCF aliases.
- Preserved the one embedded auxiliary block (`AE11_Yb`).
- Froze explicit assignments for the 3,652 inputs with no source RI basis:
  `rimp2-def2-TZVPPD` for 75 BigNC inputs, `rimp2-def2-TZVP` for 3,371
  GDB9-W1-F12 inputs, and `rimp2-def2-QZVPPD` for 206 OPT inputs. Runtime
  automatic auxiliary-basis generation is forbidden.

## AE11_Yb evidence

The earlier OS-MP2 workflow first failed because Yb lacked an auxiliary basis.
The successful input at
`/clusterfs/mhg-data/yaoshen/wb97m_os/GSCDB/wb97m_os_rimp2/work/AE11_Yb.in`
used explicit `BASIS GEN`, `AUX_BASIS_CORR GEN`, `N_FROZEN_CORE 0`, no ECP,
and the saved SCF guess. Its successful output reports 35 alpha plus 35 beta
electrons, 50 orbital shells/184 spherical AOs, and 65 auxiliary shells/285
spherical AOs. PySCF reproduces every one of those structural values exactly.
The input, output, and job-script hashes are frozen in the bridge policy.

## Validation

The independent validator recomputed every per-record resolution, definition
hash, electron count, shell count, and spherical-AO count. It also constructed
real PySCF orbital and auxiliary molecules for closed-shell, embedded-basis,
embedded-ECP, implicit-def2-ECP, BigNC ghost-center, GDB9, and `AE11_Yb`
representatives. Electron counts and spherical AO dimensions also match the
successful Q-Chem outputs for `h2o_SW49`, `3BHET_1.1_dimAB`,
`3d4dIPSS_Ag_GS`, and `DAPD_Pd`. PySCF merges some generated contraction
shells internally, but the AO dimensions are identical. All checks passed.

Key artifacts:

- `revwb97m2/manifests/basis_bridge/step6_basis_bridge_v1.yaml`
- `revwb97m2/manifests/basis_bridge/resolved_basis_records.csv`
- `revwb97m2/manifests/basis_bridge/validation.json`
- `revwb97m2/scripts/pyscf_basis_bridge.py`
- `revwb97m2/scripts/build_basis_bridge.py`
- `revwb97m2/scripts/validate_basis_bridge.py`

The next ordered plan gate is Step 7: implement and validate the project-owned
integratedDV kernel with `gamma_ss=0.01` and semantic rows `(64,154,166)`.
