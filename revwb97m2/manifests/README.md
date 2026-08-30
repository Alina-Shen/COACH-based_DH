# Manifests

This directory holds small, version-controlled manifests defining expected
species, dataset membership, immutable source locations, and experiment input
sets. Large checksums, copied scratch trees, matrices, and logs belong under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2`.

The authoritative production manifest is in [`gscdb137/`](gscdb137). It is
generated from a pinned GSCDB Git commit and independently distinguishes the
137 benchmark datasets from the appended `SC74` and `OEEFD` auxiliary rows.
Rebuild it with:

```bash
python scripts/build_gscdb137_manifest.py --gscdb-root /path/to/GSCDB
python scripts/validate_gscdb137_manifest.py
```

The SI Table 2 transcription in
[`weights/coach_si_table2_first_cycle.csv`](weights/coach_si_table2_first_cycle.csv)
is evidence about COACH's first training cycle. It is not yet an adopted
revwb97m2 weight configuration.
