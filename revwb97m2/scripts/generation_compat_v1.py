"""Explicit additive compatibility; never mutate historical modules or manifests."""
import csv
from pathlib import Path
from revwb97m2 import v7_canary as v

CONTRACT=v.ROOT/'manifests/generation_compat_v1/contract.json'


def compare_dependencies(expected,current,additions):
    v.require(not (set(expected)&set(additions)), 'addition overlaps historical dependency')
    v.require(current=={**expected,**additions}, 'changed/missing/unreviewed dependency')


def check_contract():
    contract=v.read(CONTRACT)
    for path,sha in contract['authorities'].items():
        v.require(v.digest(path)==sha,'compatibility authority changed')
    for path,sha in contract['implementation_hashes'].items():
        v.require(v.digest(path)==sha,'compatibility implementation changed')
    return contract


def native_dependencies():
    contract=check_contract();plan=v.read(contract['native_plan'])
    compare_dependencies(plan['code_hashes'],v.code_hashes(),contract['allowed_additions'])
    return {**plan['code_hashes'],**contract['allowed_additions']}


def load_native_plan(path):
    contract=check_contract()
    v.require(Path(path).resolve()==Path(contract['native_plan']).resolve(),'wrong historical plan')
    plan=v.read(path);settings=v.load_fit_settings()
    v.require(plan['schema_version']==2 and plan['purpose']=='seven_fresh_v7_canaries_only','unsupported plan')
    v.require(tuple(c['species'] for c in plan['cases'])==v.NAMES,'canary scope changed')
    v.require(plan['specification_sha256']==settings.specification_sha256 and
        plan['inventory_sha256']==v.digest(v.INVENTORY),'science/inventory changed')
    v.require(plan['basis_bridge_sha256']==v.digest(v.BRIDGE),'basis bridge changed')
    bridges={r['species']:r for r in csv.DictReader(v.BRIDGE.open())}
    v.require(all(c['basis_bridge']==bridges[c['species']] for c in plan['cases']),'case bridge changed')
    native_dependencies()
    v.require(all(v.digest(p)==h for p,h in plan['build_hashes'].items()),'build changed')
    v.require(Path(plan['output_root']).resolve().parent==v.DATA.resolve(),'unsafe output root')
    scratch=(v.SCRATCH/Path(plan['output_root']).name).resolve()
    v.require(scratch.parent==v.SCRATCH.resolve() and Path(plan['scratch_root']).resolve()==scratch,'unsafe scratch')
    v.require(all(Path(c['scratch_root']).resolve()==scratch/c['species'] for c in plan['cases']),'unsafe case scratch')
    return plan,settings
