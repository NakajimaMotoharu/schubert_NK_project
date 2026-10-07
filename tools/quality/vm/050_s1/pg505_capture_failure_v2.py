"""BUG814/815 current timeout cohort read-only capture. No start/stop/epoch/DB mutation."""
import ast,datetime,hashlib,json,os,pathlib,shutil,stat,subprocess
require=lambda v:None if v else (_ for _ in ()).throw(ValueError('fixed failure capture refused'))
require(os.geteuid()==0);os.umask(0o077)
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg505-parent-failure-v1');require(not SAVE.exists())
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
names={'command','show','metadata','tree','kernel','configuration_fields'};parsed=ast.parse(raw)
defs=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names];require(len(defs)==len(names))
constants=[n for n in parsed.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in {'UNITS','FIELDS'} for t in n.targets)]
exec(compile(ast.Module(body=constants+defs,type_ignores=[]),'<immutable readonly capture>','exec'),globals())
baseline_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg504-resume-preparation-v1/refs-after.private.json').read_bytes();require(hashlib.sha256(baseline_raw).hexdigest()=='67fa28ad6f289589994af0be7022a20fe12b673685d0c151ffb791dd91fec52e');before=json.loads(baseline_raw)
def capture():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 units={u:show(u,FIELDS) for u in UNITS};actors={}
 parent=units['schubert-nk-morning-controller.service']
 require(parent['Id']=='schubert-nk-morning-controller.service' and parent['LoadState']=='loaded'
  and parent['InvocationID']=='bbb6dc1276a4459da65143db3e4ee3f0' and parent['Result']=='timeout'
  and parent['ExecMainCode']=='1' and parent['ExecMainStatus']=='143' and parent['MainPID']==parent['ControlPID']=='0' and not parent['Job'])
 kernel('schubert-nk-morning-controller.service');require(not pathlib.Path('/proc/5872').exists())
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
 require(all(rows[t]==before['rows'][t] for t in rows if t!='schubert.batch_runs'))
 new=[r for r in rows['schubert.batch_runs'] if r not in before['rows']['schubert.batch_runs']]
 expected={'BACKUP_DB','BACKUP_CONFIG','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_TRANSFER','CLEAN_BATCH_RUN','CLEAN_EXPIRY'}
 require(len(new)==10 and {r['step'] for r in new}==expected)
 cutoffs={r['cutoff'] for r in before['rows']['schubert.batch_runs'] if r['run_id']=='91a748b4-1abe-484c-9682-44f46429b324'};require(len(cutoffs)==1)
 require(all(r['run_id']=='91a748b4-1abe-484c-9682-44f46429b324' and r['cutoff'] in cutoffs and r['status']=='SKIPPED'
  and all(r[k]==0 for k in ['target_count','success_count','failure_count','byte_count']) and r['error_code']=='ALREADY_SUCCESSFUL' and r['error_summary']=='step already successful for business date'
  and r['started_at'] is not None and r['ended_at'] is not None and r['started_at']<=r['ended_at'] for r in new))
 roots={p:tree(pathlib.Path(p)) for p in before['trees']}
 require(all(roots[p]==expected for p,expected in before['trees'].items() if not p.startswith('/run/')))
 require(units['artemis.service']['MainPID']=='38602' and units['artemis.service']['InvocationID']=='0608718743a74668a5e5bd87cf30f6b5')
 sql="select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"
 require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0'])
 require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG495')
 return {'units':units,'actors':actors,'configuration':{u:show(u,configuration_fields()) for u in UNITS},'rows':rows,'trees':roots,'current':'/opt/schubert-nk/releases/0.1.0-PG495'}
actual=capture();require(actual==capture());SAVE.mkdir(mode=0o700)
with (SAVE/'observed.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(actual,f,sort_keys=True);f.flush();os.fsync(f.fileno())
shutil.copytree('/run/schubert-nk/pt-coverage',SAVE/'native-after',symlinks=False)
for p in [SAVE/'native-after',*(SAVE/'native-after').rglob('*')]:
 require(not p.is_symlink());os.chmod(p,0o700 if p.is_dir() else 0o600)
 if p.is_file():
  with p.open('rb') as f:os.fsync(f.fileno())
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
require(actual['units']=={u:show(u,FIELDS) for u in UNITS})
print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateSnapshotSha256':hashlib.sha256((SAVE/'observed.private.json').read_bytes()).hexdigest(),'batchRows':len(actual['rows']['schubert.batch_runs']),'old442Preserved':True,'new10ExactSKIP':True,'other23TablesUnchanged':True,'persistent102Unchanged':True,'liveCohort':{u:{k:v[k] for k in ['pid','invocation','ticks']} for u,v in actual['actors'].items()},'parentTimeout143':True,'normalCloseInferred':False,'starts0':True,'changes0':True}))
