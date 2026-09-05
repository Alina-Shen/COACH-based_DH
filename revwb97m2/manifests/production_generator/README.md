# Step 13 preparatory production generator

This directory defines the resource-independent part of Step 13. It is safe to
develop while Step 12's high-cost measurement remains active because it does
not assign tiers, choose resources, render SBATCH scripts, or submit work.

The planner joins the exact 17,452-species fixed-geometry role union to the
validated basis bridge and immutable record index. It then performs a read-only
inventory of eight future restart boundaries per species:

1. fixed omegaB97M-V parent;
2. selected semilocal features on grid `250974`;
3. selected semilocal features on grid `99590`;
4. selected semilocal features on grid `75302`;
5. fixed-density VV10;
6. frozen-core total RI-UMP2;
7. frozen-parameter COACH pure three-body D4-ATM; and
8. final 292-feature species assembly.

Splitting the three grids and the scalar calculations prevents a
later failure from invalidating a successfully published earlier result. The
accepted combined Step 9/10 gateway artifacts remain unchanged; the split is a
contract for future Step 13 production artifacts.

Every boundary is reusable only when its completion marker, identity/status,
authority fingerprint, independent validation record, manifest hash, and all
declared artifact hashes pass. Failed, partial, corrupt, stale, or interrupted
trees are reported and preserved rather than overwritten or removed.

Create a dry-run plan with an explicit new output path:

```bash
python revwb97m2/scripts/plan_step13_production.py \
  --output /tmp/step13-plan.json
```

The command refuses to overwrite its output. Every species remains
`submission_authorized: false`, and all Step-12-dependent resource fields are
intentionally unset. Validate the checked-in contract with:

```bash
python revwb97m2/scripts/validate_step13_preparatory.py
```
