# Frozen scientific specification, version 2

The authoritative machine-readable specification is
[`../configs/scientific_spec.yaml`](../configs/scientific_spec.yaml). This
document records the rationale and the boundary between frozen science and
implementation checks.

## Frozen model

The primary model is a non-self-consistent double hybrid evaluated on fixed
ωB97M-V orbitals. It follows the authoritative GSCDB per-species orbital-basis
assignments, uses full long-range HF exchange, \(\omega=0.3\), VV10 with
\(b=10\) and \(C=0.01\), and frozen-core canonical RI-MP2. Total PT2 is fitted;
same- and opposite-spin PT2 are retained only as diagnostics.

## Version 2 basis-policy amendment

Version 1 incorrectly assumed a uniform def2-QZVPPD orbital basis. Version 2
supersedes that choice and pins every core species to the `basis` field in the
authoritative GSCDB137 species manifest: 13,907 species across 14 basis labels,
including 8,276 def2-QZVPPD cases. The exact distribution is frozen in the
machine-readable specification.

Q-Chem sometimes realizes a named GSCDB basis through `BASIS GEN` or
`BASIS GENERAL` plus an explicit `$basis` block. Those generated blocks are
part of the scientific input and must be preserved. The RI auxiliary-basis
policy likewise preserves each input's `AUX_BASIS_CORR` value and any
`$aux_basis` block; the Q-Chem input is authoritative if the advisory GSCDB
metadata is incomplete. BigNC remains a separate external evaluation set and
is not included in training.

The exact version-1 file is archived at
[`../configs/archive/scientific_spec.v1.yaml`](../configs/archive/scientific_spec.v1.yaml).

The fixed energy is

\[
E_{\mathrm{fixed}} = E_{\mathrm{nuc}} + E_{\mathrm{one}} + E_J
                   + E_x^{\mathrm{LR-HF}}.
\]

The 291 fitted features are 96 exchange, 96 same-spin correlation, 96
opposite-spin correlation, SR-HF, VV10, and total PT2.

## Frozen COACH semilocal forms

| Channel | Base and correction | Variables and expansion | integratedDV row |
| --- | --- | --- | ---: |
| Exchange | spin-resolved UEG × SR attenuation × nonuniform scaling | monomials in \(u_x\), Legendre in \(v=2\beta-1\) | 64 |
| Same-spin correlation | SCAN \(\alpha=1\) same-spin × \(2\beta\) SCC | monomials in \(u_{c,ss}\), Legendre in \(v\) | 154 |
| Opposite-spin correlation | SCAN \(\alpha=1\) opposite-spin | Legendre in \(u_{c,os}\) and \(w\) | 166 |

The nonlinear compression parameters are \(\gamma_x=0.004\),
\(\gamma_{c,ss}=0.01\), and \(\gamma_{c,os}=0.006\).

## Row-153/154 decision

The accepted H₂O and synthetic-reaction smoke artifacts used rows
`(64,153,166)`. They remain valid tests of calculation plumbing, feature
width, grid differences, stoichiometry, and `Nofit` algebra.

The final COACH documentation specifies Legendre polynomials in the same-spin
\(v\) variable. Under the maintained integratedDV mapping this is row 154;
row 153 uses monomials in \(v\). Since polynomial-family choice changes MIO
sparsity and coefficient-bound behavior, version 2 retains the semantic Legendre form and
therefore row 154. A direct equivalence test against the final COACH kernel is
a mandatory gateway before pilot or production calculations.

## Constraint policy

The first real fit compares:

- `C0_minimal_critical`: UEG exchange normalization, SR-HF in `[0,1]`,
  mandatory SR-HF and PT2, and the numerical coefficient bound of ±25.
- `C1_nonlocal_sum`: C0 plus \(c_{\mathrm{PT2}}+c_{\mathrm{VV10}}=1\).

The one-electron exchange limit and sampled exchange/correlation bounds are
disabled initially. They may be added only after a dense-domain audit finds a
specific pathology or as a predefined comparison. Grid sensitivity remains a
separate numerical second pass at 0.015 kcal/mol.

## Frozen versus gated

The functional definition above is frozen. The following are implementation
gates, not open scientific choices:

1. prove that semantic rows `(64,154,166)` reproduce the intended kernels;
2. validate Q-Chem `WB97M(OS)` scratch semantics for closed- and open-shell cases;
3. preserve and verify every per-species orbital basis, RI auxiliary basis,
   and generated Q-Chem basis block;
4. adopt an explicit GSCDB137 training-weight configuration;
5. reproduce trusted published ωB97M(2) component and reaction energies.

Changing the functional form, nonlinear parameters, fitted energy partition,
or constraint-profile definitions requires specification version 3 and a new
decision record.
