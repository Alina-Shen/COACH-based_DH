# Step 9 Q-Chem same-archive scalar features complete

Step 9 now has a production-facing Q-Chem route for feature columns 288–291.
It reuses an isolated, hash-verified copy of each authoritative omegaB97M-V
`qarchive.h5` and performs no iterative SCF or orbital optimization.

## Evaluation design

- The SR-HF/VV10 job uses `SCF_GUESS READ`, `MAX_SCF_CYCLES 0`, and
  `MP2_RESTART_NO_SCF TRUE`. `SRC_DFT TRUE`, `HF_SR 1000`, `HF_LR 0`, and
  `OMEGA 300` isolate unscaled erfc short-range HF. Unit-scaled VV10 uses
  `NL_VV_B 1000`, `NL_VV_C 100`, `NL_VV_SCALE 100000`, and `NL_GRID 1`.
- The RI-MP2 job reads the same copied archive and uses Q-Chem's native
  `METHOD wB97M(2)` plus `DH_PT2_ENGINE RIMP2`. This retains the imported
  wB97M-V parent Fock/orbital-energy definition. The common printed spin scale
  `0.34096` is removed; column 290 is unscaled same-spin plus opposite-spin
  canonical doubles. Non-Brillouin singles are excluded and recorded.
- D4-ATM is evaluated from authoritative geometry and charge with the frozen
  COACH parameters `s6=0,s8=0,s9=1,a1=0.215,a2=5.8,alp=16`.

## Diagnostic correction

Job `25612738` showed that generic `EXCHANGE HF`/`CORRELATION RIMP2` gives the
correct SR-HF and VV10 but rebuilds an HF Fock operator for PT2. That PT2 result
was rejected and never published. The frozen v3 split route corrected the
definition without changing or rebuilding Q-Chem.

## Gateway evidence

Job array `25613167` completed both closed-shell-singlet UKS and open-shell-
doublet UKS cases in 22 seconds each at about 696 MiB peak RSS. Both outputs
normally terminated and together showed four MO-archive reads per case. The
authoritative trees were unchanged, pre-run copies were identical, and copied
and source `qarchive.h5` hashes remained identical after execution.

Maximum absolute Q-Chem/PySCF fallback differences were `5.7621e-8 Eh` for
SR-HF, `1.9362e-8 Eh` for VV10, and `3.8152e-8 Eh` for total RI-MP2. These pass
the frozen `2e-6`, `2e-6`, and `2.3904e-5 Eh` gates, respectively. Both PT2
spin-component identities and scaled-output identities close to printed
precision.

The strict publisher creates a finite four-value vector in column order
`[SR-HF,VV10,total PT2,D4-ATM]`, records Q-Chem/input/output/archive hashes,
and publishes by atomic non-overwriting directory rename. Aggregate validation
is `passed` in `step9_qchem_validation_v3.json`.
