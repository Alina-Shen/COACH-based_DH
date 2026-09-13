# COACH MP2 mirror preparation

Prepared 2026-09-12. Historical preparation guide. Step 1 is now complete; the [frozen scientific specification](../configs/scientific_spec_v1.json) supersedes this preparation contract. A chemistry/fitting pipeline is not yet implemented.

The [live project plan](../../../codex_notes/projects/coach-based_dh/COACH-based_mp2.md) is the decision/status authority.
The [contract](../configs/mirror_contract_v1.json) records the COACH orbital substitution and user-selected fixed target omega=0.27 bohr^-1.
The [reference inventory](../manifests/revwb97m2_reference_v1.json) pins reviewed source files at repository HEAD f69b3a3313c2b779fb7e1708157805739ed9a6ff. It is not a transitive runtime dependency lock.

Port the current v7 chemistry settings and later expanded-objective/full-K campaign overrides. Earlier README/default settings include v6, VV10 b=10, explicit residuals and a seven-K scan; do not use those as current execution authority.

Before execution, create a project-specific scientific spec, complete dependency lock, metadata/orbital manifests, isolated storage adapters, COACH-native gateways and fresh release evidence. Existing runners embed reference-project matrix hashes, output roots, releases and job IDs. Do not invoke them directly on COACH inputs. Keep reference jobs and frozen files unchanged.

Reuse code and audited metadata; recompute all orbital-dependent features, Nofit, reaction matrices and grid selections. D4-ATM reuse needs matching geometry/charge/parameters/backend identity. Parent COACH omega and target-energy omega are separate provenance fields; PT2 orbital energies and frozen-core conventions require native verification.

First gateways should exercise closed/open-shell, diffuse and ECP inputs, three-grid emission, same-archive scalars, parent/target reconstruction separately, OS+SS closure, and atomic restart rejection for wrong-project inputs. Then prepare reaction identities and optimizer readback checks. No new regression suite is claimed by this documentation-only scaffold.

Use one global two-session WLS allocation across projects. The intended matched campaign has 138 discovery and 414 selected solves, all K14–82, with paired frozen noise and 7200-second budgets. New COACH discoveries determine the common selected rows. No old completion marker or submission authorization transfers.

User decision (2026-09-12): initial target-energy omega=0.27 bohr^-1 is fixed, not an initial guess. Port semilocal exchange and SR/LR-HF/Nofit consistently from the reference omega=0.30 implementation. A discrete outer omega scan with inner coefficient refits is an optional future refinement after functional-design choices are fixed; its grid and budget are deferred. The existing 552-solve plan is for the fixed-0.27 setting only.
