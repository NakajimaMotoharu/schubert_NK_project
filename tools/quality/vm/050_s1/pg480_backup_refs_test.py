"""Independent public fixture checks. AST loads definitions only; no DBus/VM side effect."""
import ast,pathlib,os,stat,subprocess,tempfile
source=pathlib.Path(__file__).with_name('pg480_backup_refs.py');tree=ast.parse(source.read_text())
names=['require','metadata','strict','epoch_ok','request_ok','pending_rows','same','show']
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
