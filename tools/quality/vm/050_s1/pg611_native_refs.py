"""Current genuine parent DONE/independent all-column batch oracle; ten held Ref readback."""
import ast,datetime,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
import dbus
from pg611_durable import save as durable_save
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg611-native-stop-v1')
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441';INV='5a1acaa0c35e484c979401e3b6dfb36a'
START=86264628081;END=87761979588
BASELINE_SHA='8d9888702641b29b9feff811cebc94f86d97de96330a43fb0c29c6959f98bf47'
def require(v):
 if not v:raise ValueError('fixed completed readback refused')
def same_value(left,right):
 if type(left)is not type(right):return False
 if isinstance(left,dict):return set(left)==set(right) and all(type(k)is str and same_value(left[k],right[k])for k in left)
 if isinstance(left,list):return len(left)==len(right) and all(same_value(a,b)for a,b in zip(left,right))
 return type(left)in (type(None),bool,int,float,str) and left==right
def verify_pid1(rows):
 from pg611_parent_receipt import completed
 done=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/970bbce1-6bba-4db0-ace1-680ee7dfde92.done').read_bytes()
 require(completed(rows,done)['endMonotonicUs']==END)
def main():
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='stop' and sys.argv[2].isdigit());backend=int(sys.argv[2]);os.umask(0o077)
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 source=ast.parse(raw);names={'command','metadata','strict','owner','show','tree','configuration_fields'}
 definitions=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names];require(len(definitions)==len(names))
 constants=[n for n in source.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
 class Fixed(ast.NodeTransformer):
  def visit_Constant(self,n):
   return ast.copy_location(ast.Constant(b'Pg611NativeStop'),n)if n.value==b'Pg480BackupRecovery'else n
 code=Fixed().visit(ast.Module(body=constants+definitions,type_ignores=[]));ast.fix_missing_locations(code)
 sealed={'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'pathlib':pathlib,'re':re,'stat':stat,'subprocess':subprocess,'sys':sys,'time':time,'require':require,'BOOT':BOOT}
 exec(compile(code,'<fixed readonly owner witness>','exec'),sealed)
 command,metadata,owner,show,tree,configuration_fields=(sealed[n]for n in('command','metadata','owner','show','tree','configuration_fields'))
 UNITS,FIELDS=sealed['UNITS'],sealed['FIELDS']
 parser=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 node=next(n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');exec(compile(ast.Module(body=[node],type_ignores=[]),'<fixed declaration parser>','exec'),sealed);exec_record=sealed['exec_record']
 require(SAVE.is_dir() and metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2] and {p.name for p in SAVE.iterdir()}=={'refs-prepare.private.log'})
 held=owner();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 def connection(present):
  q="select count(*) from pg_stat_activity a where a.pid="+str(backend)+" and a.usename='schubert_batch' and a.datname='schubert_nk' and a.application_name='PG611-native-stop' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted);select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_backup') and pid<>"+str(backend)+";"
  require(command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'1'if present else b'0',b'0'])
  if not present:
   require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',"select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"],4096).splitlines()==[b'0',b'0'])
 import pg611_native_owned_stop as h
 require(h.ROOT==SAVE and h.BOOT==BOOT)
 stages=[];captures=None;first=None
 def capture_data(present):
  require(owner()==held and h.holder()==held);connection(present)
  units={u:show(u,FIELDS)for u in UNITS}
  parent=units['schubert-nk-morning-controller.service']
  require(parent['MainPID']==parent['ControlPID']=='0' and parent['Job']=='' and parent['ActiveState']=='inactive' and parent['SubState']=='dead')
  h.kernel_empty('schubert-nk-morning-controller.service');h.kernel_empty('schubert-nk-bootstrap-admin.service')
  require(not pathlib.Path('/proc/1207482').exists())
  journal=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID='+INV,'-o','json','--no-pager'])
  j=[json.loads(l)for l in journal.splitlines()];verify_pid1(j)
  startup=pathlib.Path('/run/schubert-nk/startup');require(not any(p.name.endswith('.start.intent')for p in startup.iterdir()))
  for n in ['backup-request','cleanup-request','expiry-request']:require(not list(pathlib.Path('/run/schubert-nk',n).iterdir()))
  original=pathlib.Path('/var/lib/pgpt-s1-preservation/pg609-completed-readonly-v1/before.private.json').read_bytes()
  require(hashlib.sha256(original).hexdigest()==BASELINE_SHA);old=json.loads(original)['rows']
  q="begin isolation level repeatable read read only;set local timezone='UTC';"
  for t in old:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
  q+='commit;';data={}
  for line in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines():
   r=json.loads(line);require(r['table']not in data);data[r['table']]=r['rows']
  require(set(data)==set(old) and same_value(data,old))
  require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG600' and owner()==held)
  cfg={u:show(u,configuration_fields())for u in UNITS};signed_cfg=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg604-completed-activate-v1/after.private.json').read_bytes())['configuration']
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
   elif u in ('artemis.service','schubert-nk-expiry-cleanup.service') and 'schubert-nk-cleanup.service'in stages and h.terminal(v):
    require(h.same_generation(old,v));h.kernel_empty(u)
    if u=='schubert-nk-expiry-cleanup.service':require(h.normal_terminal(old,v))
    # Broker full vendor journal remains mandatory at its ordered stage; no repeated stop.
   else:require(v==old)
 def save(name,v):
  durable_save(SAVE,name,json.dumps(v,sort_keys=True).encode())
 first=capture_data(True);require(first==capture_data(True));save('before.private.json',first)
 baseline=pathlib.Path('/var/lib/pgpt-s1-preservation/pg609-completed-readonly-v1/before.private.json').read_bytes()
 require(hashlib.sha256(baseline).hexdigest()==BASELINE_SHA)
 prior=json.loads(baseline)
 require(prior['source']=='23b14a44b10504172e030bbd6625926bf049fb5c' and prior['manifestSha256']=='a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f')
 require(first['units']==prior['units'] and same_value(first['rows'],prior['rows']) and first['pid1']==prior['pid1'] and first['startup']==prior['trees']['startup'] and first['originals']==prior['trees']['originals'] and first['backup']==prior['trees']['backup'])
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
  print('REF_FAILED',flush=True);print('PG611_READBACK_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
  for frame in traceback.extract_tb(failure.__traceback__):
   if frame.filename==__file__:print('PG611_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
  while True:time.sleep(1)
