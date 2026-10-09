"""SSC236 fixed two retained779 processes, pidfd TERM only. No Unit/epoch/DB mutation."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')

def terminate(pid,ticks,verify,reserve,open_pidfd,send,wait,close):
    before=verify(pid,ticks)
    fd=open_pidfd(pid)
    try:
        if verify(pid,ticks)!=before:raise ValueError('owned generation changed')
        reserve(pid,before)
        send(fd)
        if not wait(fd):raise ValueError('owned TERM not terminal')
    finally:close(fd)


PAYLOAD=r'''
import sys,pathlib,json,os,hashlib,signal,select,time,stat
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG750')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'
base=pathlib.Path('/var/lib/pgpt-s1-preservation');raw=(base/'pg781-retained779-current-v1/current.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='823d5be73223e2c6232fa2758cba4badae3eba10ebb751b0c0c859465deb703b';old=json.loads(raw)
tools=base/'pg779-failed758-tools-v1'
for n,d in old['toolFiles'].items():assert hashlib.sha256((tools/n).read_bytes()).hexdigest()==d
sys.path.insert(0,str(tools));import pg779_owned as h
h.load_definitions()
save=base/'pg782-retained779-handoff-v1';assert not os.path.lexists(save)
def stable(value):
 status=dict(l.split(':',1)for l in value['status'].splitlines()if ':'in l)
 return {**{k:v for k,v in value.items()if k!='status'},'authority':{k:status[k].strip()for k in ('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid')}}
def actor(pid,ticks):
 expected=old['owner']if pid==3105271 else old['refs'];assert (pid,ticks)in ((3105271,14283385),(3105303,14283477))
 p=pathlib.Path('/proc')/str(pid);s=(p/'stat').read_text();assert s[s.rindex(')')+2:].split()[19]==str(ticks)
 argv=(p/'cmdline').read_bytes();assert hashlib.sha256(argv).hexdigest()==expected['argvSha256']
 fds={}
 for f in(p/'fd').iterdir():
  try:fds[f.name]=str(f.readlink())
  except FileNotFoundError:continue
 value={'pid':pid,'ticks':ticks,'argvSha256':hashlib.sha256(argv).hexdigest(),'status':(p/'status').read_text(),'cgroup':(p/'cgroup').read_text(),'exe':str((p/'exe').readlink()),'fds':fds}
 actual=stable(value);wanted=stable(expected)
 if pid==3105303 and not pathlib.Path('/proc/3105271').exists()and actual['authority']['PPid']=='1':
  actual['authority']['PPid']=wanted['authority']['PPid']
 assert actual==wanted;return actual
def all_kernel():
 for unit in h.ORDER+h.EXTRA:
  v=h.show(unit);assert v['MainPID']==v['ControlPID']=='0'and not v['Job'];h.kernel_empty(unit)
 h.parent()
def original():
 value=h.snapshot();assert value==old['snapshot'];assert value==h.snapshot();all_kernel();return value
def private(name,data):
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def reserve(pid,value):private(str(pid)+'.term-reserved.private.json',json.dumps(value,sort_keys=True).encode())
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
actor(3105271,14283385);actor(3105303,14283477);original()
for name in ('maintenance.lock','startup-admission.lock'):
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat();assert stat.S_IMODE(s.st_mode)==0o600 and s.st_uid==s.st_gid==0 and s.st_nlink==1
 found=[]
 for row in pathlib.Path('/proc/locks').read_text().splitlines():
  f=row.split()
  if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE','3105271']:
   d=f[5].split(':')
   if len(d)==3 and(int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):found.append(row)
 assert len(found)==1
save.mkdir(mode=0o700);private('before.private.json',json.dumps(old,sort_keys=True).encode())
terminate(3105271,14283385,actor,reserve,lambda p:os.pidfd_open(p,0),lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)
deadline=time.monotonic()+15
while any(pathlib.Path('/proc',str(pid)).exists()for pid in (3105271,3105303))and time.monotonic()<deadline:time.sleep(.02)
assert not pathlib.Path('/proc/3105271').exists()
if pathlib.Path('/proc/3105303').exists():
 # Parent EOF may have already terminated this exact Ref process; never send twice.
 actor(3105303,14283477)
 terminate(3105303,14283477,actor,reserve,lambda p:os.pidfd_open(p,0),lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)
 deadline=time.monotonic()+15
 while pathlib.Path('/proc/3105303').exists()and time.monotonic()<deadline:time.sleep(.02)
assert not pathlib.Path('/proc/3105303').exists()
assert not any(row.split()[4:5]in (['3105271'],['3105303'])for row in pathlib.Path('/proc/locks').read_text().splitlines())
# Ref loss can GC inactive Unit runtime history; no prior invocation/close is restored.
after=h.snapshot();assert after==old['snapshot'];assert after==h.snapshot();all_kernel()
db=h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',"select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"]);assert db.splitlines()==[b'0',b'0']
private('after.private.json',json.dumps(after,sort_keys=True).encode());private('complete.private.json',json.dumps({'allOldProcessesGone':True,'allOldOFDGone':True,'allTenKernel0':True,'databaseSessions0':True,'advisory0':True,'oldCloseUnknown':True,'newOwnershipNotYetAcquired':True,'unitStops0':True,'newStarts0':True},sort_keys=True).encode())
print(json.dumps({'actualExit':0,'oldJavaAndRefGone':True,'allOldOFDGone':True,'allTenKernel0':True,'all24Preserved':True,'batchRows':544,'startupEntries':42,'old779NormalClose':False,'newOwnershipNotYetAcquired':True,'startsUnitStopsRevoke0':True,'completeSha256':hashlib.sha256((save/'complete.private.json').read_bytes()).hexdigest(),'afterSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest()}))
'''


def payload():
    # Share only the independently tested pidfd algorithm, no old operator authorization.
    import inspect
    marker='h.load_definitions()\n';assert PAYLOAD.count(marker)==1
    index=PAYLOAD.index(marker)+len(marker)
    # A separate readonly administrator's ten references preserve history during handoff.
    # Old Ref process disappearance is still authenticated separately; not normal Unref.
    code=PAYLOAD[:index]+'from pg777_reference_capability import CaptureReferences\nwith CaptureReferences():\n'+''.join(' '+line+'\n'for line in PAYLOAD[index:].splitlines())
    return inspect.getsource(terminate)+'\n'+code


def main():
    os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
    base=W/'pg782-retained779-handoff-v1';assert not any(Path(str(base)+s).exists()for s in ('.private.stderr','.safe.json','.exit'))
    code=payload();ast.parse(code)
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    with Path(str(base)+'.private.stderr').open('xb')as f:r=subprocess.run(ssh,input=code.encode(),stdout=subprocess.PIPE,stderr=f,timeout=150)
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    if r.returncode==0:
        value=json.loads(r.stdout);value.update(recordedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
        with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
        print(json.dumps(value))
    else:print(json.dumps({'actualExit':r.returncode,'privateErrorSha256':hashlib.sha256(Path(str(base)+'.private.stderr').read_bytes()).hexdigest()}))
    raise SystemExit(r.returncode)


if __name__=='__main__':main()
