"""Read-only authenticate new admission original hash; no raw export or replay."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2674_operation_publication_sources import production

SLOT='pg2698-operation-admission-before-v1'
BODY=r'''
import hashlib,json,os,pathlib,stat
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2684-operation-current-noargs-once-v2/before.private.json')
def require(v):
 if not v:raise ValueError('immutable new admission original required')
def identity(s):
 return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:raw=os.pread(fd,s.st_size+1,0);require(len(raw)==s.st_size)
finally:os.close(fd)
require(identity(p.lstat())==identity(s)and p.read_bytes()==raw and identity(p.lstat())==identity(s))
v=json.loads(raw);require(set(v)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'})
require(len(v['native'])==41 and sum(pathlib.Path(k).suffix=='.exec'for k in v['native'])==28)
print(json.dumps({'actualExit':0,'privateBeforeSha256':hashlib.sha256(raw).hexdigest(),'nativeEntries':41,'execEntries':28,'rawExported':False}))
'''


def before():
    v=json.loads((W/SLOT/'manifest.safe.json').read_bytes())
    if type(v.get('actualExit'))is not int or v['actualExit']!=0 or v.get('productionSource')!=production():raise ValueError('actual new admission hash qualification required')
    value=v['guest']['privateBeforeSha256']
    if type(value)is not str or len(value)!=64 or set(value)-set('0123456789abcdef'):raise ValueError('actual immutable before SHA required')
    return value


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean read-only operator required')
    start=json.loads((W/'pg2684-operation-current-noargs-once-v2/manifest.safe.json').read_bytes())
    live=json.loads((W/'pg2686-operation-current-live-binding-v1/manifest.safe.json').read_bytes())
    for v in [start,live]:
        if type(v.get('actualExit'))is not int or v['actualExit']!=0 or v.get('productionSource')!=production():raise ValueError('actual new source single start and independent live binding required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(BODY)
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=BODY.encode(),capture_output=True,timeout=30)
    (out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'productionSource':production(),'payloadSha256':hashlib.sha256(BODY.encode()).hexdigest(),'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
