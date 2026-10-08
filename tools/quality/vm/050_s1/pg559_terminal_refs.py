"""SSC214/215/223: fresh normal all-terminal readback; no operational action."""
import ast,datetime,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
import dbus
from pg529_dependency_graph import dependency_graph
from pg556_parent_receipt import completed
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg559-terminal-readback-v1')
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
PRESERVED=pathlib.Path('/var/lib/pgpt-s1-preservation/pg558-current-owned-handoff-v1')
BASE_SHA='51c4c14e2828fca4bf0703cbc8db2cab2feddb3e1b02af4da8b202b2f8e23cb1'
COMPLETE_SHA='0f673d9bdfb1ebf02faeb91c1c11acdeb0530f7bc0737ea27811f8e84d090754'
def require(value):
 if not value:raise ValueError('current fresh terminal readback refused')
def same_value(before,actual):
 if type(before)is not type(actual):return False
 if type(before)is dict:return set(before)==set(actual)and all(type(k)is str and same_value(before[k],actual[k])for k in before)
 if type(before)is list:return len(before)==len(actual)and all(same_value(a,b)for a,b in zip(before,actual))
 return type(before)in (type(None),str,int,float,bool)and before==actual
def same_rows(before,actual):
 if type(before)is not dict or type(actual)is not dict or len(before)!=24 or set(before)!=set(actual):return False
 return all(type(before[t])is list and type(actual[t])is list and same_value(before[t],actual[t])for t in before)
def peer_query(backend):
 require(type(backend)is int and 1<backend<=2147483647)
 fixed=str(backend)
 return ("select count(*) from pg_stat_activity where pid="+fixed+";"
  "select count(*) from pg_stat_activity a where a.pid="+fixed+" and a.usename='schubert_batch' and a.datname='schubert_nk' and a.application_name='PG559-terminal-readback' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted);"
  "select count(*) from pg_stat_activity where datname='schubert_nk' and backend_type='client backend' and pid not in ("+fixed+",pg_backend_pid());"
  "select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;")
def peer_counts_valid(present,lines):
 return type(present)is bool and type(lines)is list and lines==([b'1',b'1',b'0',b'1']if present else[b'0',b'0',b'0',b'0'])
def main():
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='readback'and sys.argv[2].isdigit());backend=int(sys.argv[2]);os.umask(0o077)
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 parsed=ast.parse(raw);names={'command','metadata','strict','owner','show','tree','configuration_fields','kernel'}
 definitions=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in names];require(len(definitions)==len(names))
 constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
 class Fixed(ast.NodeTransformer):
  def visit_Constant(self,n):return ast.copy_location(ast.Constant(b'Pg559TerminalReadback'),n)if n.value==b'Pg480BackupRecovery'else n
 code=Fixed().visit(ast.Module(body=constants+definitions,type_ignores=[]));ast.fix_missing_locations(code)
 sealed={'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'pathlib':pathlib,'re':re,'stat':stat,'subprocess':subprocess,'sys':sys,'time':time,'require':require}
 exec(compile(code,'<sealed current owner>','exec'),sealed)
 command,metadata,strict,owner,show,tree,cfg,kernel,units,fields=(sealed[n]for n in ('command','metadata','strict','owner','show','tree','configuration_fields','kernel','UNITS','FIELDS'))
 require(SAVE.is_dir()and metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2]and {p.name for p in SAVE.iterdir()}=={'refs-prepare.private.log'})
 base_raw=strict(PRESERVED/'before.private.json',0o600,33554432);require(hashlib.sha256(base_raw).hexdigest()==BASE_SHA);baseline=json.loads(base_raw)
 complete_raw=strict(PRESERVED/'complete.private.json',0o600,4096);require(hashlib.sha256(complete_raw).hexdigest()==COMPLETE_SHA and all(v is True for v in json.loads(complete_raw).values()))
 require(len(baseline['units'])==10 and len(baseline['rows'])==24 and baseline['runtimeAbsent']is True)
 require(all(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',t)for t in baseline['rows']))
 held=owner();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
 for u in units:manager.RefUnit(u);refs.append(u)
 def connection(present):
  require(peer_counts_valid(present,command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',peer_query(backend)],4096).splitlines()))
 def snapshot(present):
  require(owner()==held);connection(present)
  current={u:show(u,fields)for u in units};require(current==baseline['units'])
  for u,v in current.items():require(v['MainPID']==v['ControlPID']=='0'and v['Job']==''and v['ActiveState']in('inactive','failed'));kernel(u)
  require(not any(pathlib.Path('/proc',str(p)).exists()for p in (581443,845625,848145,854439,705321,900001,900030)))
  configuration={u:show(u,cfg())for u in units};require(configuration==baseline['configuration'])
  dependencies=dependency_graph({u:show(u,{'Requires','Before','After','PartOf','BindsTo'})for u in units},units);require(dependencies==baseline['dependencies'])
  pid1={}
  for u,expected in baseline['pid1Stop'].items():
   require(type(expected)is list and len(expected)==1)
   rows=[json.loads(l)for l in command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+u,'-o','json','--no-pager']).splitlines()]
   actual=[r for r in rows if r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286'and r.get('JOB_ID')==expected[0]['JOB_ID']and r.get('JOB_TYPE')=='stop'and r.get('JOB_RESULT')=='done'];require(actual==expected);pid1[u]=actual
  journal=[json.loads(l)for l in command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=075ad6644b284056a6cccf7af252519b','-o','json','--no-pager']).splitlines()]
  done=strict(pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/12f1af04-180e-405c-8738-853bbd875443.done'),0o600,4096)
  require(completed(journal,done)['endMonotonicUs']==46382089521)
  q="begin isolation level repeatable read read only;set local timezone='UTC';";data={}
  for t in baseline['rows']:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from(select to_jsonb(t)j from "+t+" t)q;"
  for line in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
   row=json.loads(line);require(row['table']not in data);data[row['table']]=row['rows']
  require(same_rows(baseline['rows'],data))
  trees={k:tree(pathlib.Path(p))for k,p in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup'),('native','/run/schubert-nk/pt-coverage'),('oldProofs','/var/lib/pgpt-s1-preservation/pg557-native-stop-v1')]};require(all(v==baseline[k]for k,v in trees.items()))
  broker_raw=strict(PRESERVED/'broker-full-journal.private.jsonl',0o600,4194304);require(hashlib.sha256(broker_raw).hexdigest()=='5bc1c91076d2ce950bcc4f231d02a53b5ad944d0c18f65931f6308c40844bdae')
  broker_current=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+baseline['units']['artemis.service']['InvocationID'],'-o','json','--no-pager']);require([json.loads(l)for l in broker_raw.splitlines()]==[json.loads(l)for l in broker_current.splitlines()])
  require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf').exists())
  require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG548')
  require(current=={u:show(u,fields)for u in units}and owner()==held);connection(present)
  return {'units':current,'configuration':configuration,'rows':data,'dependencies':dependencies,'pid1Stop':pid1,'parentPid1':journal,'runtimeAbsent':True,**trees}
 def save(name,value):
  with (SAVE/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 before=snapshot(True);require(before==snapshot(True));save('before.private.json',before);print('REF_READY',flush=True)
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n').decode('ascii');require(action in ('before','release'));require(snapshot(action!='release')==before)
  if action=='release':
   save('after.private.json',before)
   for u in reversed(refs):manager.UnrefUnit(u)
   bus.close();print('REF_RELEASED',flush=True);return
  print('REF_CHECKED',flush=True)
 raise ValueError('new owner reference channel ended')
if __name__=='__main__':
 try:main()
 except Exception as failure:
  import traceback
  print('REF_FAILED',flush=True);print('PG559_READBACK_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
  for frame in traceback.extract_tb(failure.__traceback__):
   if frame.filename==__file__:print('PG559_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
  while True:time.sleep(1)
