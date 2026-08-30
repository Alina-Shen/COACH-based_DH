# Experiment registry

This table is generated from `experiments/registry.csv`. Use
`scripts/experiment_registry.py create` when freezing a new experiment and
`scripts/experiment_registry.py mark` after every completed run attempt.

| Experiment | Created | Status | Description |
|---|---|---|---|
| [`r2-smoke-sna-p0-d2ea6bd2`](experiments/r2-smoke-sna-p0-d2ea6bd2/config.yaml) | 2026-08-25T15:59:08-07:00 | **succeed** | Legacy H2O plumbing smoke for the 291-feature R2 pipeline on omegaB97M-V/def2-QZVPPD. |
| [`r2-smoke-sna-p0-fb367df0`](experiments/r2-smoke-sna-p0-fb367df0/config.yaml) | 2026-08-25T17:14:16-07:00 | **succeed** | Legacy balanced H2/H4 reaction smoke validating stoichiometry, Nofit algebra, and 291-column reconstruction. |

Status values are restricted to `succeed`, `fail`, and `not start`.
The immutable config hash and result locations are retained in the CSV.
