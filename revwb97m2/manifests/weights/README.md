# Training-weight manifests

The adopted revwb97m2 fitting selection and weights come solely from updated
COACH SI Section 3.5, final/Cycle-2 Table 2, pages 18-20. The authoritative SI
PDF SHA-256 is
`751b32e29c5a0cfb660d2f912be7d447014697294e9ef317eedd07f26d61956b`.

- [`coach_si_table2_final_cycle.yaml`](coach_si_table2_final_cycle.yaml) is the
  source-oriented 49-row transcription, including all ten ordered partial
  selections.
- [`coach_si_table2_final_cycle_training_weights.csv`](coach_si_table2_final_cycle_training_weights.csv)
  is the released-COACH-compatible fitting input.
- [`coach_si_table2_final_cycle_entries.csv`](coach_si_table2_final_cycle_entries.csv)
  expands the table to 1,498 ordered reactions and numeric objective weights.
- [`coach_si_table2_final_cycle_provenance.json`](coach_si_table2_final_cycle_provenance.json)
  pins sources and artifact hashes.
- [`coach_si_table2_final_cycle_validation.json`](coach_si_table2_final_cycle_validation.json)
  records the passing independent validation.

Rebuild and validate from the repository root with:

```bash
module load miniconda3
conda run -n coach python revwb97m2/scripts/build_cycle2_weight_manifest.py
conda run -n coach python revwb97m2/scripts/validate_cycle2_weight_manifest.py
```

For AE18, updated Table 2 specifies objective weight `1/sqrt(j)` in listed-atom
order. The compatible CSV uses the released COACH keyword `Shrink`, which
expands to exactly that formula. The older
[`coach_si_table2_first_cycle.csv`](coach_si_table2_first_cycle.csv) remains
historical evidence only and is not a production fitting input.
