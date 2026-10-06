"""Read-only independent observer of the exact retained v2 owner. NEVER admission authority."""
import hashlib,pathlib,subprocess,os
os.umask(0o077)
source=pathlib.Path(__file__).with_name('pg480_backup_refs.py');private=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private');work=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
payload=r'''import ast,pathlib,os,stat,sys,subprocess,json,hashlib,traceback,types
source=SOURCE;tree=ast.parse(source)
class ObservedOwner:
 def getppid(self):return 3564716
 def __getattr__(self,k):return getattr(os,k)
env={'ast':ast,'pathlib':pathlib,'os':ObservedOwner(),'stat':stat,'sys':types.SimpleNamespace(argv=['observer','retire','3564747']),'subprocess':subprocess,'json':json,'hashlib':hashlib}
constants=[n for n in tree.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in ['TOOLS','SAVE','BOOT','RUN','PARENT','BACKUP','UNITS','FIELDS','MARKER'] for t in n.targets)]
exec(compile(ast.Module(body=constants+[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<readonly-observer-not-authority>','exec'),env)
env['backend']=3564747;env['previous']=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg479-archive-diagnosis/after-terminal.private.json').read_text());env['CONFIG']=env['configuration_fields']();env['held']=env['owner']()
try:
 env['snapshot']('OBSERVING',False);print('PG480_READONLY_DIAG preservedConditionsSame=true oldDatabaseAbsent=true authorityAccepted=false')
except Exception as failure:
 print('PG480_READONLY_DIAG type='+type(failure).__name__+' authorityAccepted=false')
 for frame in traceback.extract_tb(failure.__traceback__):print(frame.name+':'+str(frame.lineno))
 raise SystemExit(1)
'''
args=['ssh','-i',str(private/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(private/'known_hosts'),'ubuntu@127.0.0.1','sudo -n python3 -B -']
result=subprocess.run(args,input=('SOURCE='+repr(source.read_text())+'\n'+payload).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
log=work/('pg480-readonly-diagnose-'+hashlib.sha256(source.read_bytes()).hexdigest()[:12]+'.private.log')
with log.open('xb') as f:f.write(result.stdout);f.write(result.stderr)
print(result.stdout.decode(),end='');raise SystemExit(result.returncode)
