# Discovery extension launched; original K14 candidates accepted for reuse

- Verified clean commit4784dc6d367bc81260a248f2d11c1c1437342564. Full411tests
  PASS16.29s; authorized release verifies committed plan/code/test hashes.
- Initially the original twoK14fits were still running. Verified their exact
  starts/task identities and scientific input provenance; no duplicateK14tasks
  in the124taskextension. They completed during this turn; fresh independent
  `audit_task` passed for BOTH, including publications, original/noisy starts,
  coefficients/support/scalars/objective and finite consistent gaps.
- K14repeat0 objective1.8895116276892168,gap0.06002171904729063;
  repeat1objective1.8895116276896715,gap0.06495802287773983. These are accepted
  discovery candidates,not provenoptima or finalselected-gridmodels. Detailed
  reports in `2026-09-11-existing-k14-reuse-audit.json`.
- Used partitionmanualfallback. cm1fouridle48CPU/241732MiBnodes atreview;resource
  test-only accepted. Dependency determines actual extension start,not scheduler
  test-only timing prediction. TwoWLSslots remain reserved for the campaign.
- Created separate extension release_20260911.json,testsreport and exclusive
  submission intent/response journal. Expandedqueue+124 checked<=998 before
  submission. No executablecode/science/noise change this turn.
- Submitted **25801134**,array0-123%2,cm1/lr_qchem/condo_qchem,16CPU/32GiB,
  2h30m/job,7200s/solve,afterokALL25796986,no automaticrequeue. Slurm confirmed
  PENDING(Dependency),throttle2 and correct resources. Originalarrayadvanced
  to tasks2/3RUNNING;tasks4–13pending. No runningjob cancelled.
- Newarraycovers62missingKvalues×2fits. Together with retained14originaltasks,
  all138discoveries for69Kvalues14–82 are now scheduled. AlreadyacceptedK14
  candidates are reused directly; all other results must still pass audits.
- Gridselection/new414selected-gridfits remain NOTsubmitted. Nextprepare the
  full138candidate barrier/rowpublication and414fit execution/readback while
  discovery runs,then use allaccepted discoveries for commonrowselection.

Heavy extension outputs:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/discovery_extension_v1`.
Logs:data`revwb97m2/logs/discovery_extension_25801134_<index>.out/.err`.
Frozenoriginalartifacts stay in their existing productionroot. Bothslotsmust
remain reserved; pendingextensionwillstartautomaticallyafteroriginalarray.
