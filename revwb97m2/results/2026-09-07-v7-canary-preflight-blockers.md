# Canary checkpoint tests pass; freeze blocked before submission

Verified clean user checkpoint b8736a7. Full committed suite:110 passed in6.49s.
Scientific configuration and launcher bash syntax checks passed. No code edits.

The first seven-case freeze failed at MOR16_ed33 with inventory electron/spin
mismatch. Direct Cartesian nuclear count is228 electrons; inventory reports200.
The firstsix cases' computed counts/spins agree with their inventory records.
No frozen manifest or new canary output root was published, and no orbital
copies, native calculations, Slurm submissions, rebuild, commit or push occurred.

## Root cause and correction to prior notes

`manifests/basis_bridge/resolved_basis_records.csv` explicitly records for
MOR16_ed33: `ecp_resolution=implicit_named_def2_ecp`,28 ECP electrons,
200 explicit electrons, and a hash-pinned ECP definition. Source input uses
Ru with BASIS DEF2-QZVPP, without an explicit $ecp block. Consequently the
inventory's has_ecp=false is not sufficient to establish all-electron chemistry.
The earlier plan/handoff description of allseven as no-ECP was incorrect.
The current driver is deliberately all-electron-only and fails closed as intended;
this is incomplete canary coverage, not grounds to ignore the electron mismatch.

Recommended next implementation, for user confirmation: retain the approved
MOR16_ed33 canary and extend the new driver to join/hash-pin the validated basis
bridge (species/source/basis/ECP identities). Use200 explicit electrons in
Q-Chem output checks, verify228=200+28, preserve the original implicit ECP/basis,
and add regression tests for implicit ECP identity and mismatch rejection.
Do not replace the molecule, disable validation or subtract28 by an ad hoc rule.
No new SCF or change to the scientific functional is required.

## Storage preflight

df reports2.5PiB available on the shared mount; this is NOT user/project quota.
The initial quota query reported RPC connection refusal. An escalated targeted
mount query returned no usable quota, and a further explicit-user attempt was
rejected by this quota CLI's argument handling; quota remains unverified.
No working project-quota reporting command was discovered.

Read-only du -sb measured source trees (apparent bytes, including directory
metadata; not a full data hash or exact allocated-block measure):

| Species | Bytes |
|---|---:|
| TMD01_H | 54236874 |
| S22_06b | 199762478 |
| HR46_N-methylacetamide | 279953527 |
| HR46_toluene | 422930565 |
| 3019_41UracilPentane090_dim_S66x8 | 660237821 |
| BSR36_c4 | 980989351 |
| MOR16_ed33 | 1762148278 |

Approximately4.1GiB source trees and24.3GiB planned retained stage copies
(five copies for H, six otherwise), excluding new Q-Chem scratch and failures.
Ask user for usable project quota/headroom or the cluster-specific command;
do not infer ample user quota from shared filesystem free space.

Next gate: confirm implicit-ECP support and storage information, implement/test
the fix with explicit provenance, then freeze/preflight again. Globaltwojobcap
remains removed; memory allocations and large-case review remain unchanged.
