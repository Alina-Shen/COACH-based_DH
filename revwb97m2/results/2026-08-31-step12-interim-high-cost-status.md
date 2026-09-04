# Step 12 interim high-cost measurement

Initial status was refreshed 2026-08-31 at approximately 20:17
America/Los_Angeles and updated after the declared stop on 2026-09-01.

- Job `25431773` reached `TIMEOUT` at `12:00:01`; Slurm cancelled its batch
  step at the original 12-hour limit. It used `mhg`, node `n0040.mhg0`, 16
  CPUs, and 240 GiB requested memory. The job was never modified.
- Terminal accounting reports `MaxRSS=8,119,928K`, disk read `104.05M`, and
  disk write `335.88M` (Slurm-reported units).
- The parent omegaB97M-V SCF did not converge. It completed ten cycles; energy
  still oscillated widely and cycle 10 had RMS gradient `0.885` and density-
  matrix change `13.8`. No parent completion marker, semilocal features, or
  scalar features were produced.
- Interpretation: this is a clean declared-stop measurement, not a memory
  failure. The upper-tail obstacle is parent-SCF wall time/convergence under
  the current initial guess and algorithm, despite peak RSS of only about
  7.74 GiB against the 240 GiB request.
- Decision: Step 12 may formally proceed and now has its high-cost terminal
  evidence. Step 12 still cannot close, and production remains unauthorized,
  until the role-minimal population is stratified, total CPU/storage/retry
  costs are extrapolated, a validated upper-tail policy is selected, and the
  user signs off.
