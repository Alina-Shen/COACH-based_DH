# Authoritative GSCDB137 species manifest

## Definition

The manifest is pinned to Jiashu Liang's GSCDB repository commit
`f62f5d844d64b4ff451cbfc9320a39d830857099`. The authoritative boundary is:

1. The 137 names in `Info/Standard_errors.csv` define the GSCDB137 datasets.
2. The rows of `Info/DatasetEval.csv` belonging to those names define 8,377
   benchmark reactions.
3. The unique species in their stoichiometries define 13,907 GSCDB137 species.
4. Charge, multiplicity, basis, grid, and related molecular attributes come
   from `Allmols_info.json`.

This procedure deliberately does not infer dataset membership from scratch
directory names. The GSCDB `DatasetEval.csv` contains 71 appended rows assigned
to `SC74` and `OEEFD`. Those groups have no entries in either the 137-row
standard-error registry or the nonblank dataset registry, so they are marked
auxiliary. They introduce 99 species not used by the 8,377 GSCDB137 reactions.
The complete molecular registry therefore has 14,006 records.

The generated artifacts are:

- `species_manifest.csv`: all 14,006 records, with `scope` equal to
  `gscdb137` or `auxiliary_only`, exact dataset membership, charge,
  multiplicity, molecular-metadata basis, and orbital-source availability.
- `dataset_manifest.csv`: the 137 datasets, categories, reaction/species
  counts, reference method descriptions, and standard errors.
- `auxiliary_dataset_groups.csv`: the explicit `SC74`/`OEEFD` exclusion.
- `scratch_inventory.json`: exact directory, `qarchive.h5`, completion-marker,
  missing, and noncanonical-directory inventories.
- `bignc_species_manifest.csv`: the separate 75-species L14/vL11 external set.
- `source_provenance.json`: repository commit, definitions, and SHA-256 hashes.
- `source/`: lightweight verbatim GSCDB CSV inputs. The 13 MB geometry-bearing
  `Allmols_info.json` is not vendored; its hash and derived fields are retained.

## Scratch coverage and the pre-copy gate

Both GSCDB scratch trees contain directories for every one of the 14,006
molecular records. The original `/global/scratch/users/jsliang/wB97M-V` tree
has 14,004 canonical `qarchive.h5` files; the missing files are for
`3d4dIPSS_V_ES` and `3d4dIPSS_V_GS`. The existing
`/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2` tree has all 14,006
canonical `qarchive.h5` files, but only 13,167 canonical `.staged.ok` markers.
Its 17 noncanonical debug/backup directories are never treated as species.

The BigNC source has exactly 75 expected directories and 75 `qarchive.h5`
files, with no extras. BigNC is not part of GSCDB137 and must remain a separate
external evaluation manifest.

The authoritative molecular metadata assigns def2-QZVPPD to only 8,276 of the
13,907 core species. The other 5,631 core species use 13 additional basis
labels. Scientific specification version 2 resolves the earlier conflict by
following these per-species assignments.

The live basis-policy validator checked all 13,907 canonical Q-Chem `input0`
records. All named bases agree semantically with the manifest. For 593 cases,
Q-Chem uses `BASIS GEN` or `BASIS GENERAL` and embeds the actual basis in a
`$basis` block; these blocks must be copied intact. All nonblank advisory
auxiliary-basis labels agree with `AUX_BASIS_CORR`. `AE11_Yb` is the one known
metadata omission: its input authoritatively specifies `AUX_BASIS_CORR GEN`
and provides `$aux_basis`.

## What the papers establish about weights

COACH SI Sections 3.4-3.5 distinguish three different kinds of weighting:

- Dataset-specific standard errors normalize evaluation errors into NERs.
  They are evaluation scales, not least-squares training weights.
- The GSCDB O24/O24x5 and transition-metal files contain special data-point
  weights used by the corresponding evaluation metrics. They are preserved
  verbatim in `source/` and must not automatically be used as global training
  weights.
- Table 2 reports 46 dataset/subset rows, 1,766 selected points, and the
  least-squares weights for COACH's first training cycle. The transcription is
  in `manifests/weights/coach_si_table2_first_cycle.csv`.

The SI says most training used the thesis-era GSCDB138, that weights began from
the omegaB97M-V scheme and were adjusted by active learning, and that weights
were finalized before each design exploration. It also explicitly says the
weights for the remaining cycle are available upon request. Consequently,
Table 2 is not the final COACH weight set. Eight published names are
predecessors/subsets of current GSCDB137 names, five current datasets use only
an unpublished selected subset, and `TMC34` is a composite/subset case. These
must not be mapped automatically.

For AE18, Table 2 uses `Shrink2`; its footnote defines the objective weight as
`1/sqrt(Z)`. The released COACH preprocessing instead expands `Shrink2` as
`1/i` and later multiplies the least-squares rows by `sqrt(weight)`. If AE18 is
ordered by atomic number, this means objective weight `1/Z`, not
`1/sqrt(Z)`. This paper/code discrepancy must be resolved before adopting the
AE18 rule.

## Rebuild and validate

Clone or check out the GSCDB repository at the pinned commit, then run:

```bash
python scripts/build_gscdb137_manifest.py --gscdb-root /path/to/GSCDB
python scripts/validate_gscdb137_manifest.py
```

The builder performs live source and scratch inventories. The validator checks
the committed artifact counts and hashes without requiring scratch access.
