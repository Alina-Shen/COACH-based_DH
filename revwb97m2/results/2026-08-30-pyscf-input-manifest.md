# Step 5: immutable all-UKS PySCF molecular-input manifest

## Outcome

Step 5 is complete. The immutable snapshot
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/authoritative_inputs/pyscf/revwb97m2_all_uks_inputs_v1`
contains 17,658 deterministic PySCF molecular-input records: 17,452 species in
the fixed-geometry energy roles and 206 OPT geometry-assessment species.
Every record fixes `UKS`, `UMP2`, and `spin = multiplicity - 1`; there are no
RKS/RMP2 production exceptions.

## Actions and rationale

1. Froze `pyscf_input_policy_v1.yaml` before generation. It records the
   all-UKS decision, source authorities, role counts, ghost-center policy, and
   the boundary between molecular input construction and basis translation.
2. Built `pyscf_input_records.jsonl` with complete PySCF atom strings, charge,
   multiplicity, spin, dataset roles, named basis requests, and verbatim
   embedded Q-Chem basis/auxiliary/ECP blocks. Q-Chem `@Element` ghost centers
   were deterministically converted to PySCF `Ghost-Element` labels without
   changing coordinates.
3. Built `pyscf_input_index.csv` for direct species lookup and exact role,
   source-hash, reference, basis-source, and record-hash auditing.
4. Independently reparsed all 17,658 Q-Chem inputs, regenerated every PySCF
   geometry, checked every per-record hash and role, and confirmed that no
   Q-Chem orbital, `qarchive.h5`, or scratch-orbital directory was used.
5. Preserved 593 embedded orbital-basis blocks, one embedded auxiliary-basis
   block, 97 embedded ECP blocks, and 2,771 BigNC ghost centers across 50
   monomer definitions.
6. Published the passed snapshot with read-only files, a read-only directory,
   `MANIFEST.sha256`, and `IMMUTABLE.json`. The checksum-manifest SHA-256 is
   `c4f2d596a5b779bc6bb25d6fb31a2ab79c285374af6388ec960b1461b40238bb`.

## Explicit boundary and plan update

These are immutable molecular definitions, not yet runnable production jobs.
Step 6 remains mandatory because PySCF aliases and generated basis/ECP blocks
must be translated and validated. In addition, 3,446 energy-role species—all
75 BigNC plus all 3,371 GDB9-W1-F12 species—lack a source RI auxiliary basis.
Step 6 must choose, document, and validate auxiliary bases for those external
sets, including coverage of BigNC ghost centers.

The 2026-08-29 route plan should be updated as follows:

- Steps 1, 3, 4, and 5 are complete; the environment-audit portion of Step 2
  is complete, but a committed version-control baseline is still pending.
- Geometry authority, all-UKS reference policy, constraint profiles, and data
  roles are now resolved; the old four-choice implementation stop is obsolete.
- Step 6 is next and gains the external-set auxiliary-basis decision above.
- Production post-SCF wording should say UMP2 for every species; RMP2 remains
  useful only as a closed-shell cross-check.
- Feasibility/AO-size estimates must be recomputed after Step 6, especially
  for BigNC counterpoise inputs with ghost basis centers.
