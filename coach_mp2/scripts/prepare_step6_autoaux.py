"""Diagnostic only: generate auxiliary basis from exact native carbon orbital basis."""
from pathlib import Path
import json,hashlib,shutil
import pyscf
from pyscf import gto,df
from pyscf.gto.basis import parse_gaussian
from step4_authority import setrem
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 bp=Path('/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux/basis/aug-cc-pCV5Z.bas');basis=parse_gaussian.load(str(bp),'C');mol=gto.M(atom='C 0 0 0',spin=2,basis={'C':basis},verbose=0);assert mol.nao_nr()==181;aux=df.autoaux(mol)['C'];lines=['$aux_basis','C 0']
 for shell in aux:
  assert len(shell)==2 and len(shell[1])==2;lines.extend(['SPDFGHIKLMN'[shell[0]]+' 1 1.0',f'{shell[1][0]:.17g} {shell[1][1]:.17g}'])
 lines+=['****','$end'];block='\n'.join(lines)+'\n';(R/'configs/step6_carbon_autoaux_diagnostic.txt').write_text(block)
 c=dict(next(c for c in json.loads((R/'manifests/step6_protocol_v1.json').read_text())['cases'] if c['tag']=='16_C_AE18_RIMP2_FC'));c['tag']='16_C_AE18_RIMP2_autoaux';text=setrem(Path(c['input']).read_text(),'AUX_BASIS_CORR','GEN')+'\n'+block;p=R/'inputs/step6_v1'/(c['tag']+'.in');p.write_text(text);c.update(input=str(p.resolve()),input_sha256=sha(p));dst=Path(c['scratch']).parent/c['tag'];dst.mkdir();c['scratch']=str(dst)
 for f,h in c['source_hashes'].items():shutil.copyfile(Path(c['source'])/f,dst/f);assert sha(dst/f)==h
 report=dict(scope='Diagnostic only, no scientific input authority change',pyscf_version=pyscf.__version__,source_basis=str(bp),source_basis_sha256=sha(bp),generator='pyscf.df.autoaux on explicit Gaussian94 native basis, no SCF',aux_shells=len(aux),aux_spherical_functions=sum(2*s[0]+1 for s in aux),max_l=max(s[0] for s in aux),cases=[c]);(R/'manifests/step6_autoaux_diagnostic_v1.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='cases'})
if __name__=='__main__':main()
