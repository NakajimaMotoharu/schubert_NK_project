"""Read-only current949 same-generation full24/private actors/native/config capture, no stop."""
import ast,inspect
import pg784_stopped_baseline as transport
PAYLOAD=r'''
import pathlib,sys,os,subprocess,json,hashlib,stat
os.umask(0o077);assert os.geteuid()==0
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg812-current-timeout-v2';assert not os.path.lexists(save)
sys.path.insert(0,str(base/'pg805-resume-tools-v2'));import pg805_snapshot as h
from pg777_reference_capability import CaptureReferences
h.load_definitions();old=h.baseline();assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
import ast,collections
library=(base/'pg805-resume-tools-v2/pg805_snapshot.py').read_text()
node=next(n for n in ast.parse(library).body if isinstance(n,ast.FunctionDef)and n.name=='rows')
rows_source=ast.unparse(node)
assert rows_source.count(" and len(result['schubert.batch_runs']) == 544")==1
rows_source=rows_source.replace(" and len(result['schubert.batch_runs']) == 544",'')
namespace=dict(h.__dict__);exec(compile(rows_source,'<812 capture-only all24>', 'exec'),namespace)
current_rows=namespace['rows']
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG796')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d'
expected={'schubert-nk-api.service':('3342473','6220dab5a87945d2bb144cb9e14f5f14'),'schubert-nk-web.service':('3344741','02ae69dca0514d8c917831eee3ca82b6'),'caddy.service':('3350579','42e945fbd2894199b7dfca297c989627'),'artemis.service':('3158873','cb2f7a6c4beb4420a0e96adb65fb6f11')}
def actor(pid):
 p=pathlib.Path('/proc',pid);s=(p/'stat').read_text();fds={}
 for fd in(p/'fd').iterdir():
  try:fds[fd.name]=str(fd.readlink())
  except FileNotFoundError:continue
 return {'pid':int(pid),'ticks':int(s.rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'argvPrivate':(p/'cmdline').read_bytes().hex(),'statusPrivate':(p/'status').read_text(),'cgroup':(p/'cgroup').read_text(),'exe':str((p/'exe').readlink()),'fds':fds}
def snapshot():
 units={u:h.show(u)for u in h.ORDER+h.EXTRA};parent=units['schubert-nk-morning-controller.service']
 assert parent['MainPID']==parent['ControlPID']=='0'and not parent['Job']and parent['InvocationID']=='7ea672e8a76c4a4a8a7994652366a4cc'and parent['Result']=='timeout'and parent['ExecMainStatus']=='143'
 actors={}
 for unit,(pid,inv)in expected.items():
  assert units[unit]['MainPID']==pid and units[unit]['InvocationID']==inv and units[unit]['ActiveState']=='active'and not units[unit]['Job'];actors[unit]=actor(pid)
 configuration={u:h.complete_configuration(h.command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),u)for u in units}
 files={}
 for u,value in configuration.items():
  fragment=h.command(['/usr/bin/systemctl','show',u,'--property=FragmentPath','--value']).decode().strip();assert fragment.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/'))
  for name in[fragment,*value['DropInPaths'].split()]:
   p=pathlib.Path(name);m=h.metadata(p);assert stat.S_ISREG(m[4])and m[2]==0 and m[5]==1;files[name]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};assert m==h.metadata(p)
 return {'units':units,'actors':actors,'configuration':configuration,'unitFiles':files,'rows':current_rows(),'trees':{root:h.tree(pathlib.Path(root))for root in old['trees']},'current':str(pathlib.Path('/opt/schubert-nk/current').readlink()),'native':h.tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}
with CaptureReferences():
 value=snapshot();second=snapshot()
 assert value['units']==second['units']and value['configuration']==second['configuration']and value['unitFiles']==second['unitFiles']and value['rows']==second['rows']and value['trees']==second['trees']
 for unit,a in value['actors'].items():
  b=second['actors'][unit];assert all(a[k]==b[k]for k in('pid','ticks','argvSha256','cgroup','exe'))
 assert value['rows'].keys()==old['rows'].keys()and len(value['rows'])==24
 for table,rows in old['rows'].items():
  if table=='schubert.batch_runs':assert not(collections.Counter(rows)-collections.Counter(value['rows'][table]))
  else:assert value['rows'][table]==rows
 save.mkdir(mode=0o700)
 with(save/'current.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
epoch=pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes()
with(save/'epoch.private').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(epoch);f.flush();os.fsync(f.fileno())
for d in(save,save.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'readonlyCapture':True,'source':'102cdf1d365ab321f74b523237590eee764ae858','all24Captured':True,'batchRows':len(value['rows']['schubert.batch_runs']),'startupEntries':len(value['trees']['/run/schubert-nk/startup'])-1,'originalActive':pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists(),'actors':{u:{k:v[k]for k in('pid','ticks','argvSha256')}for u,v in value['actors'].items()},'snapshotSha256':hashlib.sha256((save/'current.private.json').read_bytes()).hexdigest(),'epochSha256':hashlib.sha256(epoch).hexdigest(),'genuineAccepted':False,'formalAccepted':False}))
'''

if __name__=='__main__':
 ast.parse(PAYLOAD);raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg812-current-timeout-v2');context={**transport.__dict__,'PAYLOAD':PAYLOAD}
 exec(compile(raw,'<812 actual949 preownedstop full capture>', 'exec'),context);context['main']()
