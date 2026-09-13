from pathlib import Path
import struct,re
import numpy as np
F=r'[-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?'
def scalar(text,label):
 found=re.findall(label+r'\s*=\s*('+F+')',text,re.I)
 if not found:raise ValueError('Missing scalar '+label)
 v=float(found[-1].replace('D','E').replace('d','e'))
 if not np.isfinite(v):raise ValueError('Nonfinite scalar')
 return v
def parse_matrix(text):
 blocks=[];body=None
 for line in text.splitlines():
  if 'COACH integratedDV begin' in line:
   if body is not None or 'rows=96 cols=180' not in line:raise ValueError('Bad/nested matrix begin')
   body=[]
  elif 'COACH integratedDV end' in line:
   if body is None or not body or body[0].strip()!='integratedDV':raise ValueError('Unmatched end/label')
   a=np.array([[float(x) for x in row.split()] for row in body[1:]])
   if a.shape!=(96,180) or not np.isfinite(a).all():raise ValueError('Bad matrix shape/values')
   blocks.append(a);body=None
  elif body is not None:body.append(line)
 if body is not None or not blocks:raise ValueError('Missing/truncated matrix')
 return blocks[-1],len(blocks)
def iter_diagnostic(path):
 with Path(path).open('rb') as f:
  if f.read(8)!=b'COACHDV1':raise ValueError('Wrong diagnostic magic')
  while True:
   header=f.read(8)
   if len(header)!=8:raise ValueError('Truncated header')
   n=struct.unpack('=Q',header)[0]
   if n==0:
    if f.read(1):raise ValueError('Trailing diagnostic bytes')
    return
   if n>10000000:raise ValueError('Implausible batch size')
   payload=f.read(n*11*8)
   if len(payload)!=n*11*8:raise ValueError('Truncated payload')
   a=np.frombuffer(payload,dtype=np.float64).reshape(n,11,order='F')
   if not np.isfinite(a).all():raise ValueError('Nonfinite density dump')
   yield a
