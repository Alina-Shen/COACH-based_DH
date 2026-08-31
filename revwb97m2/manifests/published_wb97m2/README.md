# Published omegaB97M(2) R0 comparator

This directory records the Step-11 source audit for the unfitted `R0`
published omegaB97M(2) comparator. The uploaded paper is versioned at
`revwb97m2/wb97m2_paper/ωB97M(2).pdf` and identified by SHA-256
`c631e99b54e70859f55a159e783c2b7cc85a50e2d20d384480add5be52cc4642`.

The paper itself establishes the xDH energy partition, Table-II coefficients
at five-decimal printed precision, two exact coefficient constraints, parent
omegaB97M-V orbitals, omega/VV10 choices, basis and grid policy, and use of
frozen-core RI canonical MP2. `revwb97m2/published_wb97m2.py` implements only
the resulting named-component linear algebra; it does not claim to generate
the published semilocal density components.

That distinction is important. The paper delegates the exact semilocal base
definitions to Section V of its Ref. 31, and it does not provide trusted
molecular/reaction component energies, full coefficient precision, an exact RI
auxiliary-basis identifier, element-specific frozen-core rules, or a reference-
type policy. The current COACH-form R2 kernel uses a deliberately different
same-spin nonlinear value and therefore cannot be substituted for R0.

Run the source/scaffold validator with:

```bash
python revwb97m2/scripts/validate_published_wb97m2.py
```

A passing report means that the uploaded source, printed coefficients,
constraints, and isolated algebra scaffold are internally consistent. It does
not close Step 11; the unresolved authority list in the YAML remains binding.
