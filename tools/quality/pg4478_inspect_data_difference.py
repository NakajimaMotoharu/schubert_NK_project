"""Classify preserved full-read rejection without replay or changing expectations."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W, SSH
from pg4434_current_candidate_admission_read import authenticate_host

GUEST=r'''
import os,json,hashlib,stat
from pathlib import Path
assert os.geteuid()==0
base=Path('/var/lib/pgpt-s1-preservation');source=base/'pg4476-inspect-pair-full-read-v1'
def read(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
 raw=p.read_bytes();return json.loads(raw),hashlib.sha256(raw).hexdigest()
reference,reference_sha=read(base/'pg4440-failed-full-image-diagnosis-v1/after.private.json');assert reference_sha=='148a8d8a3a3284dbf4a72833ca808ca8a07cee84a85b5562f07356006ac91148'
first,first_sha=read(source/'first-data.private.json');second,second_sha=read(source/'second-data.private.json')
first_pair,pair1_sha=read(source/'first-pair.private.json');second_pair,pair2_sha=read(source/'second-pair.private.json')
def differences(a,b,path=''):
 if type(a)is not type(b):return[{'path':path,'old':a,'new':b}]
 if type(a)is dict:
  result=[]
  for key in sorted(set(a)|set(b)):
   p=path+'/'+str(key)
   result.extend([{'path':p,'old':a.get(key),'new':b.get(key)}]if key not in a or key not in b else differences(a[key],b[key],p))
  return result
 if type(a)is list:
  if len(a)!=len(b):return[{'path':path,'old':a,'new':b}]
  return [d for i,(x,y)in enumerate(zip(a,b))for d in differences(x,y,path+'/'+str(i))]
 return []if a==b else[{'path':path,'old':a,'new':b}]
checked=['units','actors','durable','native','startup','runtime']
old_diffs=[d for k in checked for d in differences(reference[k],first[k],'/'+k)]
new_diffs=[d for k in checked for d in differences(first[k],second[k],'/'+k)]
result={'actualExit':0,'firstDataSha256':first_sha,'secondDataSha256':second_sha,'firstPairSha256':pair1_sha,'secondPairSha256':pair2_sha,
 'historicalDifferences':old_diffs,'boundaryDifferences':new_diffs,'javaBoundaryDiff':differences(first_pair['java'],second_pair['java']),
 'pythonBoundaryDiff':differences(first_pair['python'],second_pair['python']),'databaseRowsEqual':first['database']['rows']==second['database']['rows']==reference['database']['rows'],
 'operationsIssued':0,'formalAccepted':False,'oldScopesNormal':False}
save=base/'pg4478-inspect-data-difference-v1';assert not os.path.lexists(save);save.mkdir(mode=0o700)
raw=json.dumps(result,sort_keys=True).encode()
with(save/'difference.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'actualExit':0,'privateSha256':hashlib.sha256(raw).hexdigest(),'historicalChangedPaths':[d['path']for d in old_diffs],
 'boundaryChangedPaths':[d['path']for d in new_diffs],'javaBoundaryDiffCount':len(result['javaBoundaryDiff']),'pythonBoundaryDiffCount':len(result['pythonBoundaryDiff']),
 'safeUnitDifferences':[d for d in old_diffs if d['path'].startswith('/units/')],'databaseRowsEqual':result['databaseRowsEqual'],
 'firstDataSha256':first_sha,'secondDataSha256':second_sha,'firstPairSha256':pair1_sha,'secondPairSha256':pair2_sha,'operationsIssued':0,'formalAccepted':False}))
'''


def main():
    if check(GUEST,'<full saved rejection diagnosis>'):raise ValueError('all emitted static0')
    authenticate_host();os.umask(0o077);out=W/'pg4478-inspect-data-difference-v1';out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(GUEST)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=GUEST.encode(),capture_output=True,timeout=60)
    (out/'observer.private.log').write_bytes(result.stdout+result.stderr)
    value={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(GUEST.encode()).hexdigest(),'operationsIssued':0,'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':
    raise SystemExit(main())
