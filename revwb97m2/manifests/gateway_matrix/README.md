# Step-10 scientific gateway matrix and early Step-12 measurements

The frozen seven-species matrix in `step10_gateway_matrix_v1.yaml` covers every
required chemistry and implementation edge with immutable input records. One
species may cover multiple edges; this is deliberate so the gate remains small
enough to diagnose failures rather than becoming a premature production run.

## Scientific cases

| Species | Coverage | Orbital/auxiliary AOs |
|---|---|---:|
| `h2o_SW49` | closed shell | 132 / 287 |
| `12_NH2rad_HNBrBDE18` | correlated open shell | 129 / 287 |
| `BH9_08_1R2` | charged F- | 57 / 157 |
| `CUAGAU_Au01N0_H` | transition metal and implicit def2 ECP | 121 / 317 |
| `AE11_Yb` | heavy all-electron and embedded GEN basis | 184 / 285 |
| `DAPD_B` | open shell, embedded GEN basis and ECP | 109 / 157 |
| `L14_GGG_monB` | counterpoise ghosts, noncovalent, high cost | 1485 / 3621 |

The standard array used 8 CPUs, 40 GiB, and 4 hours on `mhg/mhg/normal`.
The high-cost case uses 16 CPUs, 240 GiB, and 12 hours. Its static dense
three-center estimate is 29.77 GiB, below the frozen 50% requested-memory stop.

## Results and measured restart boundaries

Each gateway is independently restartable at the validated parent checkpoint,
three-grid semilocal matrices, and scalar VV10/RI-UMP2 artifact. Later-stage
failure never removes an earlier completed directory.

| Species | Parent seconds / end RSS MiB | Three-grid seconds / RSS MiB | Scalar seconds / end RSS MiB |
|---|---:|---:|---:|
| `h2o_SW49` | pre-existing | 28.46 / 287 | 51.71 / 276 |
| `12_NH2rad_HNBrBDE18` | pre-existing | 27.96 / 298 | 5.95 / 243 |
| `BH9_08_1R2` | 9.20 / 374 | 6.86 / 185 | 3.22 / 179 |
| `CUAGAU_Au01N0_H` | 72.66 / 872 | 18.73 / 249 | 4.32 / 238 |
| `AE11_Yb` | 118.89 / 2022 | 15.38 / 302 | 3.64 / 334 |
| `DAPD_B` | 28.44 / 749 | 10.03 / 235 | 3.73 / 193 |
| `L14_GGG_monB` | measurement in progress | measurement in progress | measurement in progress |

The detailed record is generated as `step10_resources.json`; it includes every
individual grid's point count and wall time, scratch, checkpoint size, retained
stage storage, and validation state.

## Heavy-element SG-1 compatibility finding

The first AuH and Yb attempts stopped before SCF because PySCF's built-in SG-1
pruning radii table covers H through Ar. The implementation now delegates those
elements unchanged and uses the published remaining-element SG-1 pattern,
`38^12 194^38` (7,828 parent points), only for heavier atoms. Unit tests prove
light-element parity and the exact heavy-element shell pattern. The failed
attempt directories are retained under the heavy-data `failed_gateway_attempts`
tree rather than silently deleted.

Relevant upstream documentation is the
[PySCF limitation report](https://github.com/pyscf/pyscf/issues/2082), the
[Q-Chem quadrature manual](https://manual.q-chem.com/5.4/sect_standard-quad.html),
and the [remaining-element grid specification](https://talk.q-chem.com/t/printing-grid-information-for-dft-jobs/371).

## Early Step-12 interpretation

The exact locked fixed-geometry role union contains 17,452 species after OPT is
excluded. Its median orbital/auxiliary sizes are 356/742.5 AOs, but the maxima
are 5,135/12,132. There are 652 species above the provisional 1,800-orbital-AO
stop and 646 above the 4,500-auxiliary-AO stop. The largest static dense
three-center estimate is about 1.15 TiB; 1,405 species exceed 20 GiB and 387
exceed 100 GiB by that deliberately conservative estimate.

Consequently, this early measurement does **not** authorize a production
array. Full Step 12 must use the completed high-cost observation to define
size tiers, concurrency, and an out-of-core/direct strategy for the upper tail.
It would be scientifically misleading to extrapolate CPU-hours from only the
six small completed gateways.

Regenerate and independently validate the records with:

```bash
python scripts/summarize_step10_resources.py
python scripts/validate_step10_gateway_results.py
```
