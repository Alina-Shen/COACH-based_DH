# Q-Chem orbital authority

`qchem_orbital_authority_v1.yaml` freezes the orbital-source policy for
scientific-specification version 5. The 14,006 canonical species are defined by
manifest membership, not by counting every directory below the archive root.
Each named species must have a regular, nonempty `qarchive.h5`.

Validate the live inventory with:

```bash
python revwb97m2/scripts/validate_qchem_orbital_authority.py \
  --output revwb97m2/manifests/qchem_orbitals/validation.json
```

The inventory scan deliberately does not digest the contents of every large
archive. Each execution must hash the source archive, copy it into an isolated
non-overwriting run directory, hash the copy, and require exact source/copy
identity before Q-Chem starts. The authority roots are inputs only and must
never be repaired or changed in place.

The canonical GSCDB/auxiliary scope is ready. BigNC source coverage is also
inventoried, but it requires a project-owned validated copy before use.
GDB9-W1-F12 has no validated Q-Chem orbital authority and is blocked until a
new versioned inventory is established. Missing archives never authorize a
silent PySCF SCF fallback.
