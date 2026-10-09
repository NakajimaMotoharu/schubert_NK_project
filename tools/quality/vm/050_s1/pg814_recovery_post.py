"""Independent readonly full current949 recovery afterconditions, never starts/stops/revokes."""
import ast,inspect
import pg784_stopped_baseline as transport
PAYLOAD=r'''
import pathlib,sys,json,hashlib,os,stat,ast,re
os.umask(0o077);assert os.geteuid()==0
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg814-recovered949-post-v1';assert not os.path.lexists(save)
sys.path.insert(0,str(base/'pg813-failed949-tools-v2'));import pg813_owned as h
from pg777_reference_capability import CaptureReferences
h.load_definitions();before=h.baseline();root=base/'pg813-failed949-recovery-v2'
assert(root/'complete.private').read_text()=='allNewScopesReturnedNormally=true\noldCloseNotInferred=true\nexistingPairRetired=true\ncurrentSameEpochInvalid=true\nstarts0=true\n'
observations=dict(row.split('=',1)for row in(root/'observations.private').read_text().splitlines());assert int(observations['count'])>0 and int(observations['maxGapNanos'])<30000000000
policy=(base/'pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();assert hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4'
node=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');env={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<strict exec record>','exec'),env);exec_record=env['exec_record']
# Load the separately versioned pure typed schema, not any old main/authorization.
host_schema=SCHEMA
scope={};exec(compile(host_schema,'<fixed cold history schema>','exec'),scope);accepted=scope['accepted']
def snapshot():
 h.parent();units={u:h.show(u)for u in h.ORDER+h.EXTRA};configuration={}
 for unit,v in units.items():
  assert v['MainPID']==v['ControlPID']=='0'and not v['Job'];h.kernel_empty(unit)
  closed=json.loads((root/(unit+'.stopped.private')).read_text())if unit in h.ORDER else{}
  if unit in h.ORDER and v!=closed:
   assert v['ActiveState']=='inactive'and v['SubState']=='dead'and v['InvocationID']==''and all(v[k]=='0'for k in('ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic'))
  value=h.complete_configuration(h.command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),unit)
  expected=before['configuration'][unit];old=exec_record(expected['ExecStart']);new=exec_record(value['ExecStart'])
  assert accepted(old,new,v,closed)
  value['ExecStart']=expected['ExecStart'];assert value==expected;configuration[unit]=value
 rows=h.rows();assert rows==before['rows']and len(rows)==24 and len(rows['schubert.batch_runs'])==554
 trees={name:h.tree(pathlib.Path(name))for name in before['trees']};startup='/run/schubert-nk/startup';epoch=startup+'/epoch.current';intent=startup+'/0eece14c-f832-47c2-b7dd-14125682e7ea.API.start.intent'
 for name in trees:
  if name!=startup:assert trees[name]==before['trees'][name]
 assert set(trees[startup])==set(before['trees'][startup])-{intent}and len(trees[startup])-1==43
 assert h.epoch_value(pathlib.Path(epoch).read_bytes(),True)
 assert trees[startup][startup]['metadata'][:6]==before['trees'][startup][startup]['metadata'][:6]
 for path,value in before['trees'][startup].items():
  if path not in(startup,epoch,intent):assert trees[startup][path]==value
 files={}
 for unit,value in configuration.items():
  fragment=h.command(['/usr/bin/systemctl','show',unit,'--property=FragmentPath','--value']).decode().strip()
  for name in[fragment,*value['DropInPaths'].split()]:
   p=pathlib.Path(name);metadata=h.metadata(p);assert stat.S_ISREG(metadata[4])and metadata[2]==0 and metadata[5]==1
   files[name]={'metadata':metadata,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};assert metadata==h.metadata(p)
 assert files==before['unitFiles']
 return {'units':units,'configuration':configuration,'rows':rows,'trees':trees,'unitFiles':files,'current':before['current'],'coverageAfter':h.tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}
with CaptureReferences():
 value=snapshot();assert value==snapshot()
sql="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
assert h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0']
for leaf in('maintenance.lock','startup-admission.lock'):
 s=pathlib.Path('/run/schubert-nk',leaf).stat()
 for row in pathlib.Path('/proc/locks').read_text().splitlines():
  parts=row.split();dev=parts[5].split(':')if len(parts)>5 else[]
  assert len(dev)!=3 or(int(dev[0],16),int(dev[1],16),int(dev[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
save.mkdir(mode=0o700)
with(save/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
for d in(save,save.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'source':'102cdf1d365ab321f74b523237590eee764ae858','all24Preserved':True,'batchRows':554,'startupEntries':43,'sameEpochInvalid':True,'allTenKernel0':True,'databaseClient0':True,'advisory0':True,'M_A0':True,'newScopesReturnedNormally':True,'oldParent143NotNormalized':True,'maxDbGapNanos':int(observations['maxGapNanos']),'dbObservations':int(observations['count']),'runtimePresent':True,'snapshotSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest(),'completeSha256':hashlib.sha256((root/'complete.private').read_bytes()).hexdigest(),'genuineAccepted':False,'formalAccepted':False}))
'''
if __name__=='__main__':
 from pathlib import Path
 schema=(Path(__file__).resolve().parent/'pg785_exec_history.py').read_text();assert 'if __name__'not in schema
 payload='SCHEMA='+repr(schema)+'\n'+PAYLOAD;ast.parse(payload)
 raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg814-recovered949-post-v1');context={**transport.__dict__,'PAYLOAD':payload}
 exec(compile(raw,'<independent814 readonly>', 'exec'),context);context['main']()
