# Step 6 PySCF basis bridge

This layer turns the immutable Step-5 Q-Chem input metadata into runnable
PySCF orbital-basis, RI auxiliary-basis, and ECP definitions. It translates
text and labels only; Q-Chem orbitals and `qarchive.h5` remain prohibited.

The bridge preserves embedded Gaussian basis blocks and Gaussian ECP blocks,
maps every observed named label explicitly, and assigns explicit MP2-fit
auxiliary aliases to the 3,652 inputs whose sources provide no auxiliary
basis. The latter comprise 75 BigNC, 3,371 GDB9-W1-F12, and 206 OPT inputs.

`AE11_Yb` preserves the exact all-electron orbital and uncontracted auxiliary
blocks used in the successful prior Q-Chem RI-MP2 calculation. It is not
replaced by a generic basis lookup.

Build and independently validate in the pinned `coach` environment:

```bash
python revwb97m2/scripts/build_basis_bridge.py
python revwb97m2/scripts/validate_basis_bridge.py
```

The generated CSV is a lightweight per-record resolution and dimension index.
Production drivers should load the immutable Step-5 JSONL record and call
`pyscf_basis_bridge.build_molecules`; the CSV is for audit and fast lookup.
