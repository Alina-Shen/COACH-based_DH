# Published omegaB97M(2) R0 comparator

This directory records the Step-11 authority and validation audit for the
unfitted `R0` published omegaB97M(2) comparator. Version 1 preserves the
initial paper-only blocked state; version 2 is the completed record.

The uploaded omegaB97M-V paper and SI provide the exact semilocal definitions
and nonlinear parameters. `revwb97m2/published_wb97m2.py` now implements the
13 selected Table-II density features as well as the fixed/scalar assembly.

The R0 same-spin nonlinear value is `0.2`; the COACH-form R2 value remains
`0.01` and is not modified. Native Q-Chem comparisons validate a matched H2O
energy and the H2 dissociation reaction well inside the declared tolerances.

[`comparison_schemas_v1.yaml`](comparison_schemas_v1.yaml) freezes the three
pre-fit comparison roles. `R0` is the published unfitted comparator, `R1`
applies the COACH workflow to the paper's original 78-feature candidate family
(`N'=N=4`, 75 semilocal plus three scalar terms), and `R2` applies the same
workflow to the frozen 291-feature integratedDV representation. Thus `R1-R0`
measures the workflow effect and `R2-R1` measures representation expansion.

Run the source/scaffold validator with:

```bash
python revwb97m2/scripts/validate_published_wb97m2.py
```

A passing report validates the hashes, coefficients, model isolation, matched
molecular and reaction records, and completed Step-11 gate in version 2.
