"""Seven current streams; old Backup and Inspector data retained but never counted."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1579_current_owned_stop_sources import SOURCE

CODE=r'''
import hashlib,json,os,pathlib,stat
def require(v):
 if not v:raise ValueError('current native catalog refused')
def meta(s):return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
base=pathlib.Path('/var/lib/pgpt-s1-preservation');root=base/'pg1579-native-stop-v1'
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='3d69f5af-6bac-46b1-a540-7591c4a79a0d')
def sealed(name):
 p=root/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1))
 raw=p.read_bytes();require(meta(s)==meta(p.lstat())and hashlib.sha256(raw).hexdigest()==SEALS[name]);return raw
before=json.loads(sealed('before.private.json'));after=json.loads(sealed('after.private.json'))
require(before['rows']==after['rows']and len(after['rows'])==24)
sealed('complete.private')
rows=[json.loads(line)for line in sealed('parent.private.jsonl').splitlines()]
done=[r for r in rows if r.get('INVOCATION_ID')=='c52c914a72804a89b0fd5f252f6ac0fc'and r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and r.get('JOB_ID')=='50856'and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='done']
require(len(done)==1);d=done[0];require(d['_BOOT_ID']=='3d69f5af6bac46b1a5407591c4a79a0d'and d['_PID']=='1'and d['_UID']=='0'and int(d['__MONOTONIC_TIMESTAMP'])==33583425972)
offset=int(d['__REALTIME_TIMESTAMP'])-int(d['__MONOTONIC_TIMESTAMP'])
archive=base/'pg1573-current-resume-once-v1';old=json.loads((archive/'native-before-manifest.private.json').read_bytes());require(len(old)==6)
for relative,v in old.items():
 p=archive/'native-before-private'/relative;require(p.stat().st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
native=pathlib.Path('/run/schubert-nk/pt-coverage');selected=[]
names=[('cleanup/cleanup.exec','schubert-nk-cleanup.service'),('expiry/expiry.exec','schubert-nk-expiry-cleanup.service'),('parent/parent.exec','schubert-nk-morning-controller.service')]
for role,unit,inv in [('api','schubert-nk-api.service','2111873a431743359c0627a8f5e394c8'),('web','schubert-nk-web.service','fb683eeb6d3b4e90b66c1576f9108a0c')]:
 require(before['units'][unit]['InvocationID']==after['units'][unit]['InvocationID']==inv)
 names.extend([('ordinary-'+role+'193/'+inv+'.terminal.exec',unit),('root-'+role+'193/'+inv+'.before-exec.exec',unit)])
for relative,unit in names:
 if unit=='schubert-nk-morning-controller.service':start=32043431270;end=33583425972
 else:start=int(before['units'][unit]['ExecMainStartTimestampMonotonic']);end=int(after['units'][unit]['ExecMainExitTimestampMonotonic'])
 require(32043431270<=start<=end)
 p=native/relative;s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_nlink==1 and 0<s.st_size<=16777216)
 raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest();require(meta(s)==meta(p.lstat())and(relative not in old or old[relative]['sha256']!=digest))
 selected.append({'relative':relative,'unit':unit,'sha256':digest,'bytes':s.st_size,'metadata':meta(s),'lowerMs':(offset+start)//1000-1000,'upperMs':(offset+end)//1000+1000})
require(len(selected)==7 and len({v['relative']for v in selected})==7)
excluded=[]
for p in native.rglob('*.exec'):
 relative=str(p.relative_to(native))
 if relative in {v['relative']for v in selected}:continue
 require(relative in old and hashlib.sha256(p.read_bytes()).hexdigest()==old[relative]['sha256'])
 excluded.append(relative)
require(set(excluded)=={'backup/backup.exec','ordinary-inspector196/d69f0f99b48a47a5b51ad571ac996c31.closing.exec','ordinary-inspector196/d69f0f99b48a47a5b51ad571ac996c31.terminal.exec'})
print(json.dumps({'selected':selected,'excludedHistorical':sorted(excluded),'oldSixArchiveUnchanged':True,'currentRootOriginalBudgetPreserved':True,'guestWritesStartsStops0':True}))
'''

def main():
    os.umask(0o077);out=W/'pg1584-current-native-catalog-v1';out.mkdir(mode=0o700)
    post=json.loads((W/'pg1583-current-terminal-post-v1.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or not post['allClientAdvisoryFlock0']:raise ValueError('actual sameSource complete stop post required')
    seals={n:post['proofHashes'][n]['sha256']for n in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
    payload=('SEALS='+repr(seals)+'\n'+CODE).encode();(out/'payload.private.py').write_bytes(payload)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=payload,capture_output=True,timeout=30)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(payload).hexdigest(),'formalAccepted':False}
    if r.returncode==0:value.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return r.returncode

if __name__=='__main__':raise SystemExit(main())
