"""One durable current same-run resume after independent post/live watch, not success."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1571_existing_runtime_closing import payload as closing
from pg1572_current_resume_observer import namespace

BEFORE_SHA='cc8ec852ca75bb2cf980ec97176ec771dab17bc0ffa4b3c2936f1c76db93345d'
BODY=r'''
raw=(BASE/'pg1571-existing-runtime-independent-closing-v1/observed.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==BEFORE_SHA);frozen=json.loads(raw)
def watch_identity():
 root=BASE/'pg1572-observer-v1';require(metadata(root)[2:6]==[0,0,stat.S_IFDIR|0o700,2]and not os.listxattr(root)and set(os.listdir(root))==set(WATCH_FILES))
 for name,digest in WATCH_FILES.items():
  file=root/name;m=metadata(file);require(m[2:6]==[0,0,stat.S_IFREG|0o400,1]and hashlib.sha256(file.read_bytes()).hexdigest()==digest and metadata(file)==m)
 argv=b'\0'.join([b'python3',b'-B',str(root/'pg1572_watch_parent.py').encode(),SOURCE.encode(),BOM.encode(),b'PG1544'])+b'\0';matches=[]
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdecimal():continue
  try:cmd=(p/'cmdline').read_bytes()
  except(FileNotFoundError,ProcessLookupError,PermissionError):continue
  if cmd!=argv:continue
  status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
  require(str((p/'exe').readlink())=='/usr/bin/python3.14'and status['Uid'].split()==status['Gid'].split()==['0']*4)
  matches.append({'pid':int(p.name),'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256(cmd).hexdigest()})
 require(len(matches)==1);return matches[0]
def persist(name,value):
 with(SAVE/name).open('xb')as f:f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def preserve_old_native(current):
 root=pathlib.Path('/run/schubert-nk/pt-coverage');out=SAVE/'native-before-private';out.mkdir(mode=0o700);records={}
 for path,row in current['runtime']['pt-coverage'].items():
  p=pathlib.Path(path)
  if p.suffix!='.exec':continue
  require(p.is_relative_to(root));fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:
   require(metadata(p)==row['metadata']and 0<=row['metadata'][6]<=67108864)
   data=os.pread(fd,row['metadata'][6]+1,0);require(len(data)==row['metadata'][6]and hashlib.sha256(data).hexdigest()==row['sha256']and metadata(p)==row['metadata'])
  finally:os.close(fd)
  relative=p.relative_to(root);dest=out/relative;dest.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
  with dest.open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
  records[str(relative)]={'size':len(data),'sha256':row['sha256'],'sourceOrigin':'legacy769-before-current1544-activation; not newsource coverage'}
 persist('native-before-manifest.private.json',records)
 for directory in [out,*[p for p in out.rglob('*')if p.is_dir()]]:
  fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
 return len(records)
SAVE=BASE/'pg1573-current-resume-once-v1';require(not os.path.lexists(SAVE))
PEER_CLOSED=True;peer_check();initialize_runtime()
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[];result=None
try:
 for n in UNITS:manager.LoadUnit(n);manager.RefUnit(n);refs.append(n)
 for n in UNITS:kernel_empty(n)
 first=snapshot();require(first==frozen and first==snapshot());protected_runtime(first)
 watch=watch_identity();require(watch==watch_identity())
 require(min(os.statvfs(p).f_bavail*os.statvfs(p).f_frsize for p in[BASE,pathlib.Path('/srv/schubert-nk/backup')])>=10737418240)
 SAVE.mkdir(mode=0o700);persist('before.private.json',first);native_count=preserve_old_native(first)
 persist('external-start-guard.private.json',{'source':SOURCE,'bomSha256':BOM,'boot':BOOT,'beforeSha256':BEFORE_SHA,'sameRun':'15700a87-9117-4f63-a0ff-768dd604d0f1','sameCutoff':'2026-10-11T21:18:59.040097Z','sameActivation':'9e706936-a3c9-4a09-bb66-e2b1e8bbef66','originalBudgetSeconds':1800,'watch':watch,'legacyNativePreservedCount':native_count,'attemptReserved':True,'repeatForbidden':True,'operatorEpochPermitWrites0':True})
 fd=os.open(SAVE.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
 require(snapshot()==frozen and watch_identity()==watch);peer_check()
 result=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],capture_output=True,timeout=15)
 parent=show('schubert-nk-morning-controller.service');persist('external-start-issued.private.json',dict(parent,clientExit=result.returncode,clientSuccessIsNotParentSuccess=True))
finally:
 errors=[]
 for n in reversed(refs):
  try:manager.UnrefUnit(n)
  except Exception as e:errors.append(type(e).__name__)
 try:bus.close()
 except Exception as e:errors.append(type(e).__name__)
 require(not errors)
require(result is not None)
print(json.dumps({'run':'PG1573-current-resume-once-v1','source':SOURCE,'boot':BOOT,'sameActiveRunCutoffActivation':True,'externalStartIssuedOnce':True,'originalBudgetSeconds':1800,'clientExit':result.returncode,'clientSuccessIsNotParentSuccess':True,'legacyNativePreservedCount':native_count,'parent':parent,'observer':watch,'metadataScopesClosedNormally':True,'formalAccepted':False},sort_keys=True))
raise SystemExit(result.returncode)
'''

def compose(hashes):
    if type(hashes)is not dict or set(hashes)!={'pg1572_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'}or any(type(h)is not str or len(h)!=64 or any(c not in '0123456789abcdef'for c in h)for h in hashes.values()):raise ValueError('exact observer closure required')
    raw=closing().split("POST=BASE/'pg1571-existing-runtime-independent-closing-v1'",1)[0]
    raw+='\nBEFORE_SHA='+repr(BEFORE_SHA)+'\nWATCH_FILES='+repr(hashes)+'\n'+BODY
    compile(raw,'<one current same-run resume>','exec');return raw

def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed dispatch source required')
    if not(W/'pg1572-watch-v1.started').exists()or(W/'pg1572-watch-v1.exit').exists()or not(W/'pg1572-parent-watch-v1.private.jsonl').stat().st_size:raise ValueError('live fresh observer first frame required')
    if json.loads((W/'pg1571-existing-runtime-independent-closing-v1/manifest.safe.json').read_bytes())['actualExit']!=0:raise ValueError('actual independent normal closing required')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg1572-observer-stage-v1').iterdir()};wanted={n:hashlib.sha256(v.encode()).hexdigest()for n,v in namespace()['files']().items()}
    if hashes!=wanted:raise ValueError('immutable actual observer changed')
    os.umask(0o077);out=W/'pg1573-current-resume-once-v1';out.mkdir(mode=0o700);code=compose(hashes).encode();(out/'payload.private.py').write_bytes(code)
    with(out/'observer.private.log').open('xb')as f:result=subprocess.run(SSH+['sudo','-n','python3','-'],input=code,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    safe={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(code).hexdigest(),'formalAccepted':False}
    if result.returncode==0:safe['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return result.returncode

if __name__=='__main__':raise SystemExit(main())
