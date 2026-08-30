# Archived Q-Chem-route smoke data

This snapshot preserves the pre-v3 accepted smoke and gateway artifacts copied
from `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2`:

- `revwb97m2/smoke/`: accepted H2O plumbing smoke;
- `revwb97m2/reaction_smoke/`: accepted synthetic reaction/algebra smoke;
- `revwb97m2/logs/` and `revwb97m2/failed/`: associated smoke evidence;
- `revwb97m2/reaction_smoke_25250431.{out,err}`: reaction-smoke Slurm logs;
- `revwb97m2/qchem_gateway/`: the prepared, not-yet-run gateway snapshot.

Files were copied without changing the originals. `MANIFEST.sha256` records
the complete archived payload. The authoritative 14,006-species Q-Chem input
publication is intentionally not duplicated because it is not smoke data.
