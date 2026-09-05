# Q2 Q-Chem build and integratedDV capability complete

Date: 2026-09-04

Status: Q2 complete; Q3 ready for tolerance freeze and the restricted plus
unrestricted three-grid comparison.

## Final source and build identity

- Q-Chem trunk revision: `48798`; libks external revision: `1666`.
- Complete five-file libks diff SHA-256:
  `a7d9660e8fccc293691639cab38c4fe29a1496b1974383aa46ade92ba9eb92c3`.
- The final dispatcher correction is in `libks/qchem/ks_main.C`; the temporary
  `fock_xc.C` experiment was restored exactly to SVN pristine content.
- The user-supplied module stack was loaded and the existing GNU 10.5/OpenMP
  relwithdebinfo configuration was rebuilt from `build` with
  `make install -j8`. Configure was not rerun because the final change did not
  alter CMake configuration. Build and install returned zero.
- Executable SHA-256:
  `0cfc9b426f71e9a7e8fd57990cd09d3241ec458742e319839bd7f05fae571084`.
- Installed `libks.so` SHA-256:
  `36a8f41a10d7541c25731be398ae270814dde7c5f23d2aeea52a6023e3b629a7`.
- The executable has 165 `ldd` output entries and zero unresolved
  dependencies.

## Runtime diagnosis and contract

The default legacy XC Fock path does not dispatch into libks. Fixed-orbital
integratedDV feature inputs therefore require `XC_FXC 3`, which selects the
libks XC Fock engine. This is an implementation selector: it does not change
the requested omegaB97M-V functional or imported orbital density.

When `QCHEM_PRINT_INTEGRATED_DV=1` is present, the libks Fock dispatcher now
invokes the isolated energy driver after a successful Fock evaluation. With
the environment variable absent, the additional evaluation and output are not
requested.

## Archive-read capability probe

An unrestricted H2/STO-3G wB97M-V probe used `SCF_GUESS READ`,
`MAX_SCF_CYCLES 0`, `GEN_SCFMAN FALSE`, and `XC_FXC 3`. The launcher explicitly
selected the new trunk executable (with inherited `QCPROG` unset). The output:

- reported two MO-coefficient reads;
- contained exactly one begin marker, one `integratedDV` label, and one end
  marker;
- contained 96 data rows with exactly 180 numeric, finite values per row; and
- reached normal Q-Chem termination.

Input SHA-256:
`9eb96f6f21d685b025e16c77d53b0a25e61e313cefc6790217b03dd273460816`.
Output SHA-256:
`ef2024c15267f821420d4f891763d02f9d1ea2b10277b16136ae24a437a5e757`.

This is the Q2 executable-capability gate only. It is not the Q3 scientific
comparison: before inspecting Q3 results, freeze tolerances and then run at
least one restricted and one unrestricted imported-orbital case on all three
production feature grids, including full-matrix and selected-row parity.
