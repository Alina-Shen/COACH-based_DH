# 2026-08-29 final/Cycle-2 COACH weight manifest

## Authority

The sole scientific authority is updated COACH SI Section 3.5, Table 2, pages
18-20 of `coach/paper/SI_COACH_2026MHG.pdf`, SHA-256
`751b32e29c5a0cfb660d2f912be7d447014697294e9ef317eedd07f26d61956b`.
The table says these are the final-cycle coefficient-fitting selections and
objective weights fixed before best-subset optimization.

No weights or reaction selections were inferred from performance results. The
SI row order, partial-selection order, counts, property classes, and numeric
weights were transcribed directly. The only normalization is converting the
SI's printed reaction form, such as `Dip146 1`, to the exact checked-in
`DatasetEval.csv` identifier `Dip146_1` and verifying that identifier there.

## Published artifacts

- `coach_si_table2_final_cycle.yaml`: source-oriented transcription of all 49
  SI rows, including all ten explicit partial-selection lists.
- `coach_si_table2_final_cycle_training_weights.csv`: 49-row input compatible
  with the released COACH preprocessing schema. AE18 uses `Shrink`, whose
  released implementation is exactly `1/sqrt(j)`.
- `coach_si_table2_final_cycle_entries.csv`: fully expanded, ordered 1,498-row
  manifest with the set/subset, property class, DatasetEval dataset, exact
  reaction ID, DatasetEval order, selection order, weight formula, and numeric
  objective weight.
- `coach_si_table2_final_cycle_provenance.json`: hashes and source paths.
- `coach_si_table2_final_cycle_validation.json`: independent validation result.

## Validation result

All checks pass:

- 49 SI rows expand to exactly 1,498 fitting entries.
- Every mapped dataset exists in the pinned `DatasetEval.csv`.
- Every selected reaction ID exists in its mapped dataset.
- Every explicit list is unique and follows DatasetEval file order.
- Every `All` row reproduces that dataset's complete DatasetEval order and the
  SI count, including `PCONF21` with 18 entries and `TAE_W4-17nonMR` with 183.
- The two SI subsets `RG10N1` and `RG10N2` map to distinct ordered selections
  within DatasetEval dataset `RG10N`; the SI `CUAGAU83` row maps to its listed
  `CUAGAU_*` reactions in DatasetEval dataset `CUAGAU83`.
- Every non-AE18 entry has its SI constant objective weight.
- AE18 has 18 entries with objective weight exactly `1/sqrt(j)` for listed
  order `j=1,...,18`; these values match the released COACH `Shrink` expansion.
- All weights are positive and finite, and no set/reaction pair is duplicated.

The pinned `DatasetEval.csv` SHA-256 is
`0b95de0d35308e7ea39e1f73ed68d7ab5a65f4195212ee6295383fbf22281fbe`.

## Specification integration

With user permission on 2026-08-30, specification v3 now names the published
row, expanded-entry, source, provenance, and validation artifacts. Its
independent validator checks their existence, 49/1,498 counts, passing
validation record, SHA-256 hashes, and agreement between data-policy and
execution-protocol paths. The final/Cycle-2 weight-manifest gate is closed.
