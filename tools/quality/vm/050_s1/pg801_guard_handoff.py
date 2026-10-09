"""BUG946 known pre-SAVE/DB/Refs owner only; ordinary pidfd TERM, no Unit operation."""
import ast
import inspect
import pg784_stopped_baseline as transport
from pg782_owned_handoff import terminate

PAYLOAD=r'''
import os,sys,pathlib,json,hashlib,signal,select,time,stat
os.umask(0o077);assert os.geteuid()==0
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg801-guard-handoff-v1';assert not os.path.lexists(save)
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG750')
assert not os.path.lexists(base/'pg799-pending-codeonly')
sys.path.insert(0,str(base/'pg799-pending-tools-v1'));import pg799_snapshot as h
from pg777_reference_capability import CaptureReferences
h.load_definitions()
def actor(pid,ticks):
 assert(pid,ticks)==(3112232,15308543);p=pathlib.Path('/proc')/str(pid)
 assert str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java'and int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks
 argv=(p/'cmdline').read_bytes();assert argv.split(b'\0')[-4:]==[b'Pg799PendingDeployment',b'102cdf1d365ab321f74b523237590eee764ae858',b'c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d',b'']
 status=dict(s.split(':',1)for s in(p/'status').read_text().splitlines()if ':'in s)
 assert status['Uid'].split()==status['Gid'].split()==['0']*4 and not(p/'task'/str(pid)/'children').read_text().strip()
 return {'pid':pid,'ticks':ticks,'argvSha256':hashlib.sha256(argv).hexdigest(),'cgroup':(p/'cgroup').read_text(),'authority':{k:status[k].strip()for k in('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid')}}
def resources(expect_owned):
 h.parent()
 for u in h.ORDER+h.EXTRA:
  v=h.show(u);assert v['MainPID']==v['ControlPID']=='0'and not v['Job'];h.kernel_empty(u)
 for name in('maintenance.lock','startup-admission.lock'):
  p=pathlib.Path('/run/schubert-nk',name);s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
  found=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':')
   if len(d)==3 and(int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):found.append(f)
  assert (len(found)==1 and found[0][1:5]==['FLOCK','ADVISORY','WRITE','3112232'])if expect_owned else not found
 q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 assert h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0']
def private(name,data):
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def reserve(pid,value):private(str(pid)+'.term-reserved.private.json',json.dumps(value,sort_keys=True).encode())
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
with CaptureReferences():
 owner=actor(3112232,15308543);resources(True);before=h.snapshot();assert before==h.snapshot()==h.baseline()['capturedSnapshot']
 save.mkdir(mode=0o700);private('before.private.json',json.dumps(before,sort_keys=True).encode());private('owner.private.json',json.dumps(owner,sort_keys=True).encode())
 terminate(3112232,15308543,actor,reserve,lambda pid:os.pidfd_open(pid,0),lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)
 deadline=time.monotonic()+15
 while pathlib.Path('/proc/3112232').exists()and time.monotonic()<deadline:time.sleep(.02)
 assert not pathlib.Path('/proc/3112232').exists();resources(False);after=h.snapshot();assert after==before==h.snapshot()
 private('after.private.json',json.dumps(after,sort_keys=True).encode())
 private('complete.private',b'knownPreDatabaseOwnerGone=true\noldCloseUnknown=true\nallOriginalValuesPreserved=true\nnewUnitStartsStopsRevoke0=true\n')
resources(False)
print(json.dumps({'actualExit':0,'ownedJavaGone':True,'M_A_OFD0':True,'databaseSessions0':True,'advisory0':True,'allTenKernel0':True,'all24Preserved':True,'batchRows':544,'startupEntries':39,'oldNormalClose':False,'startsUnitStopsRevoke0':True,'snapshotSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest(),'completeSha256':hashlib.sha256((save/'complete.private').read_bytes()).hexdigest()}))
'''

def payload():return inspect.getsource(terminate)+'\n'+PAYLOAD

if __name__=='__main__':
 ast.parse(payload());raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg801-guard-handoff-v1');context={**transport.__dict__,'PAYLOAD':payload()}
 exec(compile(raw,'<801 fixed preDB guard owner handoff>', 'exec'),context);context['main']()
