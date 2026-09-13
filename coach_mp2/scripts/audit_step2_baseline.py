"""Read-only reference audit; writes reports only inside coach_mp2.
This is NOT a reconstruction from imported production orbitals.
"""
from pathlib import Path
import hashlib, json, re, sys, os
ROOT = Path(__file__).resolve().parents[1]
os.environ['TMPDIR'] = str(ROOT / 'runtime')
os.environ.setdefault('OMP_NUM_THREADS', '1')
REF = ROOT.parent / 'coach'
sys.path.insert(0, str(REF))
import h5py
import numpy as np
from pyscf import gto
from FunctionalCOACH.coach_pyscf import d4_atm_energy, load_xyz_job, OMEGA, CX_SR_HF, D4_PARAMS

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()

def parse(text):
    vals = {}
    for line in text.splitlines():
        if '=' not in line: continue
        key, value = line.split('=', 1)
        try: vals[' '.join(key.split())] = float(value.split()[0].replace('D','E'))
        except (ValueError, IndexError): pass
    return vals

def closure(vals):
    names = ['Alpha HF Exchange Energy','Beta HF Exchange Energy','DFT Correlation Energy',
             'DFT Exchange Energy','DFT Non-Local Correlation Energy','Total Coulomb Energy',
             'Nuclear Repulsion Energy']
    if 'One-Electron (alpha) Energy' in vals:
        names += ['One-Electron (alpha) Energy','One-Electron (beta) Energy']
    else:
        names += ['Kinetic (alpha) Energy','Kinetic (beta) Energy',
                  'Nuclear Attraction (alpha) Energy','Nuclear Attraction (beta) Energy','SEOQF Energy']
    reconstructed = sum(vals[k] for k in names)
    target = vals['SCF energy in the final basis set']
    return dict(terms={k:vals[k] for k in names}, reconstructed_hartree=reconstructed,
                printed_scf_hartree=target, residual_hartree=reconstructed-target,
                tolerance_hartree=2e-9, passed=abs(reconstructed-target)<2e-9)

def main():
    fixtures = []
    for name in ['SIE4x4_h2o','16_C_AE18','L14_2a']:
        path = REF/'FunctionalCOACH/tests/qchem_outputs'/f'{name}.out'
        text = path.read_text(); vals = parse(text)
        row = dict(name=name, source=str(path), sha256=sha(path),
                   method_coach=bool(re.search(r'^method\s+COACH\s*$',text,re.M)),
                   build_banner=next((line.strip() for line in text.splitlines() if re.search(r'Q-Chem [0-9.]+ for Intel',line)),None))
        if name != 'L14_2a': row['printed_component_closure'] = closure(vals)
        else:
            job = load_xyz_job(REF/'FunctionalCOACH/tests/xyzfiles'/f'{name}.xyz')
            # Geometry-only D4 needs no orbital basis or SCF. STO-3G is only a Mole container.
            mol = gto.M(atom=job['atom'], basis='sto-3g', charge=job['charge'],spin=job['spin'],verbose=0)
            energy = d4_atm_energy(mol); target = vals['-D4 energy including 3-body term']
            row['d4_geometry_reconstruction'] = dict(calculated_hartree=energy,printed_hartree=target,
                 residual_hartree=energy-target,tolerance_hartree=1e-10,passed=abs(energy-target)<1e-10)
            row['full_energy_reconstruction'] = 'unavailable: no full component breakdown in fixture'
        fixtures.append(row)
    binding = json.loads((ROOT/'manifests/orbital_source_locations_v1.json').read_text())
    samples = []
    for source in binding['sources']:
        for example in source['examples']:
            directory = Path(source['source_root'])/example['directory']
            row = dict(role=source['role'],directory=str(directory),files=[])
            for name in ['qarchive.h5','archive.h5','53.0','54.0','58.0','819.0','99.0','molecule','pseudodata']:
                p = directory/name
                info = dict(name=name,exists=p.is_file())
                if p.is_file():
                    info.update(size_bytes=p.stat().st_size,sha256=sha(p))
                    if name.endswith('.h5'):
                        with h5py.File(p,'r') as h:
                            datasets=[]; h.visititems(lambda n,o: datasets.append(n) if isinstance(o,h5py.Dataset) else None)
                            info.update(root_keys=list(h.keys()),root_attributes=list(h.attrs),datasets=datasets, dataset_shapes={n:list(h[n].shape) for n in datasets}, scalar_values={n:h[n][()].item() for n in datasets if h[n].shape==() and h[n].dtype.kind in 'ifu'})
                    if name=='molecule': info['text']=p.read_text()
                row['files'].append(info)
            row['original_input_output_present'] = [p.name for p in directory.iterdir() if p.suffix in ('.in','.out')]
            samples.append(row)
    paths = list((REF/'FunctionalCOACH').glob('coach*.py'))+[REF/'FunctionalCOACH/COACH.md',REF/'FunctionalCOACH/tests/test_coach_regression.py']
    paths += list((REF/'FunctionalCOACH/tests/xyzfiles').glob('*.xyz'))+list((REF/'paper').glob('*.pdf'))
    provenance=dict(schema_version=1,date='2026-09-12',reference_files=[dict(path=str(p),sha256=sha(p),size_bytes=p.stat().st_size) for p in sorted(paths)],
                    source_samples=samples,sampling_scope='three previously declared examples per source; not exhaustive inventory',
                    source_inputs_and_build_verified=False,production_orbital_energy_reconstruction=False,
                    reference_constants=dict(omega=OMEGA,c_sr_hf=CX_SR_HF,d4=D4_PARAMS))
    report=dict(schema_version=1,date='2026-09-12',fixtures=fixtures,
       scope='printed Q-Chem component closure and independent geometry-only D4; no SCF or orbital import',
       step2_complete=False, blockers=['Generating input/output and exact COACH build identity not supplied or verified.',
       'Three sampled GSCDB137 qarchive.h5 files are empty; three BigNC qarchive.h5 files contain data. GSCDB137 legacy scratch needs a verified native reader.',
       'Parent energy has not been reconstructed from supplied production orbitals.'])
    for path,data in [(ROOT/'manifests/step2_provenance_audit_v1.json',provenance),(ROOT/'results/step2_baseline_audit_v1.json',report)]:
        path.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    assert all(r['method_coach'] for r in fixtures)
    assert all(r.get('printed_component_closure',r.get('d4_geometry_reconstruction'))['passed'] for r in fixtures)
if __name__=='__main__':main()
