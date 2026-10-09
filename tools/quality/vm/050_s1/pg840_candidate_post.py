"""Independent full 24/current832/approval-only/owned resources post; no replay."""
import ast,inspect
import pg784_stopped_baseline as transport

PAYLOAD=r'''
import pathlib,sys,json,hashlib,os,stat
os.umask(0o077);assert os.geteuid()==0
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg840-current832-post-v1';assert not os.path.lexists(save)
oldraw=(base/'pg833-current-before832-v1/after.private.json').read_bytes()
assert hashlib.sha256(oldraw).hexdigest()=='d725011754d5a06d8591b16820b9e272aa41116723df8d6946384d6d1bc13652';before=json.loads(oldraw)
sys.path.insert(0,str(base/'pg835-pending-tools-v6'));import pg835_snapshot as h
from pg777_reference_capability import CaptureReferences
h.load_definitions();probe=base/'pg835-pending-codeonly-v6'
assert(probe/'complete.private').read_bytes()==b'pendingCodeOnly=true\nallNewScopesReturnedNormally=true\nepochUnchanged=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n'
observations=dict(row.split('=',1) for row in(probe/'observations.private').read_text().splitlines());assert observations.keys()=={'maxGapNanos'}and 0<int(observations['maxGapNanos'])<30000000000
approval='/etc/schubert-nk/release-approval/current'
expected=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG832\nmanifest_sha256=8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977\n'
def parent():
 assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
 assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG832')
 assert h.parent_value(h.show(h.EXTRA[0]))and not pathlib.Path('/proc/3123795').exists();h.kernel_empty(h.EXTRA[0])
h.parent=parent
def resources():
 parent()
 for u in h.ORDER+h.EXTRA:
  v=h.show(u);assert v['MainPID']==v['ControlPID']=='0'and not v['Job'];h.kernel_empty(u)
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:a=(p/'cmdline').read_bytes().split(b'\0')
  except(FileNotFoundError,PermissionError,ProcessLookupError):continue
  assert b'Pg835PendingDeployment'not in a and not any(s.endswith(b'/pg835_pending_refs.py')for s in a)
 for leaf in('maintenance.lock','startup-admission.lock'):
  s=pathlib.Path('/run/schubert-nk',leaf).lstat();assert s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split();d=f[5].split(':')if len(f)>5 else[]
   assert len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
 sql="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 assert h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0']
with CaptureReferences():
 resources();after=h.snapshot();assert after==h.snapshot()
 assert after['rows']==before['rows']and len(after['rows'])==24 and len(after['rows']['schubert.batch_runs'])==554
 assert after['configuration']==before['configuration']and set(after['trees'])==set(before['trees'])
 for root,entries in before['trees'].items():
  assert set(entries)==set(after['trees'][root])
  for name,old in entries.items():
   actual=after['trees'][root][name]
   if name==approval:
    assert actual['sha256']==hashlib.sha256(expected).hexdigest()and actual['metadata'][0]==old['metadata'][0]and actual['metadata'][2:7]==[0,0,stat.S_IFREG|0o400,1,len(expected)]
   elif name==str(pathlib.Path(approval).parent):assert actual['metadata'][:7]==old['metadata'][:7]and actual['sha256']==old['sha256']
   else:assert actual==old
 assert pathlib.Path(approval).read_bytes()==expected and hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'
 units={u:h.show(u)for u in h.ORDER+h.EXTRA};configuration={};files={}
 for unit in units:
  value=h.complete_configuration(h.command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),unit);configuration[unit]=value
  fragment=h.command(['/usr/bin/systemctl','show',unit,'--property=FragmentPath','--value']).decode().strip()
  assert fragment.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/'))
  for name in[fragment,*value['DropInPaths'].split()]:
   p=pathlib.Path(name);m=h.metadata(p);assert stat.S_ISREG(m[4])and m[2]==0 and m[5]==1
   files[name]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};assert m==h.metadata(p)
 assert files==before['unitFiles']and not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir())
 value={**after,'units':units,'configuration':configuration,'unitFiles':files,'current':'/opt/schubert-nk/releases/0.1.0-PG832','coverageBefore':h.tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}
 assert len(value['trees']['/run/schubert-nk/startup'])==44 and h.epoch_value(pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes(),True)
 save.mkdir(mode=0o700)
 with(save/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
resources()
for d in(save,save.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'candidateSource':'2a0d5aa392c85a1dc12a1cdb423978e8500895b8','currentRelease':'0.1.0-PG832','all24Preserved':True,'batchRows':554,'startupEntries':43,'allTenKernel0':True,'M_A_OFD0':True,'databaseSessions0':True,'advisory0':True,'newScopesReturnedNormally':True,'old835CloseNormal':False,'sameEpochInvalid':True,'runtimePresent':False,'maxObservationGapNanos':int(observations['maxGapNanos']),'unitFiles':len(files),'snapshotSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest(),'formalAccepted':False}))
'''

if __name__=='__main__':
 ast.parse(PAYLOAD);raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg840-current832-post-v1');context={**transport.__dict__,'PAYLOAD':PAYLOAD}
 exec(compile(raw,'<840 independent full current832>', 'exec'),context);context['main']()
