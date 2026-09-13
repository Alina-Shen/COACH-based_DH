**AutoAux is an automatically generated auxiliary fitting basis—not new COACH orbitals or a different functional.** Also, **I did not modify `/global/scratch/users/jsliang/COACH3`.**

**What the AutoAux candidate is**

RI-MP2 approximates electron-repulsion integrals using an auxiliary basis. AutoAux constructs such a basis from the orbital-basis functions, aiming to represent their products. This is an established algorithm implemented in PySCF. [Algorithm paper](https://pubs.acs.org/doi/10.1021/acs.jctc.6b01041), [PySCF implementation](https://pyscf.org/_modules/pyscf/df/autoaux.html).

For carbon, I generated it from the exact native `AUG-CC-PCV5Z` basis:

- Orbital basis: unchanged, **181 functions**.
- Approved auxiliary basis: **157 functions**.
- AutoAux candidate: **525 functions**, in 95 shells.
- COACH orbitals, geometry, spin and ω=0.27: unchanged.

It remains a **diagnostic candidate**, not an active input exception.

**Why the approved auxiliary basis failed**

“Failed” means **exceeded our RI-versus-conventional accuracy threshold**, not that Q-Chem crashed or the orbitals were invalid.

The evidence points to insufficient fitting flexibility for this particular orbital-basis/COACH combination: `rimp2-def2-QZVPPD` accompanies the def2 family, while this carbon calculation uses `AUG-CC-PCV5Z`.

| Carbon auxiliary basis | RI − conventional PT2 |
|---|---:|
| Approved def2-QZVPPD fitting basis | −0.092803 kcal/mol |
| aug-cc-pVQZ fitting basis | −0.058960 kcal/mol |
| AutoAux candidate | +0.003729 kcal/mol |

The threshold is **0.015 kcal/mol**. MO preservation and COACH parent/Fock checks pass, and changing only the auxiliary basis substantially improves agreement. That supports the explanation, without proving every discrepancy has the same cause.

**How the other projects handled carbon**

All three retain **`AUG-CC-PCV5Z` / `rimp2-def2-QZVPPD`**. I found no carbon AutoAux exception in the inspected records.

| Project | Actual handling |
|---|---|
| **revwb97m2** | Completed native RI-MP2 stage using `METHOD wB97M(2)`, frozen core, and both OS/SS components. |
| **wb97m_os_rimp2** | Normally terminated; one frozen core orbital; OS coefficient 0.4534, SS coefficient zero. |
| **xyg_os5** | Normally terminated using the auxiliary basis and Laplace OS-MP2; OS coefficient 0.5574, SS coefficient zero. |

Their successful execution **does not demonstrate carbon-specific agreement with conventional MP2**. I found a water conventional/RI comparison in revwb97m2, but not an equivalent carbon comparison in the records inspected.

The distinction matters: our carbon error comprises approximately **−0.1398 kcal/mol SS** and **+0.0470 kcal/mol OS**. The two OS-only methods omit SS. Their different parent orbitals also prevent transferring our numerical error directly to them.

**Where the copied orbitals are**

The preserved imports are under:

```text
/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_import_v1/species/<species>/
```

This contains **14,081 species**, with per-species `import.json` receipts and read-only copied files. Calculations use separate working copies under:

```text
/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/
```

including `step5_native_v2/` and `step6_v1/`.

The import scripts read source files, write destinations, and verify hashes. Permission changes apply only to destination copies. **No source-file edits, deletions, renames or Q-Chem execution inside COACH3 were performed.** This is supported by the import workflow and recorded checks; I have not performed another full source-tree rehash today.

This turn was read-only, so I left project notes and settings unchanged.
