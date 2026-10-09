"""Fresh independent source102/796 post-readback full snapshot, declarations and resources0."""
import ast
import inspect
import pg784_stopped_baseline as transport

PAYLOAD=r'''
import pathlib,sys,json,os,hashlib,stat
os.umask(0o077);assert os.geteuid()==0
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg802-current-source-post-v1';assert not os.path.lexists(save)
sys.path.insert(0,str(base/'pg804-current-tools-v1'));import pg804_owned as h
from pg777_reference_capability import CaptureReferences
h.load_definitions();probe=base/'pg804-current-readback-v1'
assert(probe/'complete.private').read_bytes()==b'allNewScopesReturnedNormally=true\nsameTwoServersOver75s=true\ndbClosedConfirmed=true\noldCloseNotInferred=true\nstartsStopsRevokeRetire0=true\n'
observations={}
for line in(probe/'observations.private').read_text().splitlines():
 k,v=line.split('=');assert k not in observations and v.isdigit();observations[k]=int(v)
assert observations.keys()=={'count','maxGapNanos','maxGapBoundNanos'}and observations['count']>=15 and 0<observations['maxGapNanos']<observations['maxGapBoundNanos']==30000000000
def resources():
 h.parent()
 for u in h.ORDER+h.EXTRA:
  v=h.show(u);assert v['MainPID']==v['ControlPID']=='0'and not v['Job'];h.kernel_empty(u)
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:a=(p/'cmdline').read_bytes().split(b'\0')
  except(FileNotFoundError,PermissionError,ProcessLookupError):continue
  assert b'Pg799PendingDeployment'not in a and b'Pg804CurrentReadback'not in a and not any(s.endswith((b'/pg799_pending_refs.py',b'/pg804_refs.py'))for s in a)
 for name in('maintenance.lock','startup-admission.lock'):
  s=pathlib.Path('/run/schubert-nk',name).lstat();assert s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':');assert len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
 q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 assert h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0']
with CaptureReferences():
 resources();after=h.snapshot();assert after==h.snapshot()==h.baseline()['capturedSnapshot']
 units={u:h.show(u)for u in h.ORDER+h.EXTRA};files={};configuration={}
 for unit in units:
  value=h.complete_configuration(h.command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),unit);configuration[unit]=value
  fragment=h.command(['/usr/bin/systemctl','show',unit,'--property=FragmentPath','--value']).decode().strip()
  assert fragment.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/'))
  for name in[fragment,*value['DropInPaths'].split()]:
   p=pathlib.Path(name);m=h.metadata(p);assert stat.S_ISREG(m[4])and m[2]==0 and m[5]==1
   files[name]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};assert m==h.metadata(p)
 value={**after,'units':units,'configuration':configuration,'unitFiles':files,'current':str(pathlib.Path('/opt/schubert-nk/current').readlink()),'coverageBefore':h.tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}
 assert value['current']=='/opt/schubert-nk/releases/0.1.0-PG796'and len(value['rows'])==24 and len(value['rows']['schubert.batch_runs'])==544
 assert len(value['trees']['/run/schubert-nk/startup'])==40
 assert h.epoch_value(pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes(),True)
 save.mkdir(mode=0o700)
 with(save/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
resources()
for d in(save,save.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'candidateSource':'102cdf1d365ab321f74b523237590eee764ae858','currentRelease':'0.1.0-PG796','all24Preserved':True,'batchRows':544,'startupEntries':39,'allTenKernel0':True,'M_A_OFD0':True,'databaseSessions0':True,'advisory0':True,'newScopesReturnedNormally':True,'old799CloseNormal':False,'sameEpochInvalid':True,'maxObservationGapNanos':observations['maxGapNanos'],'observations':observations['count'],'unitFiles':len(files),'snapshotSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest(),'formalAccepted':False}))
'''

if __name__=='__main__':
 ast.parse(PAYLOAD);raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg802-current-source-post-v1');context={**transport.__dict__,'PAYLOAD':PAYLOAD}
 exec(compile(raw,'<802 independent current796 qualification>', 'exec'),context);context['main']()
