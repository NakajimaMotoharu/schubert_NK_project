"""Current genuine parent DONE/independent all-column batch oracle; ten held Ref readback."""
import ast,datetime,hashlib,json,os,pathlib,stat,subprocess,sys,time
import dbus
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg528-terminal-readback-v1')
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
 source=ast.parse(raw);names={'command','metadata','strict','owner','show','tree','configuration_fields','kernel'}
 definitions=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names];require(len(definitions)==len(names))
 constants=[n for n in source.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
 class Fixed(ast.NodeTransformer):
  def visit_Constant(self,n):
   return ast.copy_location(ast.Constant(b'Pg528TerminalReadback'),n)if n.value==b'Pg480BackupRecovery'else n
 code=Fixed().visit(ast.Module(body=constants+definitions,type_ignores=[]));ast.fix_missing_locations(code);exec(compile(code,'<fixed readonly owner witness>','exec'),globals())
 require(SAVE.is_dir() and metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2] and {p.name for p in SAVE.iterdir()}=={'refs-prepare.private.log'})
 held=owner();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 def connection(present):
  q="select count(*) from pg_stat_activity a where a.pid="+str(backend)+" and a.usename='schubert_batch' and a.datname='schubert_nk' and a.application_name='PG528-terminal-readback' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted);select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_backup') and pid<>"+str(backend)+";"
  require(command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'1'if present else b'0',b'0'])
 preserved=pathlib.Path('/var/lib/pgpt-s1-preservation/pg527-prestop-owned-handoff-v1')
 base_raw=strict(preserved/'before.private.json',0o600,33554432);require(hashlib.sha256(base_raw).hexdigest()=='c8c6b915a380902c3c8d022de24ab91a28e726e0d914a6ae88060bc8c360d5e3');baseline=json.loads(base_raw)
 complete=strict(preserved/'complete.private.json',0o600,4096);require(hashlib.sha256(complete).hexdigest()=='0f673d9bdfb1ebf02faeb91c1c11acdeb0530f7bc0737ea27811f8e84d090754')
 require(len(baseline)==12 and len(baseline['units'])==10 and len(baseline['rows'])==24 and len(baseline['rows']['schubert.batch_runs'])==462 and all(v is True for v in json.loads(complete).values()))
 def snapshot(present):
  require(owner()==held);connection(present)
  units={u:show(u,FIELDS)for u in UNITS};require(units==baseline['units'])
  for u,v in units.items():
   require(v['MainPID']==v['ControlPID']=='0'and v['Job']==''and v['ActiveState']in('inactive','failed'));kernel(u)
  require(not any(pathlib.Path('/proc',str(p)).exists()for p in (320189,504968,507277,512938,353417,561260,561289)))
  journal=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID='+INV,'-o','json','--no-pager']);j=[json.loads(l)for l in journal.splitlines()];verify_pid1(j)
  configuration={u:show(u,configuration_fields())for u in UNITS};require(configuration==baseline['configuration'])
  dependencies={u:show(u,{'Requires','Before','After','PartOf','BindsTo'})for u in UNITS};require(dependencies==baseline['dependencies'])
  pid1={}
  for u,expected in baseline['pid1Stop'].items():
   lines=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+u,'-o','json','--no-pager'])
   rows=[json.loads(l)for l in lines.splitlines()]
   actual=[r for r in rows if r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286'and r.get('JOB_ID')==expected[0]['JOB_ID']and r.get('JOB_TYPE')=='stop'and r.get('JOB_RESULT')=='done']
   require(actual==expected);pid1[u]=actual
  q="begin isolation level repeatable read read only;set local timezone='UTC';";data={}
  for t in baseline['rows']:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from(select to_jsonb(t)j from "+t+" t)q;"
  for l in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
   r=json.loads(l);require(r['table']not in data);data[r['table']]=r['rows']
  require(data==baseline['rows'])
  original=strict(pathlib.Path('/var/lib/pgpt-s1-preservation/pg521-runtime-resume-v2/after.private.json'),0o600,33554432);require(hashlib.sha256(original).hexdigest()=='f72d6c82d7ab352e415b3d9547ec83cf5c3a0a9d80a77a1d795720e8f9f8991e')
  verify_batch(json.loads(original)['rows']['schubert.batch_runs'],data['schubert.batch_runs'])
  trees={k:tree(pathlib.Path(p))for k,p in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup'),('native','/run/schubert-nk/pt-coverage'),('oldProofs','/var/lib/pgpt-s1-preservation/pg526-native-stop-v1')]}
  require(all(v==baseline[k]for k,v in trees.items()))
  native=trees['native'];require(sum(p.endswith('.exec')for p in native)==8)
  runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf');runtime_value={'metadata':metadata(runtime),'sha256':hashlib.sha256(runtime.read_bytes()).hexdigest()};require(runtime_value==baseline['runtime'])
  broker_raw=strict(preserved/'broker-full-journal.private.jsonl',0o600,4194304);require(hashlib.sha256(broker_raw).hexdigest()=='9dfb32081e5fe7851c4077a377d7dad4da6c5030223c369ab83c841a373b270b')
  broker_current=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+baseline['units']['artemis.service']['InvocationID'],'-o','json','--no-pager'])
  require([json.loads(l)for l in broker_raw.splitlines()]==[json.loads(l)for l in broker_current.splitlines()])
  require(units=={u:show(u,FIELDS)for u in UNITS}and owner()==held);connection(present)
  return{'units':units,'configuration':configuration,'rows':data,'dependencies':dependencies,'pid1Stop':pid1,'parentPid1':j,'runtime':runtime_value,**trees}
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
  print('REF_FAILED',flush=True);print('PG528_READBACK_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
  for frame in traceback.extract_tb(failure.__traceback__):
   if frame.filename==__file__:print('PG528_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
  while True:time.sleep(1)
