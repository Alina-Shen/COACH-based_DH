"""Scoped publication of supplied orbital locations and open-source solver research."""
from pathlib import Path
import argparse

ROOT=Path(__file__).resolve().parents[1]
NOTES=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
HEAVY=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2')
SCRATCH=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2')
NAME='06-orbital-sources-and-open-mio-solvers.md'

def proposed():
    chapter='''# 2026-09-12 — COACH orbital sources and open-source MIO alternatives

## Contents

- [Detailed solver comparison and benchmark recommendation](../../../../coach-based_dh/coach_mp2/results/2026-09-12-open-source-mio-solvers.md)
- [Orbital source binding](../../../../coach-based_dh/coach_mp2/manifests/orbital_source_locations_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, orbital-sources, MIO, open-source, SCIP, solver-comparison

User supplied GSCDB137 COACH orbitals at
`/global/scratch/users/jsliang/COACH3` (leading slash normalized from the supplied
`global/scratch/...`) and BigNC at `/global/scratch/users/jsliang/BigNC/COACH`.
Both directories and three sampled qarchive.h5 paths per directory are readable.
No complete inventory, archive-content/method validation, hashing or copy was
performed. Coverage for other external roles remains to be established. Sources
are read-only; working scratch remains `/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2`.

User asks for open alternatives because Gurobi is proprietary and their WLS
license permits at most two concurrent sessions. Our mathematical problem is
convex MIQP with 292 coefficient and 292 binary variables before presolve,
weighted SSE plus ridge, linear UEG/grid/bounds and big-M/cardinality constraints.

Primary-source research recommends SCIP/PySCIPOpt as first benchmark. Other
credible exact-formulation candidates: Pajarito+HiGHS+Hypatia (conic reformulation),
Pyomo MindtPy+HiGHS/Cbc+Ipopt (convex OA), Bonmin+Cbc+Ipopt and SHOT+Cbc+Ipopt.
Juniper is a heuristic supplement rather than the preferred bound/gap reference.
HiGHS/MILP solvers alone and continuous QP solvers alone do not supply the full
required MIQP route; modeling libraries are not replacement solver engines.
Detailed pros/cons, licenses, official citations and exact epigraph/conic
reformulations are in the linked report.

Recommendation is based on documented capabilities, not measured speed. Benchmark
matched matrices/starts/constraints, fixed-support controls and representative
K14/middle/K82 cases with/without the same grid rows; compare independently
audited objective, support, bounds/gaps, time, memory and global-throughput under
equal total resources. Publish an open fitting recipe and solver-neutral inputs/
audits for reviewers, where distribution rights permit. Q-Chem generation is a
separate dependency. No claim about journal requirements or guaranteed speedup.

No solver installed, executed or selected for production. Frozen Step 1 and the
18-step index remain unchanged; Gurobi remains the current contract until a
versioned validated backend amendment. Recorded source bindings, research report,
mutable progress and README/plan updates. Source-path receipt does not complete
Step 2/5. All writes remain inside the permitted project roots and project notes.
'''
    p=NOTES/'COACH-based_mp2.md';plan=p.read_text()
    plan=plan.replace('Source path remains pending;', 'GSCDB137/BigNC source paths are now recorded; source validation remains pending;')
    plan=plan.replace('The user will supply the COACH orbital source path\nlater.','The user supplied the GSCDB137 and BigNC source paths on September 12.\nThey are recorded below and await full validation.')
    addition='''## Orbital locations and solver alternatives — 2026-09-12

User-supplied read-only sources:

- GSCDB137: `/global/scratch/users/jsliang/COACH3` (normalized leading slash).
- BigNC: `/global/scratch/users/jsliang/BigNC/COACH`.

Both directories and three sampled archive paths per directory are readable.
This is not a coverage or COACH-method pass. Bindings are stored in
[orbital_source_locations_v1.json](../../../coach-based_dh/coach_mp2/manifests/orbital_source_locations_v1.json),
separately from the frozen scientific specification. Full manifest-based inventory,
method/input validation and copying remain pending; other external-role coverage
must be checked. Source receipt alone does not complete Step 2 or Step 5.

The user requested research into open-source MIO alternatives because of Gurobi's
proprietary dependency and two-session WLS limit. [Detailed comparison](../../../coach-based_dh/coach_mp2/results/2026-09-12-open-source-mio-solvers.md)
recommends SCIP as first benchmark, with Pajarito/MindtPy and Bonmin/SHOT as
additional candidates and Juniper as a heuristic supplement. No backend switch,
installation or solver benchmark has been authorized/performed. Preserve the
frozen Gurobi specification; any adoption requires a versioned validated change.

'''
    plan=plan.replace('## Fixed-orbital comparison and resolved omega decision',addition+'## Fixed-orbital comparison and resolved omega decision',1)
    plan=plan.replace('- [Step 1 scientific freeze]', '- [Orbital sources and open MIO research](./2026-09-12.chapters/'+NAME+')\n- [Step 1 scientific freeze]',1)
    p=NOTES/'2026-09-12.md';index=p.read_text().replace('\nTags:', '\n- [Orbital sources and open-source MIO alternatives](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
    heavy=(HEAVY/'README.md').read_text().replace('Source path/identity and native feature gates\nremain pending.','GSCDB137/BigNC source paths are recorded; source identity, full inventory\nand native feature gates remain pending.')
    scratch=(SCRATCH/'README.md').read_text().replace('The user will supply the read-only source orbital path later.','Read-only sources: `/global/scratch/users/jsliang/COACH3` (GSCDB137) and\n`/global/scratch/users/jsliang/BigNC/COACH` (BigNC). Directory/sample-path\nreadability passed; full inventory, method validation and copying remain pending.')
    return {NOTES/'COACH-based_mp2.md':plan,NOTES/'2026-09-12.md':index,NOTES/'2026-09-12.chapters'/NAME:chapter,HEAVY/'README.md':heavy,SCRATCH/'README.md':scratch}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');args=parser.parse_args()
    chapter=NOTES/'2026-09-12.chapters'/NAME
    if chapter.exists():raise ValueError('Already published; never overwrite a dated chapter')
    for p,t in proposed().items():
        if p.resolve()!=p:raise ValueError('Unexpected symlink')
        if args.publish:
            with p.open('x' if p==chapter else 'w') as f:f.write(t)
            assert p.read_text()==t
        print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(p))

if __name__=='__main__':main()
