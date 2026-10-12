"""One reserved ordinary noargs new-run start; previous DONE is never resumed."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1596_current_ordinary_before import payload as preflight
from pg1597_current_ordinary_observer import namespace

BODY=r'''
def observer():
 root=base/'pg1597-observer-v1';require(root.is_dir()and{p.name for p in root.iterdir()}==set(WATCH_FILES))
 for name,digest in WATCH_FILES.items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest)
 argv=b'\0'.join([b'python3',b'-B',str(root/'pg1597_watch_parent.py').encode(),b'4d6bcbddb417b76d27e52d5d9640752c300edccf',b'e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c',b'PG1544'])+b'\0';matches=[]
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdecimal():continue
  try:cmd=(p/'cmdline').read_bytes()
  except(FileNotFoundError,ProcessLookupError,PermissionError):continue
  if cmd!=argv:continue
  status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
  require(str((p/'exe').readlink())=='/usr/bin/python3.14'and status['Uid'].split()==status['Gid'].split()==['0']*4)
  matches.append({'pid':int(p.name),'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256(cmd).hexdigest()})
 require(len(matches)==1);return matches[0]
require(native==after['native']and declaration[1].endswith('dev.codex.schubert.nk.batch.file.MorningProcessMain')and '--resume'not in declaration[1])
require(os.statvfs('/var/lib/pgpt-s1-preservation').f_bavail*os.statvfs('/var/lib/pgpt-s1-preservation').f_frsize>=10737418240)
watch=observer();save=base/'pg1598-current-ordinary-once-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
def persist(name,value):
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
native_copy=save/'native-before-private';native_copy.mkdir(mode=0o700);records={}
for path,v in native.items():
 p=pathlib.Path(path)
 if p.suffix!='.exec':continue
 require(p.is_relative_to(pathlib.Path('/run/schubert-nk/pt-coverage')))
 s=p.lstat();require(metadata(p)==v['metadata']and stat.S_ISREG(s.st_mode)and s.st_nlink==1 and 0<s.st_size<=16777216)
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:content=os.pread(fd,s.st_size+1,0);require(len(content)==s.st_size and hashlib.sha256(content).hexdigest()==v['sha256']and metadata(p)==v['metadata'])
 finally:os.close(fd)
 relative=p.relative_to('/run/schubert-nk/pt-coverage');destination=native_copy/relative;destination.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 with destination.open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(content);f.flush();os.fsync(f.fileno())
 records[str(relative)]={'sha256':v['sha256'],'bytes':len(content)}
require(len(records)==10);persist('native-before-manifest.private.json',records)
for p in [native_copy,*[p for p in native_copy.rglob('*')if p.is_dir()]]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
require(watch==observer()and native==snapshot())
persist('before.private.json',after)
persist('external-start-guard.private.json',{'source':data['source']['commit'],'manifestSha256':hashlib.sha256(manifest).hexdigest(),'ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'previousCompletion':summary,'originalBudgetSeconds':1800,'attemptReserved':True,'replayAllowed':False,'observer':watch})
r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic'],text=True,timeout=5)
current=dict(line.split('=',1)for line in raw.splitlines());current.update(clientExit=r.returncode,ordinaryNoargs=True,oldCompletedRunNotResumed=True,clientSuccessIsNotParentSuccess=True,originalBudgetSeconds=1800)
persist('external-start-issued.private.json',current)
print(json.dumps(current))
raise SystemExit(r.returncode)
'''

def payload(hashes):
    raw=preflight();marker="save=base/'pg1596-current-ordinary-before-v1'"
    if raw.count(marker)!=1:raise ValueError('one before persistence boundary required')
    raw=raw[:raw.index(marker)]+BODY
    return 'WATCH_FILES='+repr(hashes)+'\n'+raw

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    if not(W/'pg1597-watch-v1.started').exists()or(W/'pg1597-watch-v1.exit').exists():raise ValueError('current live observer required')
    raw=(W/'pg1597-parent-watch-v1.private.jsonl').read_bytes()
    frames=[json.loads(line)for line in raw.splitlines()]
    if not frames or any(frame.get('automaticStop',False)is not False for frame in frames):raise ValueError('fresh readonly observer first frame required')
    states=[frame['states']for frame in frames if 'states'in frame]
    if not states or set(states[-1])!={'morning','api','web','caddy'}or any(row['MainPID']!='0'or row['ControlPID']!='0'or row['Job']for row in states[-1].values()):raise ValueError('new observer quiescent first frame required')
    expected={n:hashlib.sha256(s.encode()).hexdigest()for n,s in namespace()['files']().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg1597-observer-stage-v1').iterdir()}!=expected:raise ValueError('fixed observer source changed')
    out=W/'pg1598-current-ordinary-once-v1';out.mkdir(mode=0o700);code=payload(expected).encode();(out/'payload.private.py').write_bytes(code)
    with(out/'observer.private.log').open('xb')as log:r=subprocess.run(SSH+['sudo','-n','python3','-'],input=code,stdout=log,stderr=log);log.flush();os.fsync(log.fileno())
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(code).hexdigest(),'formalAccepted':False,'reservationMustBeReauthenticatedBeforeRetry':True}
    if r.returncode==0:value['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return r.returncode

if __name__=='__main__':raise SystemExit(main())
