# Pinned GSCDB AdditionalSets snapshot

The heavy-data directory
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/authoritative_inputs/qchem/additionalsets_gscdb_8f2c7e5`
is a byte-for-byte snapshot of `AdditionalSets/` from
`JiashuLiang/GSCDB` commit
`8f2c7e5f683824c79c7035714de215ec22d0f04a` (2026-03-18). Every one of its
7,310 source files is pinned by the versioned `MANIFEST.sha256` in this
directory.

The Q-Chem inputs, rather than the derived XYZ files or orbital scratch, are
authoritative for geometry, charge, multiplicity, basis, ghost centers, and
other input metadata. BigNC contains 75 inputs for 25 L14/vL11 interactions;
GDB9-W1-F12 contains 3,371 inputs for 3,366 atomization energies; and OPT
contains 206 inputs (122 W4-11-GEOM and 84 SE systems).

BigNC and GDB9-W1-F12 enter the frozen energy final-assessment role. OPT is a
separate geometry-optimization assessment and is not mixed into the
fixed-geometry energy tables. COACH itself optimized D4-ATM parameters on
L14/vL11, so BigNC is an untouched assessment for `revwb97m2` only while no
model or dispersion parameter is selected from it. GDB9-W1-F12 is the stronger
untouched robustness test identified by the COACH paper.

All 3,652 external Q-Chem inputs set `UNRESTRICTED True`. The role-manifest
builder parses BigNC and GDB9 metadata and records it alongside the core input
metadata; it never reads Q-Chem orbitals.
