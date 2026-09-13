# Step 5 progress — 2026-09-12

Step 5 is **in progress, not complete**. Solver selection is unnecessary. Omega
remains 0.27; no new SCF, quantum jobs, fitting or solver use occurred.

## Work performed and explanation

1. Read the frozen Step 5 exit criterion and Step 4 authority. Inspected the
   revwb97m2 immutable-copy implementation and XYG-OS5 working input. Pinned
   representative reference hashes/settings in `step5_settings_reference.json`.
   Retained the validated COACH no-update controls; XYG-OS5's 200-cycle allowance
   and method/grid are not adopted as COACH execution settings.
2. Inventoried all 17,452 energy-role species against both supplied source roots.
   14,081 directories are present: 14,006 core/auxiliary and 75 BigNC. All 3,371
   GDB9-W1-F12 species lack a directory in either supplied source tree. No fallback
   to another functional or new orbital generation was attempted.
3. Checked charge, multiplicity, atom/ghost identity and coordinates (absolute
   tolerance 1e-10 Angstrom), legacy AO/MO dimensions from 819.0, MO/density/Fock
   file lengths and flat-file sizes. 14,077 pass structurally; four are quarantined.
   Inventory is `../manifests/step5_inventory_v1.csv`; summary is
   `step5_inventory_v1.json`. Available top-level files total 805,644,039,802 bytes.
4. Quarantined ISOL24_i8e: source has 1,884 AOs, frozen authority requires 2,085.
   Asked user for a compatible replacement. Quarantined He3_47/48/49: dimensions
   315 AOs/314 MOs but 53.0 contains 5,056 extra bytes (square-sized allocation).
   Both occupied densities reconstruct from the packed reduced layout within
   roundoff; interpreting the beta block as square fails. Current GuessMan.C
   lines 801–822 warns on length mismatch and reads packed offsets. This does
   not validate the virtual spectrum or justify modifying/truncating the source;
   a native no-update read check remains necessary before clearing these cases.
5. Independently checked finite MO/density data and occupied-MO density closure
   for carbon, water, Yb, one helium entry and BigNC L14_2a. All five pass the
   Step 2 normwise roundoff bound. L14_2a has 2,724 AOs/2,662 MOs. Source hashes
   are retained in `step5_sample_numerics.json`; this is a five-species diagnostic.
6. Inspected a populated BigNC HDF5 schema, including two spin sets and reduced
   orbital rank. Empty HDF5 files in core sources are not automatically rejected:
   the user-authorized legacy route remains authoritative. Full basis identity,
   AO ordering and full-domain numerical checks remain pending, despite matching
   dimensions. Historical generating build/method outputs remain unavailable.
7. Implemented and started a resumable import of the 14,077 structurally eligible
   records into `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_import_v1`.
   Each file is hashed while reading source bytes, checked by destination readback,
   and checked for source size/mtime changes during copying. Per-species directories
   publish by rename after validation; files are made read-only. Resume rechecks
   source and destination hashes. Top-level parent files are preserved; nested
   fragment directories are excluded and named in each import record. Runtime
   scratch will use separate copies. Imports are labelled structural-only, with
   numerical and full basis validation pending. The copy is still running;
   `step5_import_v1.log` and `python3 -B coach_mp2/scripts/step5_status.py` report
   progress. No entire-domain completion marker is issued.
8. Added six tests covering ghost/invalid geometry, reduced-rank dimensions,
   mismatches/truncation, geometry displacement, copy/resume integrity, corruption,
   source preservation and unsafe paths. All pass (`step5_tests.log`).
9. Recorded coverage by scientific role: all 2,799 fitting and 249 diagnostic
   species pass structurally; four model-selection species are quarantined;
   3,371 final-assessment species are missing. Roles overlap and must not be summed.
10. Updated the mutable progress record, code/heavy-data READMEs, live plan table
    and a dated project-note chapter. Step IDs and earlier frozen artifacts remain
    unchanged. All writes are in the authorized project roots or project notes.

## Remaining gates and user help

- Supply the GDB9-W1-F12 COACH archive root or decide explicitly how that final
  assessment will be staged; it is not silently dropped.
- Supply a compatible ISOL24_i8e archive, or decide how to resolve its source-basis
  discrepancy. No replacement SCF is authorized.
- Finish and audit the available-copy campaign, then establish full basis/archive
  compatibility and resolve the three He3 native-read cases. Matching dimensions
  and file hashes alone do not establish production readiness.
- Pause before backend-dependent work if solver selection remains unresolved.

The first inventory run preceded a parser hardening that explicitly rejects NaN
coordinates and malformed molecule lines. Six tests cover the hardened code;
this does not constitute a rerun of all 17,452 records with that revision. A final
inventory rerun is required before declaring Step 5 complete.

## User update — GDB9 deferral and quarantine investigation

The user has no replacement archives for the four quarantined cases. GDB9-W1-F12 COACH orbitals are explicitly a future TODO for Step 17 final assessment, after Step 16 model freeze; they do not block current development. The frozen role membership is retained. Before assessment, obtain/generate orbitals and finish their deferred import, feature and assembly gates. No new SCF is authorized now. See `../configs/step5_gdb9_deferral_v1.json`.

Compared all four XYG-OS5 inputs/outputs. He3 basis/geometry are unchanged; all three XYG-OS5 outputs have the same length warning and terminate normally. Native COACH no-update job 25826223 tests isolated copies. ISOL24_i8e requires 2,085 AOs in both input sets, whereas the COACH source has 1,884, matching non-diffuse def2-QZVPP/QZVP counts. Generating basis identity is inferred, not proven. See `step5_quarantine_investigation.json`.

Native He3 update: completed He3_47 reads normally and preserves orbital energies/density, but fails the strict MO byte-invariance gate. Source scfman.C calls post-SCF orimo even on the no-update path; oriorb.F reorients degenerate MOs and writes coefficients. This is consistent with 34 changed columns per spin (maximum difference after sign alignment about 1.75e-9). Keep quarantine and the strict contract; investigate a project-local bypass or pre-postprocessing extraction. Native job 25826223 continues for the other cases. Source archives are unchanged.

All three He3 native tests have now finished. Source/output density closure and unchanged orbital-energy bytes pass; strict MO bytes fail in every case (34/30/22 changed columns per spin, maximum sign-aligned coefficient differences 1.75e-9/2.02e-9/8.42e-9). Job 25826223 evidence is in step5_he3_native_validation.json and step5_he3_orientation.json. Keep quarantine pending a post-SCF orientation bypass or validated pre-postprocessing extraction; no new He3 SCF is indicated.
