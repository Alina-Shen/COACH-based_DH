# Step 7 integratedDV kernel validation

The production feature kernel is
[`../../integrated_dv.py`](../../integrated_dv.py). It applies the COACH
integratedDV construction protocol to fixed omegaB97M-V spin densities and
returns only the three frozen rows needed by the new omegaB97M(2)-form fit:

- row 64: short-range exchange with nonuniform scaling, monomial `u_x` and
  Legendre `beta_f`;
- row 154: SCAN-alpha=1 same-spin correlation with the `2 beta` correction,
  monomial `u_ss` and Legendre `beta_f`;
- row 166: SCAN-alpha=1 opposite-spin correlation, Legendre `u_os` and
  Legendre `w`.

The frozen nonlinear values are `gamma_x=0.004`, `gamma_ss=0.01`, and
`gamma_os=0.006`. The output shape is `3 x 96`, which is flattened to the 288
semilocal columns of the 292-feature fitting model. The kernel contains no
published COACH coefficients: its purpose is to construct a basis in which a
new functional is fitted.

Run the independent validation with the pinned project environment:

```bash
/global/home/users/yaoshen/.conda/envs/coach/bin/python \
  revwb97m2/scripts/validate_integrated_dv.py
```

The validator checks row decoding, nonlinear parameters, independent
polynomial-coordinate identities, alpha/beta symmetry, grid-block partition
invariance, zero-density handling, agreement with the maintained upstream
protocol where its nonlinear parameters agree, and a required negative
regression against upstream `gamma_ss=0.2`. Results are stored in
[`validation.json`](validation.json).
