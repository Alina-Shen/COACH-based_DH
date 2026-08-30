# 2026-08-29 reproducible code/environment baseline

## Outcome

The existing `coach` Conda environment was already complete, so it was
preserved and audited instead of being deleted or rebuilt. It is suitable as
the pinned pilot environment. Exact Conda builds, the complete pip dependency
closure, readable direct dependencies, installed-distribution hashes, the Git
source commit, and validation results are recorded in
`revwb97m2/environment/baseline.json`.

The environment is healthy, but the upstream FunctionalCOACH regression suite
is not fully green: three of four tests pass. The carbon AE18 regression fails
inside the COACH SCF/DIIS path after invalid scaling values produce NaNs. This
is recorded as a code-level baseline failure and was not altered as part of
environment setup.

## Actions and descriptions

1. Loaded `miniconda3/22.11.1-gcc-11.4.0` and audited the existing
   `/global/home/users/yaoshen/.conda/envs/coach` environment.
2. Confirmed the source baseline at Git commit
   `4a7cddd52acddf08d65806d636a6da0d93315311`. At capture time that commit was
   not contained in the local `origin/main` tracking ref.
3. Captured a readable exact-version environment specification in
   `environment.yml`, exact Linux Conda build URLs in
   `conda-linux-64.explicit.txt`, and the complete pip dependency closure in
   `pip-linux-64.lock.txt`.
4. Recorded SHA-256 hashes for the three lock artifacts and the installed
   distributions' `RECORD` manifests in `baseline.json`.
5. Kept `coach-workflow==0.1.0` as an editable install from this checkout and
   added a validator that rejects a different project root or dependency set.
6. Verified Python 3.11.15, PySCF 2.14.0, LibXC 7.0.0, NumPy 2.4.6, SciPy
   1.17.1, pandas 3.0.5, dftd4 4.2.0, basis-set-exchange 0.12, PyYAML 6.0.3,
   pytest 9.1.1, h5py 3.16.0, and gurobipy 13.0.3.
7. Ran `pip check` and imported every required package successfully.
8. Verified the Gurobi restricted non-production license by solving a real
   bounded optimization problem; the license expires 2027-11-29.
9. Confirmed `environment.yml` resolves successfully with a clean Conda
   environment-creation dry run. This did not create or modify an environment.
10. Passed the v3 scientific-specification validator and revalidated copied
    versions of the stored 291-feature H2O smoke and synthetic reaction smoke.
11. Ran all four upstream FunctionalCOACH regressions: the two H2O cases and
    the D4 case pass; `test_16_c_ae18_matches_qchem` fails after 3 passes.

## Reproduction and verification

See `revwb97m2/environment/README.md`. The exact Linux lock is the strictest
reproduction route; `environment.yml` is the readable maintenance interface.
The editable repository package is installed separately so its source identity
remains tied to Git rather than being hidden in a wheel lock.
