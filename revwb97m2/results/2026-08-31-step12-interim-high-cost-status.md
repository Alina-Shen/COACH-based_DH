# Step 12 interim high-cost measurement

Status refreshed 2026-08-31 at approximately 20:17 America/Los_Angeles.

- Job `25431773` remains `RUNNING` on `mhg`, node `n0040.mhg0`, with 16 CPUs,
  240 GiB requested memory, runtime `06:26:27`, and its original 12-hour limit.
- Live `sstat` counters: average CPU `4-02:12:52`, average RSS `5,505,040K`,
  maximum RSS `7,837,968K`, disk read `109,069,285`, and disk write
  `176,115,977` (Slurm-reported units).
- Stdout has reached SCF cycle 5, most recently at `-905.769171 Eh` with RMS
  gradient about `12.6`; the energies remain strongly oscillatory and far from
  convergence. Five overlap eigenvectors were removed. The counters and new
  SCF cycles show that the job is active rather than scheduler-stalled, but
  SCF convergence and time-to-solution are now the measured dominant risks.
- Decision: Step 12 may formally proceed because the measurement is valid
  evidence. Step 12 cannot close, no upper-tail production extrapolation is
  defensible, and no production submission is authorized until this job
  terminates or reaches its declared stop and its terminal artifacts are
  summarized.
- The live job was observed read-only and was not modified.
- No additional large benchmark was submitted: duplicating the same upper-tail
  question before this run reaches a terminal state would not improve the
  resource decision.
