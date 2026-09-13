# ISOL24_i8e — reference-project handling

Date: 2026-09-12. Read-only investigation; no quantum calculations or source modifications.

All three current protocols require def2-QZVPPD (2,085 AOs) and RIMP2-def2-QZVPPD auxiliary basis (4,819 functions). Their behavior does not support using the smaller COACH archive unchanged.

| Project | Actual evidence | Handling |
| --- | --- | --- |
| wb97m_os_rimp2 | METHOD wb97m(os), DH_PT2_ENGINE RIMP2; printed parent wB97M-V, omega 0.3, SR HF 0.15. SCF converges in 15 cycles to -941.7730454277 Eh, then RI-MP2 and normal termination. | SCF_GUESS READ initializes a genuine correct-basis SCF; it does not freeze the guess. Current scratch has 2,085 AOs / 2,053 MOs. |
| xyg_os5 | METHOD XYG-OS5; printed parent exchange/correlation are B3LYP (0.20 HF, 0.08 Slater, 0.72 B88; 0.19 VWN1RPA, 0.81 LYP). Three SCF cycles converge to -942.1987557866 Eh, followed by the DH calculation and normal termination. | Also READ plus allowed orbital optimization in the correct basis. Current scratch has 2,085 AOs / 2,053 MOs. A commented copy command mentions xygj_os; this is not proof it was executed. |
| revwb97m2 | Current versioned Q-Chem orbital authority selects `/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2`; species/basis manifests specify 2,085 AOs. | Reuses the compatible-basis wB97M-V source under its fixed-orbital policy. This establishes source selection, not completion of a species-specific revwb97m2 feature job. Earlier PySCF-parent or original shared-archive policies are historical, not the current production authority. |

The quoted energies are parent SCF energies, not final double-hybrid totals.

Both benchmark inputs use MEM_TOTAL 120000, MEM_STATIC 3000, GDM, SCF_CONVERGENCE 7, MAX_SCF_CYCLES 200, UKS, SCF_GUESS READ and XC_GRID 99x590. SCF_GUESS_MIX/internal-stability lines are commented out. Neither successful output reports the saved-MO dimension warning. These settings differ materially from COACH's zero-update production contract.

Current archive headers show:

| Source | AOs | Retained MOs |
| --- | ---: | ---: |
| Shared original COACH3 | 1,884 | 1,884 |
| Shared original wB97M-V | 1,884 | 1,884 |
| Current wb97m_os_rimp2 scratch | 2,085 | 2,053 |
| Current xyg_os5 scratch | 2,085 | 2,053 |

The legacy MO files in the latter two match 2,053 retained orbitals in 2,085 AOs. The inspected HDF5 files are 800-byte containers; do not infer populated HDF5 content or native feature readiness merely from their existence. The dimension comparison here uses legacy 819.0/53.0.

**Provenance limit:** available successful outputs do not establish who originally supplied their read guesses, or whether an earlier job regenerated/projected/replaced the shared 1,884-AO source. Therefore, do not describe these jobs as proven automatic repairs of that archive. The original wB97M-V archive having the same smaller count as COACH is a shared source-history issue, not a reason to relax the basis authority.

**COACH implication:** preserve the 2,085-AO authority. The closest analogue is eventually obtaining or generating COACH orbitals in that basis, using any suitable guess only as an initialization under an explicitly authorized SCF. Directly replacing COACH orbitals with wB97M-V/B3LYP orbitals, silently changing basis, or zero-padding the missing virtual space would change the intended comparison. No new COACH SCF or basis exception was authorized in this investigation.

Machine-readable evidence and source hashes: [comparison JSON](./step5_isol24_reference_comparison.json).
