# Experiment identity and registry

Every experiment has one immutable configuration and an ID of the form:

```text
<model>-<profile>-s<sparsity>-p<pass>-<config-hash8>
```

Example: `r2-c0-s32-p1-a17c9e2`.

- `r2`: feature model.
- `c0`: constraint profile; `smoke` is used for plumbing tests.
- `s32`: sparsity; use `sna` when sparsity is not applicable.
- `p1`: workflow pass; `p0` is used for pre-fit smoke tests.
- `a17c9e2`: first eight hexadecimal characters of the immutable config's
  SHA-256 hash.

The prefix is readable metadata, while the hash prevents scientifically
different configs from sharing an identity. Status is deliberately stored in
the registry rather than the config, so recording a run outcome does not alter
the scientific input.

## Create and update

Freeze and register a new experiment:

```bash
python scripts/experiment_registry.py create \
  --config /path/to/completed-draft.yaml \
  --model r2 --profile c0 --sparsity 32 --pass-number 1 \
  --description "One-line description"
```

This copies the config to `experiments/<ID>/config.yaml`, makes it read-only,
adds a `not start` row to `registry.csv`, and regenerates `../EXPERIMENTS.md`.
Never edit the frozen copy. Any scientific-input change creates a new ID.
Start by copying `config_template.yaml`; creation rejects missing structured
sections, CLI/config identity disagreements, and unfilled placeholders.

After every run attempt, update the same registry row:

```bash
python scripts/experiment_registry.py mark \
  --experiment-id r2-c0-s32-p1-a17c9e2 \
  --status succeed \
  --result-path /absolute/path/to/result
```

Use only `succeed`, `fail`, or `not start`. Validate the registry with:

```bash
python scripts/experiment_registry.py validate
```

`registry.csv` is authoritative; `../EXPERIMENTS.md` is its generated,
human-readable view. Experiment configs and the registry belong in version
control. Heavy run artifacts belong under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/runs/<ID>/`.

The two currently registered smoke tests predate this schema and are preserved
as read-only legacy config snapshots. All newly created experiments must use
the structured template.
