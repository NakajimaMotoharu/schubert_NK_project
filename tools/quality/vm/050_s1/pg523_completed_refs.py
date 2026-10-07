"""Current genuine parent DONE/independent all-column batch oracle; ten held Ref readback."""
import ast,datetime,hashlib,json,os,pathlib,stat,subprocess,sys,time
import dbus
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg523-completed-readback-v1')
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441';INV='8f4514e19fd94c429f2587af71edb53a'
START=15089848500;END=16431357068
def require(v):
 if not v:raise ValueError('fixed completed readback refused')
def verify_batch(old,actual):
 require(isinstance(old,list) and len(old)==452 and isinstance(actual,list) and len(actual)==462)
 require(all(isinstance(r,dict) and r and type(r.get('id'))is int for r in old+actual))
 require(len({r['id']for r in old})==452 and len({r['id']for r in actual})==462)
 previous={r['id']:r for r in old};current={r['id']:r for r in actual}
 require(all(current.get(i)==r for i,r in previous.items()))
 added=[r for r in actual if r['id']not in previous]
 expected={'BACKUP_DB','BACKUP_CONFIG','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_TRANSFER','CLEAN_BATCH_RUN','CLEAN_EXPIRY'}
 require(len(added)==10 and {r.get('step')for r in added}==expected)
 for r in added:
  require(r.get('run_id')=='91a748b4-1abe-484c-9682-44f46429b324' and r.get('business_date')=='2026-10-06' and r.get('status')=='SKIPPED')
  require(all(type(r.get(k))is int and r[k]==0 for k in ['target_count','success_count','failure_count','byte_count']))
  require(r.get('error_code')=='ALREADY_SUCCESSFUL' and r.get('error_summary')=='step already successful for business date')
  require(isinstance(r.get('started_at'),str) and isinstance(r.get('ended_at'),str))
  require(datetime.datetime.fromisoformat(r['started_at'])<=datetime.datetime.fromisoformat(r['ended_at']))
  prior=[x for x in old if x.get('step')==r['step'] and x.get('business_date')=='2026-10-06']
  require(prior and type(r.get('attempt'))is int and r['attempt']==max(x['attempt']for x in prior)+1)
def verify_pid1(rows):
 require(isinstance(rows,list) and len(rows)==4)
 for r in rows:
  require(isinstance(r,dict) and r.get('_BOOT_ID')==BOOT.replace('-','') and r.get('_PID')=='1' and r.get('_UID')=='0' and r.get('_COMM')=='systemd' and r.get('UNIT')=='schubert-nk-morning-controller.service' and r.get('INVOCATION_ID')==INV)
  require(isinstance(r.get('__MONOTONIC_TIMESTAMP'),str) and r['__MONOTONIC_TIMESTAMP'].isdigit() and START<=int(r['__MONOTONIC_TIMESTAMP'])<=END+1000)
 done=[r for r in rows if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf' and r.get('JOB_ID')=='26968' and r.get('JOB_TYPE')=='start' and r.get('JOB_RESULT')=='done']
 succeeded=[r for r in rows if r.get('MESSAGE_ID')=='7ad2d189f7e94e70a38c781354912448']
 require(len(done)==len(succeeded)==1 and int(done[0]['__MONOTONIC_TIMESTAMP'])==END and END-START<=1800000000)
 require(not any(r.get('JOB_RESULT')not in (None,'done') for r in rows))
def main():
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='readback' and sys.argv[2].isdigit());backend=int(sys.argv[2]);os.umask(0o077)
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 source=ast.parse(raw);names={'command','metadata','strict','owner','show','tree'}
 definitions=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names];require(len(definitions)==len(names))
 constants=[n for n in source.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
 class Fixed(ast.NodeTransformer):
  def visit_Constant(self,n):
   return ast.copy_location(ast.Constant(b'Pg523CompletedReadback'),n)if n.value==b'Pg480BackupRecovery'else n
 code=Fixed().visit(ast.Module(body=constants+definitions,type_ignores=[]));ast.fix_missing_locations(code);exec(compile(code,'<fixed readonly owner witness>','exec'),globals())
 require(SAVE.is_dir() and metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2] and {p.name for p in SAVE.iterdir()}=={'refs-prepare.private.log'})
 held=owner();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 def connection(present):
  q="select count(*) from pg_stat_activity a where a.pid="+str(backend)+" and a.usename='schubert_batch' and a.datname='schubert_nk' and a.application_name='PG523-completed-readback' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted);select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_backup') and pid<>"+str(backend)+";"
  require(command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'1'if present else b'0',b'0'])
 def snapshot(present):
  require(owner()==held);connection(present)
  units={u:show(u,FIELDS)for u in UNITS};parent=units['schubert-nk-morning-controller.service']
  require(parent['MainPID']==parent['ControlPID']=='0' and parent['Job']=='' and parent['ActiveState']=='inactive' and parent['SubState']=='dead')
  for p in pathlib.Path('/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service').glob('**/cgroup.procs'):require(not p.read_text().strip())
  require(not pathlib.Path('/proc/320189').exists())
  journal=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID='+INV,'-o','json','--no-pager']);j=[json.loads(l)for l in journal.splitlines()];verify_pid1(j)
  for u,pid,inv in [('schubert-nk-api.service','504968','844d2217a6494e4f9f852fc4f488a0fa'),('schubert-nk-web.service','507277','7127bb06489a4218acd2b72570ce1ec5'),('caddy.service','512938','bcb3353f526a4bd59a715cd4eb99d9fe')]:
   v=units[u];require(v['MainPID']==pid and v['InvocationID']==inv and v['ActiveState']=='active' and v['SubState']=='running' and v['Result']=='success' and v['ControlPID']=='0' and v['Job']=='')
  startup=pathlib.Path('/run/schubert-nk/startup');require(not any(p.name.endswith('.start.intent')for p in startup.iterdir()))
  for n in ['backup-request','cleanup-request','expiry-request']:require(not list(pathlib.Path('/run/schubert-nk',n).iterdir()))
  original=pathlib.Path('/var/lib/pgpt-s1-preservation/pg521-runtime-resume-v2/after.private.json').read_bytes();require(hashlib.sha256(original).hexdigest()=='f72d6c82d7ab352e415b3d9547ec83cf5c3a0a9d80a77a1d795720e8f9f8991e');old=json.loads(original)['rows']['schubert.batch_runs']
  q="begin isolation level repeatable read read only;set local timezone='UTC';select to_jsonb(t)::text from schubert.batch_runs t order by id;commit;"
  rows=[json.loads(l)for l in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()];verify_batch(old,rows)
  require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG495' and owner()==held)
  return {'units':units,'rows':rows,'pid1':j,'startup':tree(startup),'originals':tree(pathlib.Path('/var/lib/schubert-nk/maintenance'))}
 def save(name,v):
  with(SAVE/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 before=snapshot(True);require(before==snapshot(True));save('before.private.json',before);print('REF_READY',flush=True)
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n').decode('ascii');require(action in ['before','release']);require(snapshot(action!='release')==before)
  if action=='release':
   save('after.private.json',before)
   for u in reversed(refs):manager.UnrefUnit(u)
   bus.close();print('REF_RELEASED',flush=True);return
  print('REF_CHECKED',flush=True)
 raise ValueError('readonly owner channel ended')
if __name__=='__main__':
 try:main()
 except Exception as failure:
  import traceback
  print('REF_FAILED',flush=True);print('PG523_READBACK_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
  for frame in traceback.extract_tb(failure.__traceback__):
   if frame.filename==__file__:print('PG523_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
  while True:time.sleep(1)
