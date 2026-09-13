# Step 5 continuation — 2026-09-12

All 14,081 imports and six native evaluations finished. Corrected v4 audit
25828892 is the final numerical gate; see the completion report after publication.

The v3 audit passed MO-byte, density and overlap checks but incorrectly added
printed D4 to the SCF-cycle component sum. The seven printed terms already close
against that native SCF energy. V4 records D4 separately without relaxing any
tolerance or rerunning Q-Chem. The failed v3 report remains as historical evidence.
The earlier live-source audit stalled on external storage and was cancelled;
v4 verifies immutable imports against their receipts and staging source hashes.

Six input/copy tests and two corrected energy-bookkeeping tests pass.

- [Current native audit](./step5_native_v4_validation.json)
- [Complete work list](./step5_complete.md)
- [Import audit](./step5_import_audit.json)
