"""Independent pre-start802->805 raw declaration/runtime/data/resource qualification."""
import ast,inspect
import pg784_stopped_baseline as transport

PAYLOAD=r'''
import pathlib,os,sys,json,hashlib,stat
os.umask(0o077);assert os.geteuid()==0
base=pathlib.Path('/var/lib/pgpt-s1-preservation');prep=base/'pg805-runtime-resume-v2';save=base/'pg806-resume-post-v1';assert not os.path.lexists(save)
assert hashlib.sha256((prep/'complete.private').read_bytes()).hexdigest()=='479f6c1def5b869850c43bf708355a362ec6c80dd5ec5652a40627e4ba9ead80'
raw=(prep/'after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='a1cd83116444d30e0ca2cb974494f0edbe30a73cd233de308c7a68a1d2f79d63';before=json.loads(raw)
sys.path.insert(0,str(base/'pg805-resume-tools-v2'));import pg805_snapshot as h
from pg777_reference_capability import CaptureReferences
h.load_definitions();assert len(before['rows'])==24 and len(before['rows']['schubert.batch_runs'])==544 and len(before['unitFiles'])==18
def same():
 h.parent();units={u:h.show(u)for u in h.ORDER+h.EXTRA};assert units==before['units']
 for u,v in units.items():assert v['MainPID']==v['ControlPID']=='0'and not v['Job'];h.kernel_empty(u)
 for u,expected in before['configuration'].items():assert h.complete_configuration(h.command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),u)==expected
 assert h.rows()==before['rows']and {root:h.tree(pathlib.Path(root))for root in before['trees']}==before['trees']
 assert h.tree(pathlib.Path('/run/schubert-nk/pt-coverage'))==before['coverageBefore']
 for name,value in before['unitFiles'].items():
  p=pathlib.Path(name);assert h.metadata(p)==value['metadata']and hashlib.sha256(p.read_bytes()).hexdigest()==value['sha256']and h.metadata(p)==value['metadata']
 runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d');assert {p.name for p in runtime.iterdir()}=={'pg805-once-resume.conf'}
 p=runtime/'pg805-once-resume.conf';s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o644 and s.st_nlink==1 and 'system.posix_acl_access'not in os.listxattr(p)
 assert hashlib.sha256(p.read_bytes()).hexdigest()=='eb600f61cdc75089d2cc66da426ff69efe8b644806e8b21684ae5ebc88466911'and p.read_bytes()==(prep/'new-runtime.private').read_bytes()
 assert p.read_bytes().count(b' --resume ')==1 and p.read_bytes().endswith(b' --resume 9de2d03c-28c7-4647-97d9-c66ace06048c\n')
def resources():
 q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 assert h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0']
 for name in('maintenance.lock','startup-admission.lock'):
  s=pathlib.Path('/run/schubert-nk',name).lstat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':');assert len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
with CaptureReferences():
 same();same();resources();save.mkdir(mode=0o700)
 with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
for d in(save,save.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
resources()
print(json.dumps({'actualExit':0,'candidateSource':'102cdf1d365ab321f74b523237590eee764ae858','all24Preserved':True,'batchRows':544,'startupEntries':39,'originalPendingSame':True,'runtimePrepared':True,'starts0':True,'allTenKernel0':True,'M_A_OFD0':True,'databaseSessions0':True,'advisory0':True,'newScopesReturnedNormally':True,'snapshotSha256':hashlib.sha256(raw).hexdigest(),'runtimeSha256':'eb600f61cdc75089d2cc66da426ff69efe8b644806e8b21684ae5ebc88466911','formalAccepted':False}))
'''

if __name__=='__main__':
 ast.parse(PAYLOAD);raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg806-resume-post-v1');context={**transport.__dict__,'PAYLOAD':PAYLOAD}
 exec(compile(raw,'<806 fixed current once-runtime prestart fullpost>', 'exec'),context);context['main']()
