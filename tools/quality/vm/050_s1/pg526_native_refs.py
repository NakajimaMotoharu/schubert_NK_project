"""Current genuine parent DONE/independent all-column batch oracle; ten held Ref readback."""
import ast,datetime,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
import dbus
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg526-native-stop-v1')
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441';INV='8f4514e19fd94c429f2587af71edb53a'
START=15089848500;END=16431357068
def require(v):
 if not v:raise ValueError('fixed completed readback refused')
def same_value(left,right):
 if type(left)is not type(right):return False
 if isinstance(left,dict):return set(left)==set(right) and all(type(k)is str and same_value(left[k],right[k])for k in left)
 if isinstance(left,list):return len(left)==len(right) and all(same_value(a,b)for a,b in zip(left,right))
 return type(left)in (type(None),bool,int,float,str) and left==right
def batch_index(rows):
 require(type(rows)is list and len(rows)==462)
 require(all(type(r)is dict and r and type(r.get('id'))is int and r['id']>0 for r in rows))
 columns=set(rows[0]);require(all(type(k)is str for k in columns)and all(set(r)==columns for r in rows))
 require(len({r['id']for r in rows})==462)
 return {r['id']:r for r in rows}
def verify_same_batch(previous,current):
 left=batch_index(previous);right=batch_index(current)
 require(set(left)==set(right) and all(same_value(left[i],right[i])for i in left))
def verify_batch(old,actual):
 require(isinstance(old,list) and len(old)==452 and isinstance(actual,list) and len(actual)==462)
 require(all(isinstance(r,dict) and r and type(r.get('id'))is int for r in old+actual))
 require(len({r['id']for r in old})==452 and len({r['id']for r in actual})==462)
 previous={r['id']:r for r in old};current={r['id']:r for r in actual}
 require(all(same_value(current.get(i),r) for i,r in previous.items()))
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
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='stop' and sys.argv[2].isdigit());backend=int(sys.argv[2]);os.umask(0o077)
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 source=ast.parse(raw);names={'command','metadata','strict','owner','show','tree','configuration_fields'}
 definitions=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names];require(len(definitions)==len(names))
 constants=[n for n in source.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
 class Fixed(ast.NodeTransformer):
  def visit_Constant(self,n):
   return ast.copy_location(ast.Constant(b'Pg526NativeStop'),n)if n.value==b'Pg480BackupRecovery'else n
 code=Fixed().visit(ast.Module(body=constants+definitions,type_ignores=[]));ast.fix_missing_locations(code);exec(compile(code,'<fixed readonly owner witness>','exec'),globals())
 parser=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 node=next(n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');exec(compile(ast.Module(body=[node],type_ignores=[]),'<fixed declaration parser>','exec'),globals())
 require(SAVE.is_dir() and metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2] and {p.name for p in SAVE.iterdir()}=={'refs-prepare.private.log'})
 held=owner();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 def connection(present):
  q="select count(*) from pg_stat_activity a where a.pid="+str(backend)+" and a.usename='schubert_batch' and a.datname='schubert_nk' and a.application_name='PG526-native-stop' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted);select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_backup') and pid<>"+str(backend)+";"
  require(command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'1'if present else b'0',b'0'])
 import pg526_native_owned_stop as h
 require(h.ROOT==SAVE and h.BOOT==BOOT)
 stages=[];captures=None;first=None
 def capture_data(present):
  require(owner()==held and h.holder()==held);connection(present)
  units={u:show(u,FIELDS)for u in UNITS}
  parent=units['schubert-nk-morning-controller.service']
  require(parent['MainPID']==parent['ControlPID']=='0' and parent['Job']=='' and parent['ActiveState']=='inactive' and parent['SubState']=='dead')
  h.kernel_empty('schubert-nk-morning-controller.service');h.kernel_empty('schubert-nk-bootstrap-admin.service')
  require(not pathlib.Path('/proc/320189').exists())
  journal=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID='+INV,'-o','json','--no-pager'])
  j=[json.loads(l)for l in journal.splitlines()];verify_pid1(j)
  startup=pathlib.Path('/run/schubert-nk/startup');require(not any(p.name.endswith('.start.intent')for p in startup.iterdir()))
  for n in ['backup-request','cleanup-request','expiry-request']:require(not list(pathlib.Path('/run/schubert-nk',n).iterdir()))
  original=pathlib.Path('/var/lib/pgpt-s1-preservation/pg521-runtime-resume-v2/after.private.json').read_bytes()
  require(hashlib.sha256(original).hexdigest()=='f72d6c82d7ab352e415b3d9547ec83cf5c3a0a9d80a77a1d795720e8f9f8991e');old=json.loads(original)['rows']
  q="begin isolation level repeatable read read only;set local timezone='UTC';"
  for t in old:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
  q+='commit;';data={}
  for line in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines():
   r=json.loads(line);require(r['table']not in data);data[r['table']]=r['rows']
  require(set(data)==set(old));verify_batch(old['schubert.batch_runs'],data['schubert.batch_runs'])
  require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG495' and owner()==held)
  cfg={u:show(u,configuration_fields())for u in UNITS};signed_cfg=json.loads(original)['configuration']
  for u,v in cfg.items():
   expected=signed_cfg[u];require(set(v)==set(expected)and all(v[k]==expected[k]for k in v if k!='ExecStart'))
   left=exec_record(v['ExecStart']);right=exec_record(expected['ExecStart']);require(left is not None and right is not None and left[:3]==right[:3])
  return {'units':units,'configuration':cfg,'rows':data,'pid1':j,'startup':tree(startup),'originals':tree(pathlib.Path('/var/lib/schubert-nk/maintenance')),'backup':tree(pathlib.Path('/srv/schubert-nk/backup'))}
 def check_data(now):
  require(first is not None)
  require(all(now[k]==first[k]for k in first if k not in ['units','configuration']))
  for u,v in now['configuration'].items():
   old=first['configuration'][u];require(set(v)==set(old)and all(v[k]==old[k]for k in old if k!='ExecStart'))
   left=exec_record(v['ExecStart']);right=exec_record(old['ExecStart']);require(left is not None and right is not None and left[:3]==right[:3])
  for u,v in now['units'].items():
   old=first['units'][u]
   if u in stages:
    saved=json.loads((SAVE/(u+'.stopped.private')).read_bytes(),object_pairs_hook=h.unique);require(v==saved and h.terminal(v));h.kernel_empty(u)
   elif u=='artemis.service' and 'schubert-nk-cleanup.service'in stages and h.terminal(v):
    require(h.same_generation(old,v));h.kernel_empty(u) # Full vendor stop proof required at its ordered step.
   else:require(v==old)
 def save(name,v):
  with(SAVE/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 first=capture_data(True);require(first==capture_data(True));save('before.private.json',first)
 baseline=pathlib.Path('/var/lib/pgpt-s1-preservation/pg523-completed-readback-v1/after.private.json').read_bytes()
 require(hashlib.sha256(baseline).hexdigest()=='07b5dc48adeaa97f3aba60f47ba1086df847302fb962f4467504c832497a53ec')
 prior=json.loads(baseline)
 require(all(first[k]==prior[k]for k in prior if k!='rows'))
 verify_same_batch(prior['rows'],first['rows']['schubert.batch_runs'])
 h.parent_receipt();captures={u:first['units'][u]for u in h.ORDER};h.validate_live(captures);ticks={}
 for u,v in captures.items():
  if v['MainPID']!='0':
   ticks[u]=h.tick(v['MainPID']);require((pathlib.Path('/proc')/v['MainPID']/'cgroup').read_text()=='0::/system.slice/'+u+'\n')
  require(v==h.show(u) and h.holder()==held)
 h.save('stops-before.private',json.dumps(captures,sort_keys=True).encode());h.save('ticks-before.private',json.dumps(ticks,sort_keys=True).encode())
 print('REF_READY',flush=True)
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n').decode('ascii')
  require(action in ['before','terminal','release'] or action.startswith('stop:'))
  if action.startswith('stop:'):
   unit=action[5:];require(len(stages)<len(h.ORDER) and unit==h.ORDER[len(stages)]);check_data(capture_data(True))
   import contextlib
   with contextlib.redirect_stdout(sys.stderr):h.stop_one(unit,captures,ticks)
   stages.append(unit);check_data(capture_data(True))
  else:
   check_data(capture_data(action!='release'))
   if action in ['terminal','release']:
    require(stages==h.ORDER)
    for u in UNITS:require(h.terminal(show(u,FIELDS)));h.kernel_empty(u)
  if action=='release':
   save('after.private.json',capture_data(False))
   for u in reversed(refs):manager.UnrefUnit(u)
   bus.close();print('REF_RELEASED',flush=True);return
  print('REF_CHECKED',flush=True)
 raise ValueError('readonly owner channel ended')
if __name__=='__main__':
 try:main()
 except Exception as failure:
  import traceback
  print('REF_FAILED',flush=True);print('PG526_READBACK_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
  for frame in traceback.extract_tb(failure.__traceback__):
   if frame.filename==__file__:print('PG526_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
  while True:time.sleep(1)
