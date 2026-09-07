# Local Gurobi gap reproducer candidate

This folder is **not an approved external attachment**. `reproduce.py` needs
only Python and gurobipy, plus the recipient's own working license.

```bash
python reproduce.py
python reproduce.py --model /path/to/full_R2.lp
python reproduce.py --data research_inputs.local.json
```

The first command tests three synthetic one-binary-variable quadratic models
with objective scales 1, 1e-6 and 1e-9. These are diagnostic controls, not
changes to the production scientific objective.

The optional LP replay tests the project model twice, with 60 seconds per
repeat, one thread, seed zero, the original feasibility/integrality tolerances,
and the original beta/selection MIP start. It needs no COACH imports, NumPy,
Q-Chem, orbital files or Slurm. Gurobi licensing must be configured locally;
no license file should be attached or sent.

The `--data` alternative constructs the model directly from exact JSON-exported
input numbers and has the same bounded settings. `prepare_local_data.py` is a
project-side preparation utility (requires NumPy/COACH imports); the recipient
does not need it to run `reproduce.py`. The generated `research_inputs.local.json`
is explicitly git-ignored and **not approved for external sharing**. Its numeric
round-trip is checked before writing; source hashes are retained.

The local model is
`revwb97m2/results/step15_wls_60s_25658936/full_R2.lp`, relative to the project
root. **It contains research-derived coefficients.** It remains in its original
location and is not copied into this folder or approved for disclosure.
LP exports can lose precision; standalone replay must be tested before calling
this a reproducer. A successful full-model replay is not proof of mathematical
minimality. Wall-clock-limited results can differ between machines.

The JSON output labels raw infinity as a string and separately records the
derived ratio, preserving the distinction. Errors expose only type/code, not
credential-bearing messages. Exit zero means execution finished; inspect each
case's `discrepancy` field to determine whether the issue reproduced.

Review the local support draft and test evidence before any external sharing.

## Verified local outcomes (September 6–7, 2026)

- LP replay job `25659090`: completed in 2:05; neither repeat reproduced the
  discrepancy. Both raw and derived gaps were 0.9999991006408575.
- Exact-data direct construction job `25659141`: completed in 2:06; **both
  repeats reproduced** raw infinity versus derived gap 0.9999999995553118.
  Objective and bound matched the original project run exactly.
- Synthetic controls all solved optimally with gap zero; they are not a
  synthetic minimal reproducer.
- The direct case remains 604 variables and 610 constraints. It is standalone,
  not proven minimal. No explanation of Gurobi's internal cause is established.
- Evidence: `revwb97m2/results/gap_reproducer_25659090.json` and
  `revwb97m2/results/gap_reproducer_25659141.json`, relative to project root.

The smallest currently verified local attachment set is `reproduce.py` plus
`research_inputs.local.json`; review research-data disclosure before sharing.
