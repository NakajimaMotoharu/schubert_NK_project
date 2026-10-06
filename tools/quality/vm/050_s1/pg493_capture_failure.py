"""BUG799 current timeout cohort read-only capture. No start/stop/epoch/DB mutation."""
import ast,datetime,hashlib,json,os,pathlib,shutil,stat,subprocess
require=lambda v:None if v else (_ for _ in ()).throw(ValueError('fixed failure capture refused'))
require(os.geteuid()==0);os.umask(0o077)
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg493-parent-failure-v1');require(not SAVE.exists())
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
names={'command','show','metadata','tree','kernel','configuration_fields'};parsed=ast.parse(raw)
defs=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names];require(len(defs)==len(names))
constants=[n for n in parsed.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in {'UNITS','FIELDS'} for t in n.targets)]
exec(compile(ast.Module(body=constants+defs,type_ignores=[]),'<immutable readonly capture>','exec'),globals())
before=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg492-resume-preparation-v3/refs-after.private.json').read_text())
def capture():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 units={u:show(u,FIELDS) for u in UNITS};actors={}
 parent=units['schubert-nk-morning-controller.service']
 require(parent['Id']=='schubert-nk-morning-controller.service' and parent['LoadState']=='loaded'
  and parent['InvocationID']=='52accf6d68f44487b6e0b3635c20396f' and parent['Result']=='timeout'
  and parent['ExecMainCode']=='1' and parent['ExecMainStatus']=='143' and parent['MainPID']==parent['ControlPID']=='0' and not parent['Job'])
 kernel('schubert-nk-morning-controller.service');require(not pathlib.Path('/proc/3905484').exists())
 for unit in UNITS:
  v=units[unit];require(v['Id']==unit and v['LoadState']=='loaded')
  if v['MainPID']!='0':
   p=pathlib.Path('/proc')/v['MainPID'];ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19])
   status={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in (p/'status').read_text().splitlines() if ':' in line}
   selected={k:status[k] for k in ['Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs']}
   actors[unit]={'pid':v['MainPID'],'invocation':v['InvocationID'],'ticks':ticks,'authority':selected,'cgroup':(p/'cgroup').read_text(),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()}
   require(ticks==int((p/'stat').read_text().rpartition(')')[2].split()[19]))
  require(v==show(unit,FIELDS))
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for table in before['rows']:q+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 q+='commit;'
 for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines():
  v=json.loads(line);require(v['table'] not in rows);rows[v['table']]=v['rows']
 require(all(r in rows['schubert.batch_runs'] for r in before['rows']['schubert.batch_runs']))
 allowed={'schubert.batch_runs','schubert.app_logs','schubert_web_session.web_log_outbox','schubert_web_session.web_http_sessions'}
 require(all(rows[t]==before['rows'][t] for t in rows if t not in allowed))
 roots={p:tree(pathlib.Path(p)) for p in before['trees']}
 require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG489')
 return {'units':units,'actors':actors,'configuration':{u:show(u,configuration_fields()) for u in UNITS},'rows':rows,'trees':roots,'current':'/opt/schubert-nk/releases/0.1.0-PG489'}
actual=capture();SAVE.mkdir(mode=0o700)
with (SAVE/'observed.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(actual,f,sort_keys=True);f.flush();os.fsync(f.fileno())
shutil.copytree('/run/schubert-nk/pt-coverage',SAVE/'native-after',symlinks=False)
for p in [SAVE/'native-after',*(SAVE/'native-after').rglob('*')]:
 require(not p.is_symlink());os.chmod(p,0o700 if p.is_dir() else 0o600)
 if p.is_file():
  with p.open('rb') as f:os.fsync(f.fileno())
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
require(actual['units']=={u:show(u,FIELDS) for u in UNITS})
print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateSnapshotSha256':hashlib.sha256((SAVE/'observed.private.json').read_bytes()).hexdigest(),'batchRows':len(actual['rows']['schubert.batch_runs']),'old432Preserved':True,'other20TablesUnchanged':True,'liveCohort':{u:{k:v[k] for k in ['pid','invocation','ticks']} for u,v in actual['actors'].items()},'parentTimeout143':True,'normalCloseInferred':False,'starts0':True,'changes0':True}))
