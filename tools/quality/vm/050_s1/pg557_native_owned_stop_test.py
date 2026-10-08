"""Literal current stop/dependency vectors; no runtime actions or Production PT credit."""
import copy,json,pathlib,tempfile,types,contextlib
from unittest.mock import patch
import pg557_native_owned_stop as h
count=0
def check(ok):
 global count
 count+=1
 if not ok:raise AssertionError('stop vector '+str(count))
def b(unit):return {'Id':unit,'LoadState':'loaded','ActiveState':'active','SubState':'running','Job':'','MainPID':'42','ControlPID':'0','InvocationID':'a'*32,'Type':'simple','Restart':'no','RemainAfterExit':'no','Result':'success','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'100','ExecMainExitTimestampMonotonic':'0','KillMode':'control-group','SendSIGKILL':'no'}
before=b('artemis.service');after={**before,'ActiveState':'inactive','SubState':'dead','MainPID':'0','ExecMainCode':'1','ExecMainStatus':'143','ExecMainExitTimestampMonotonic':'200'}
rows=[{'__CURSOR':'literal-1','__MONOTONIC_TIMESTAMP':'150','__REALTIME_TIMESTAMP':'1791178000000000','_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_SYSTEMD_UNIT':'artemis.service','_SYSTEMD_INVOCATION_ID':'a'*32,'PRIORITY':'6','MESSAGE':'AMQ221002: Apache Artemis Message Broker version 2.56.0 stopped, uptime 1h'}]
def raw(v):return ('\n'.join(json.dumps(x) for x in v)+'\n').encode()
check(h.broker_witness(before,after,raw(rows))['vendorStopData'])
def denied(bv,av,r):
 try:h.broker_witness(bv,av,r)
 except (ValueError,TypeError,UnicodeDecodeError):check(True);return
 raise AssertionError('invalid broker accepted')
for k in ['Id','LoadState','InvocationID','ExecMainStartTimestampMonotonic','Type','Restart','RemainAfterExit','KillMode','SendSIGKILL','ActiveState','SubState','Result','MainPID','ControlPID','Job','ExecMainCode','ExecMainStatus']:
 for value in ['foreign',None]:
  bad=dict(after);bad[k]=value;denied(before,bad,raw(rows))
for k in before:
 for side in ['before','after']:
  x=dict(before);y=dict(after);del (x if side=='before' else y)[k];denied(x,y,raw(rows))
  x=dict(before);y=dict(after);(x if side=='before' else y)[k]=None;denied(x,y,raw(rows))
for k,value in [('Id','other.service'),('LoadState','not-found'),('ActiveState','failed'),('SubState','other'),('Result','timeout'),('MainPID','0'),('ControlPID','1'),('Job','99'),('ExecMainCode','1'),('ExecMainStatus','143'),('ExecMainExitTimestampMonotonic','200')]:
 bad=dict(before);bad[k]=value;denied(bad,after,raw(rows))
for k in rows[0]:
 v=copy.deepcopy(rows);del v[0][k];denied(before,after,raw(v))
for k,value in [('_BOOT_ID','0'*32),('_SYSTEMD_UNIT','other.service'),('_SYSTEMD_INVOCATION_ID','b'*32),('PRIORITY','3'),('__CURSOR',''),('__MONOTONIC_TIMESTAMP','99'),('__MONOTONIC_TIMESTAMP','201'),('MESSAGE','AMQ224000: ERROR'),('MESSAGE','other normal message')]:
 v=copy.deepcopy(rows);v[0][k]=value;denied(before,after,raw(v))
for v in [None,b'',b'\xff\n',b'{}\n',raw(rows).rstrip(b'\n'),raw(rows+rows),b' '*4194305]:denied(before,after,v)
for value in ['100','200']:
 v=copy.deepcopy(rows);v[0]['__MONOTONIC_TIMESTAMP']=value;check(h.broker_witness(before,after,raw(v))['rows']==1)
def run_stop(dependent=False,fault=None):
 events=[];unit='artemis.service';captures={u:b(u) for u in h.ORDER};captures[unit]=before;current=dict(after if dependent else before);error=RuntimeError('literal fault')
 def event(name):
  events.append(name)
  if fault==len(events):raise error
 def show(u):event('show');return dict(current)
 def stop(args,**kw):event('STOP');current.update(after);return types.SimpleNamespace(returncode=0)
 def saved(name,data):event('save:'+name)
 with tempfile.TemporaryDirectory(prefix='pg475-native-control-') as tmp,contextlib.ExitStack() as stack:
  root=pathlib.Path(tmp)
  for prior in h.ORDER[:-1]:(root/(prior+'.stopped.private')).touch()
  stack.enter_context(patch.object(h,'ROOT',root));stack.enter_context(patch.object(h,'holder',lambda:(event('holder') or (777,123))))
  stack.enter_context(patch.object(h,'show',show));stack.enter_context(patch.object(h,'tick',lambda pid:(event('tick') or 456)))
  stack.enter_context(patch.object(h,'kernel_empty',lambda unit:event('kernel')));stack.enter_context(patch.object(h,'save',saved))
  stack.enter_context(patch.object(h,'command',lambda args:(event('journal') or raw(rows))))
  stack.enter_context(patch.object(h,'subprocess',types.SimpleNamespace(run=stop,DEVNULL=-3)))
  realPath=pathlib.Path
  class Proc:
   def __truediv__(self,key):return self
   def read_text(self):return '0::/system.slice/artemis.service\n'
   def exists(self):return False
  stack.enter_context(patch.object(h,'pathlib',types.SimpleNamespace(Path=lambda value:Proc() if str(value)=='/proc' else realPath(value))))
  try:h.stop_one(unit,captures,{'artemis.service':456});return events,None
  except RuntimeError as actual:check(actual is error);return events,actual
for dependent in [False,True]:
 events,error=run_stop(dependent);check(error is None)
 check(events.count('STOP')==(0 if dependent else 1))
 if not dependent:check(events.index('save:artemis.service.stop-reserved.private')<events.index('STOP'))
 check(events.index('journal')<events.index('save:artemis.service.stopped.private'))
 for at in range(1,len(events)+1):
  failed,error=run_stop(dependent,at);check(error is not None and len(failed)==at)
  check('save:artemis.service.stopped.private' not in failed[:-1])
check(h.ORDER==['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service'])
print('PG557_STOP_ORACLE independentAssertions='+str(count)+' nativeMutation0=true productionPT0=true')

# Literal current cohort, separate from tested EXPECTED constants.
captures={u:b(u) for u in ['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service']}
for u,pid,inv in [('caddy.service','854439','976e35e6b8eb47f889d99bd5f4e34fd5'),('schubert-nk-web.service','848145','3bcfbad981e64d8fadda66f27d1994fa'),('schubert-nk-api.service','845625','0df039719b644400b1da023c6cc604eb'),('artemis.service','705321','fb112c36889c4311a67f9f80de7dd746')]:
 captures[u].update(MainPID=pid,InvocationID=inv)
h.validate_live(captures);check(True)
for unit in ['caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service']:
 for key,value in [('MainPID','1'),('InvocationID','b'*32),('ActiveState','failed'),('SubState','start'),('Job','1'),('ControlPID','1'),('Result','failed'),('ExecMainStatus','143'),('Id','foreign'),('LoadState','missing')]:
  bad=copy.deepcopy(captures);bad[unit][key]=value
  try:h.validate_live(bad)
  except ValueError:check(True)
  else:raise AssertionError('wrong cohort accepted')
for bad in [None,{}, {u:v for u,v in captures.items() if u!='artemis.service'}]:
 try:h.validate_live(bad)
 except ValueError:check(True)
 else:raise AssertionError('missing cohort accepted')
print('PG557_NATIVE_CONTROL_COMPLETE independentAssertions='+str(count)+' nativeMutation0=true')

# Fixed PID1 receipt oracle: GC'd Unit counters are not a substitute for job done.
parent_rows=[{'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd','INVOCATION_ID':'075ad6644b284056a6cccf7af252519b','__MONOTONIC_TIMESTAMP':'46382089521','MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','JOB_ID':'59402','JOB_TYPE':'start','JOB_RESULT':'done'},
 {'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd','INVOCATION_ID':'075ad6644b284056a6cccf7af252519b','__MONOTONIC_TIMESTAMP':'46382089297','MESSAGE_ID':'7ad2d189f7e94e70a38c781354912448'}]
declaration='Type=oneshot\nSuccessExitStatus=\nActiveState=inactive\nSubState=dead\nMainPID=0\nControlPID=0\nJob=\nResult=success\nInvocationID=\n'
def parent_case(v,config=declaration):
 outputs=[]
 with patch.object(h,'holder',lambda:(777,123)),patch.object(h,'kernel_empty',lambda unit:None),patch.object(h,'save',lambda n,d:outputs.append(n)),patch.object(h,'command',lambda args:raw(v) if 'journalctl' in args[0] else config.encode()):
  h.parent_receipt()
 return outputs
check(parent_case(parent_rows)==['parent.private.jsonl','parent.normal.private'])
for key,value in [('_BOOT_ID','0'*32),('_PID','2'),('_UID','1'),('_COMM','other'),('INVOCATION_ID','a'*32),('__MONOTONIC_TIMESTAMP','46678901763'),('JOB_ID','59403'),('JOB_TYPE','stop'),('JOB_RESULT','failed'),('MESSAGE_ID','other')]:
 bad=copy.deepcopy(parent_rows);bad[0][key]=value
 try:parent_case(bad)
 except ValueError:check(True)
 else:raise AssertionError('foreign parent receipt accepted')
for bad in [[],parent_rows[:1],parent_rows[1:],parent_rows+parent_rows]:
 try:parent_case(bad)
 except ValueError:check(True)
 else:raise AssertionError('missing or duplicate receipt accepted')
for old,new in [('Type=oneshot','Type=simple'),('SuccessExitStatus=\n','SuccessExitStatus=143\n'),('MainPID=0','MainPID=1'),('ActiveState=inactive','ActiveState=active'),('Result=success','Result=timeout')]:
 try:parent_case(parent_rows,declaration.replace(old,new))
 except ValueError:check(True)
 else:raise AssertionError('invalid parent declaration accepted')
print('PG557_PARENT_RECEIPT_ORACLE independentAssertions='+str(count)+' nativeMutation0=true')
