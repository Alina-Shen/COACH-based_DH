# GSCDB137 species-manifest result

Date: 2026-08-28

Status: **manifest complete; basis-policy decision resolved in specification version 2**

## Authoritative counts

| Scope | Datasets | Reactions | Species |
|---|---:|---:|---:|
| GSCDB137 | 137 | 8,377 | 13,907 |
| Appended auxiliary groups (`SC74`, `OEEFD`) | 2 | 71 | 127 used, including 99 auxiliary-only |
| Complete GSCDB molecular registry | — | 8,448 | 14,006 |
| BigNC external evaluation (`L14`, `vL11`) | 2 | 25 | 75 |

Source: `https://github.com/JiashuLiang/GSCDB.git` at commit
`f62f5d844d64b4ff451cbfc9320a39d830857099`.

## Orbital inventory

- `/global/scratch/users/jsliang/wB97M-V`: all 14,006 canonical directories;
  14,004 canonical `qarchive.h5` files. `3d4dIPSS_V_ES` and
  `3d4dIPSS_V_GS` have `archive.h5` but no `qarchive.h5`. There are 483
  noncanonical directories, which the manifest excludes.
- `/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2`: all 14,006 canonical
  directories and `qarchive.h5` files; 13,167 canonical `.staged.ok` markers;
  17 excluded debug/backup directories.
- `/global/scratch/users/jsliang/BigNC/wB97M-V`: all 75 BigNC directories and
  `qarchive.h5` files, with no extras.

No files were copied from any of these roots.

## Basis-policy finding and resolution

The GSCDB137 molecular registry contains 8,276 def2-QZVPPD species and 5,631
species with other basis labels. The project chose to follow COACH/GSCDB
closely. Scientific specification version 2 now makes the authoritative
per-species assignments mandatory and preserves generated Q-Chem orbital and
auxiliary-basis blocks. No orbitals were copied as part of this amendment.

## COACH training-weight finding

The SI provides only the first-cycle training table: 46 dataset/subset rows and
1,766 selected data points. It states that later-cycle weights are available
upon request. The exact Table 2 values were transcribed with mapping warnings;
they are evidence, not an adopted revwb97m2 objective. Standard-error, O24x5,
and TMC34 files were also preserved, explicitly classified as evaluation
weighting inputs rather than universal least-squares weights. The SI's AE18
`Shrink2` footnote (`w=1/sqrt(Z)`) also disagrees with the released
preprocessor's `1/i` implementation, so that rule remains unresolved.

## Validation

`scripts/validate_gscdb137_manifest.py` passed every committed count, scope,
provenance, and SHA-256 check. The live builder also passed its source equality
and scratch-coverage assertions.
