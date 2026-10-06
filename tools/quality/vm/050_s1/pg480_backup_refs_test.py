"""Independent public fixture checks. AST loads definitions only; no DBus/VM side effect."""
import ast,pathlib,os,stat,subprocess,tempfile,json,hashlib,types
source=pathlib.Path(__file__).with_name('pg480_backup_refs.py');tree=ast.parse(source.read_text())
names=['require','metadata','strict','epoch_ok','request_ok','pending_rows','marker_namespace_ok','same','show']
defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
env={'os':os,'stat':stat,'pathlib':pathlib,'RUN':'49437eda-1681-43a9-883a-424eb55a6166','UNITS':['fixed.service']}
exec(compile(ast.Module(body=defs,type_ignores=[]),str(source),'exec'),env)
n=0
def check(value):
 global n
 assert value;n+=1
def refused(call):
 global n
 try:call()
 except (ValueError,FileNotFoundError):n+=1;return
 raise AssertionError('invalid input accepted')
epoch=b'NKEPOCH1\nstate=INVALID\nboot_id=e07aa706-1acd-4e65-b309-d7f330f79d54\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=49437eda-1681-43a9-883a-424eb55a6166\ncutoff_utc=2026-10-06T06:28:43.734078Z\nactivation_id=21111111-2222-4333-8444-555555555555\npermit_sha256=-\n'
check(env['epoch_ok'](epoch))
for bad in [None,'text',b'',epoch.replace(b'INVALID',b'ISSUED'),epoch.replace(b'734078',b'734079'),epoch.replace(b'49437eda',b'49437edb'),epoch.replace(b'permit_sha256=-',b'permit_sha256='+b'a'*64)]:check(not env['epoch_ok'](bad))
request=b'NKBACKUP1\nrun=49437eda-1681-43a9-883a-424eb55a6166\nstarted=2026-10-06T06:28:52.000000Z\n'
check(env['request_ok'](request))
for bad in [None,'text',b'',request[:-1],request+b'extra\n',request.replace(b'NKBACKUP1',b'NKBACKUPVERIFY1'),request.replace(b'49437eda',b'49437edb')]:check(not env['request_ok'](bad))
rows=[{'run_id':'49437eda-1681-43a9-883a-424eb55a6166','step':s,'status':'RUNNING','ended_at':None,'target_count':0,'success_count':0,'failure_count':0,'byte_count':0,'error_code':None,'error_summary':None} for s in ['BACKUP_DB','BACKUP_CONFIG']]
check(env['pending_rows'](rows))
for bad in [None,{},[],rows[:1],rows+[rows[0]]]:check(not env['pending_rows'](bad))
for key,value in [('run_id','different'),('step','CLEANUP'),('status','FAILED'),('ended_at','now'),('target_count',1),('success_count',1),('failure_count',1),('byte_count',1),('error_code','ABANDONED'),('error_summary','failure')]:
 bad=[dict(x) for x in rows];bad[0][key]=value;check(not env['pending_rows'](bad))
env['before']={'old':{'allColumns':[1,None,'literal']}};env['same']({'old':{'allColumns':[1,None,'literal']}});check(True)
refused(lambda:env['same']({'old':{'allColumns':[1,None,'changed']}}));refused(lambda:env['same']({}))
env['command']=lambda *a:b'Id=fixed.service\nMainPID=0\n';check(env['show']('fixed.service',{'Id','MainPID'})=={'Id':'fixed.service','MainPID':'0'})
refused(lambda:env['show']('other.service',{'Id','MainPID'}));refused(lambda:env['show']('fixed.service',{'Id'}))
env['command']=lambda *a:b'Id=fixed.service\nId=fixed.service\n';refused(lambda:env['show']('fixed.service',{'Id'}))
with tempfile.TemporaryDirectory(prefix='pg480-literal-') as tmp:
 p=pathlib.Path(tmp)/'marker';p.touch();p.chmod(0o600)
 # Host owner is intentionally synthetic; test strict metadata and change rejection separately.
 original=env['metadata'];env['metadata']=lambda path:[*original(path)[:2],0,0,*original(path)[4:]]
 check(env['strict'](p,0o600,0)==b'');p.write_bytes(b'x');refused(lambda:env['strict'](p,0o600,0));p.chmod(0o640);refused(lambda:env['strict'](p,0o600,1))
 p.chmod(0o600);os.link(p,pathlib.Path(tmp)/'alias');refused(lambda:env['strict'](p,0o600,1));(pathlib.Path(tmp)/'alias').unlink();p.unlink();refused(lambda:env['strict'](p,0o600,1))
print('PG480_REFERENCE_ORACLE assertions='+str(n)+' actual0=true vmMutation0=true')

# BUG774/775: actually execute the new operator's loader with distinct public before-image
# and pinned current policy. Genuine old helper remains unchanged; history is not blanked.
definition=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='approved_configuration')
policy=source.with_name('pg477_unit_references.py').read_bytes()
check(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
fields=set('ExecStart,DropInPaths,ReadWritePaths,User,Group,SupplementaryGroups,NoNewPrivileges,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,RestrictSUIDSGID,CapabilityBoundingSet,AmbientCapabilities,UMask,LimitCORE,TimeoutStartUSec,TimeoutStopUSec,MemoryMax,TasksMax'.split(','))
def record(argv,history):return '{ path=/usr/bin/java ; argv[]='+argv+' ; ignore_errors=no ; start_time=['+('Tue 2026-10-06 06:28:42 UTC' if history else 'n/a')+'] ; stop_time=['+('Tue 2026-10-06 06:58:42 UTC' if history else 'n/a')+'] ; pid='+('3418691' if history else '0')+' ; code='+('exited' if history else '(null)')+' ; status='+('143' if history else '0/0')+' }'
old={k:'fixed-public-literal' for k in fields};old['ExecStart']=record('/usr/bin/java -cp fixed BackupWorker',False)
fixture={'configuration':{'schubert-nk-backup.service':old}}
class FixedPath:
 def __init__(self,name):self.name=name
 def __truediv__(self,name):return FixedPath(self.name+'/'+name)
 def read_bytes(self):
  assert self.name=='/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py';return policy
 def read_text(self):
  if self.name=='/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py':return policy.decode()
  assert self.name=='/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v3/refs-activate-before.private.json';return json.dumps(fixture)
loader={'pathlib':types.SimpleNamespace(Path=FixedPath),'ast':ast,'json':json,'hashlib':hashlib,'CONFIG':fields,'require':env['require']}
exec(compile(ast.Module(body=[definition],type_ignores=[]),str(source),'exec'),loader)
conf=dict(old);conf['ExecStart']=record('/usr/bin/java -cp fixed BackupWorker',True)
loader['approved_configuration']('schubert-nk-backup.service',conf);check(True)
for history in ['0','143','9']:
 value=dict(conf);value['ExecStart']=conf['ExecStart'].replace('status=143','status='+history)
 loader['approved_configuration']('schubert-nk-backup.service',value);check(True) # Declaration only; full18 separately rejects foreign history.
for key in fields-{'ExecStart'}:
 value=dict(conf);value[key]='foreign';refused(lambda:loader['approved_configuration']('schubert-nk-backup.service',value))
for value in [conf['ExecStart'].replace('BackupWorker','ForeignWorker'),conf['ExecStart'].replace('ignore_errors=no','ignore_errors=yes'),'',None]:
 bad=dict(conf);bad['ExecStart']=value;refused(lambda:loader['approved_configuration']('schubert-nk-backup.service',bad))
print('PG480_CONFIGURATION_ORACLE assertions='+str(n-44)+' actual0=true historyNotNormalized=true vmMutation0=true')
before_count=n
for phase,present,absent in [('OBSERVING',True,False),('BEFORE_RETIRE',True,False),('RETIRING',True,True),('RETIRED',False,True),('REISOLATING',True,True),('QUARANTINED',True,False)]:
 check(env['marker_namespace_ok']({'backup-request','backup-start.intent'},phase)==present)
 check(env['marker_namespace_ok']({'backup-request'},phase)==absent)
 for names in [set(),{'backup-start.intent'},{'backup-request','foreign'},{'backup-request','backup-start.intent','foreign'}]:check(not env['marker_namespace_ok'](names,phase))
for phase in [None,'FOREIGN','release']:check(not env['marker_namespace_ok']({'backup-request'},phase))
print('PG480_NAMESPACE_ORACLE assertions='+str(n-before_count)+' actual0=true typedInternalBoundary=true vmMutation0=true')
