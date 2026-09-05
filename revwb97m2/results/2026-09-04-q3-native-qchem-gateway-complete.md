# Q3 native Q-Chem imported-orbital gateway complete

Date: 2026-09-04

Status: complete; all six native comparisons pass the predeclared gate.

## Frozen scientific contract

Before any molecular result was generated or inspected, the project froze
`q3_native_gateway_v1.yaml` at `2026-09-04T21:40:47-07:00` (SHA-256
`1d277c97489fe0f84ae2494005d93b42b4d6d253513299dae75d68cc9f8068a0`).
The user approved interpreting the requested restricted/unrestricted coverage
as a closed-shell singlet and an open-shell doublet while preserving the
authoritative all-UKS Q-Chem archives. The cases are `h2o_SW49` and
`12_NH2rad_HNBrBDE18`, each on grids `250974`, `99590`, and `75302`.

The comparison was frozen at `rtol=2e-12` and `atol=2e-12` hartree. It requires
both the complete native 96x180 matrix and transposed semantic rows
`(64,154,166)` to agree with an independent Python recomputation on the exact
Q-Chem quadrature inputs. Every run must also read the copied MO archive,
terminate normally, emit exactly one finite delimited block, and leave the
authoritative input and archive hashes unchanged.

## Diagnostic build and independent reference

The Q-Chem libks driver gained an opt-in diagnostic stream controlled by
`QCHEM_DUMP_INTEGRATED_DV_INPUTS`; it operates only when
`QCHEM_PRINT_INTEGRATED_DV` is also enabled. The stream records the quadrature
weight and ten meta-GGA density inputs passed to the native evaluator, refuses
to overwrite an existing file, and is disabled by default. This makes a
same-grid comparison possible without changing the physical density or
substituting a PySCF SCF.

The user-supplied module stack and `make install -j8` recipe rebuilt the current
configuration successfully. A configure rerun was unnecessary because this was
a source-only diagnostic addition to the existing
`./configure gnu openmp relwdeb` tree. The executable hash remained
`0cfc9b426f71e9a7e8fd57990cd09d3241ec458742e319839bd7f05fae571084`;
the installed diagnostic `libks.so` hash is
`95441cef4e010a334ffa9e73f5342c10ad639471c17d33ab0c6f7295fad39081`,
with zero unresolved dynamic dependencies. The complete build record is
`q3_diagnostic_build_v1.yaml`.

`qchem_integrated_dv_reference.py` independently evaluates all 96x180 entries
from the dumped weights and density variables. The maintained series helper
was extended to evaluate the Chebyshev family needed by the full reference.
Before the molecular gateway, a synthetic full-matrix comparison had maximum
absolute error `6.661338147750939e-16` hartree, and an archive-read H2
diagnostic smoke had maximum absolute error `3.3306690738754696e-16` hartree.

## Native gateway results

The six cases ran as Slurm array `25560893` on `lr8` with 8 CPUs and 16 GB per
task. Each exited `0:0`; elapsed times were 12–36 seconds and batch peak RSS was
approximately 740–790 MiB. The heavy, restart-safe run root occupies 486 MiB.

| Species / role | Grid | Points | Batches | Full max abs (Eh) | Selected max abs (Eh) | Elapsed |
|---|---:|---:|---:|---:|---:|---:|
| `h2o_SW49`, closed-shell singlet UKS | 250974 | 603,880 | 620 | 2.665e-15 | 1.776e-15 | 31 s |
| `h2o_SW49`, closed-shell singlet UKS | 99590 | 145,140 | 246 | 3.553e-15 | 1.776e-15 | 16 s |
| `h2o_SW49`, closed-shell singlet UKS | 75302 | 56,776 | 188 | 2.665e-15 | 8.882e-16 | 12 s |
| `12_NH2rad_HNBrBDE18`, open-shell doublet UKS | 250974 | 598,036 | 614 | 2.665e-15 | 1.776e-15 | 36 s |
| `12_NH2rad_HNBrBDE18`, open-shell doublet UKS | 99590 | 143,960 | 244 | 2.220e-15 | 1.776e-15 | 21 s |
| `12_NH2rad_HNBrBDE18`, open-shell doublet UKS | 75302 | 56,172 | 186 | 1.776e-15 | 1.776e-15 | 16 s |

All full and selected comparisons pass the frozen combined relative/absolute
tolerance. The maximum absolute disagreement across the gateway is
`3.552713678800501e-15` hartree, more than 500 times smaller than the absolute
tolerance. Scaled relative errors can be larger than `rtol` near zero, as
expected; acceptance is the predeclared NumPy `allclose` combined criterion,
and every matrix passed it.

## Execution and validation controls

The preparation script checks hashes and copies each complete orbital scratch
tree into a new non-overwriting case directory. Derived inputs preserve
`wB97M-V`, basis, charge, multiplicity, and `UNRESTRICTED TRUE`, while setting
`SCF_GUESS READ`, `MAX_SCF_CYCLES 0`, `GEN_SCFMAN FALSE`, `XC_FXC 3`, and the
requested grid. The per-case validator writes full native/reference matrices,
selected rows, hashes, and a pass marker only after every check succeeds.
The aggregate validator independently rechecks all six reports, the frozen
manifest, build hashes, live libks diff, role/grid coverage, and unchanged
authoritative input/archive hashes.

The first corrected array, `25560294`, was canceled before any task started
because its `cm1` target was blocked by three multi-hour jobs stuck in
`COMPLETING`. A live `sbatch --test-only` comparison predicted immediate `lr8`
capacity; only partition/account/QOS were changed to
`lr8/lr_mhg2/mhg2_lr8_normal`, with memory and all scientific settings
unchanged. Array `25560893` then started immediately. An earlier pending array
`25560224` had also been canceled before execution after detecting that the
full build-time module stack produced nonfatal Lmod dependency notices that
would become fatal under the runtime script's `set -e`; the runtime was
corrected to the verified minimal linked-library module set before submission.

The aggregate record `q3_validation_v1.json` has SHA-256
`5f5fdf132e307a4691d6d2246c5ee97df59c0e1292cf359952ab6073c681c50e`
and reports `status: passed`, with all 16 aggregate checks true. Repository
validation totals 31 passing tests. Q3 is complete. Q4—production-grade parsing,
atomic publication, and restart/refusal tests—is the next gate; no bulk
production is authorized.

