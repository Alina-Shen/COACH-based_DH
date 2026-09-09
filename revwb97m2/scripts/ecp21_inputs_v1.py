"""Exact21 reference-pinned embedded-ECP inputs; no arbitrary-element fallback."""
import hashlib
import re
from pathlib import Path
from revwb97m2 import v7_canary as v

REVIEW=v.ROOT/'results/2026-09-09-ecp21-production-reference-review.json'


def block(source,key):
    values=re.findall(rf'(?ims)^\s*\${key}\s*\n(.*?)^\s*\$end\b',source)
    v.require(len(values)==1,'missing/duplicate '+key)
    return values[0]


def electron_count(source,bridge):
    if not re.search(r'(?im)^\s*\$ecp\b',source):return v.electron_count(source,bridge)
    sha=hashlib.sha256(source.encode()).hexdigest()
    review=v.read(REVIEW)
    matches=[r for r in review['cases'] if r['input_sha256']==sha]
    v.require(len(matches)==1,'unreviewed embedded ECP input')
    case=matches[0]
    v.require(case['normal_termination'] and not case['fatal_marker'] and case['production_input_identical'],
              'production reference not successful')
    v.require(v.digest(case['production_input'])==sha and
        v.digest(case['production_output'])==case['production_output_sha256'],'production reference changed')
    molecule=block(source,'molecule').split()
    v.require(len(molecule)==6,'single real atom required')
    charge,mult=map(int,molecule[:2]);element=molecule[2]
    from pyscf.data import elements
    v.require(element in elements.ELEMENTS,'unknown element')
    core=int(bridge['ecp_electrons']);count=elements.ELEMENTS.index(element)-charge-core;spin=mult-1
    v.require(core==28 and bridge['elements']==element and
        bridge['ecp_resolution']==bridge['orbital_resolution']=='embedded_qchem_block','bridge representation changed')
    v.require(all(bridge[k]==value for k,value in case['bridge'].items()),'reviewed bridge changed')
    v.require(re.search(rf'(?im)^\s*{element}-ECP\s+4\s+28\s*$',block(source,'ecp')) is not None,'ECP header changed')
    v.require((count,spin)==(int(bridge['electron_count']),int(bridge['spin'])) and count>=spin>=0 and (count-spin)%2==0,
              'valence/spin mismatch')
    v.require(list(map(int,case['reported_alpha_beta']))==[(count+spin)//2,(count-spin)//2],'production electron mismatch')
    for key,value in (('BASIS','GEN'),('ECP','GEN'),('PURECART','11111'),('SCF_GUESS','READ'),('N_FROZEN_CORE','FC')):
        v.require(re.search(rf'(?im)^\s*{key}\s+(?:=\s*)?{value}\s*$',block(source,'rem')) is not None,'changed '+key)
    return count,spin


def stage_inputs(source,settings,bridge):
    if not re.search(r'(?im)^\s*\$ecp\b',source):return v.stage_inputs(source,settings,bridge)
    electron_count(source,bridge)
    result={grid:v.derive_input(source,v.GRID_VALUES[grid],skip_post_fock_diagonalization=True) for grid in v.GRIDS}
    result.update(scalar=v.derive_scalar_input(source,settings=settings)[0],
                  fixed=v.derive_fixed_energy_input(source)[0],pt2=v.derive_pt2_input(source)[0])
    for text in result.values():
        for key in ('molecule','basis','ecp'):
            v.require(block(text,key)==block(source,key),'changed authoritative block')
        v.require('MP2_RESTART_NO_SCF TRUE' in text,'no-SCF control absent')
    return result
