"""Literal current stop/dependency vectors; no runtime actions or Production PT credit."""
import copy,json,pathlib,tempfile,types,contextlib
from unittest.mock import patch
import pg471_native_owned_stop as h
count=0
def check(ok):
 global count
 count+=1
 if not ok:raise AssertionError('stop vector '+str(count))
def b(unit):return {'Id':unit,'LoadState':'loaded','ActiveState':'active','SubState':'running','Job':'','MainPID':'42','ControlPID':'0','InvocationID':'a'*32,'Type':'simple','Restart':'no','RemainAfterExit':'no','Result':'success','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'100','ExecMainExitTimestampMonotonic':'0','KillMode':'control-group','SendSIGKILL':'no'}
before=b('artemis.service');after={**before,'ActiveState':'inactive','SubState':'dead','MainPID':'0','ExecMainCode':'1','ExecMainStatus':'143','ExecMainExitTimestampMonotonic':'200'}
rows=[{'__CURSOR':'literal-1','__MONOTONIC_TIMESTAMP':'150','__REALTIME_TIMESTAMP':'1791178000000000','_BOOT_ID':'e07aa7061acd4e65b309d7f330f79d54','_SYSTEMD_UNIT':'artemis.service','_SYSTEMD_INVOCATION_ID':'a'*32,'PRIORITY':'6','MESSAGE':'AMQ221002: Apache Artemis Message Broker version 2.56.0 stopped, uptime 1h'}]
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
 with tempfile.TemporaryDirectory(prefix='pg471-native-control-') as tmp,contextlib.ExitStack() as stack:
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
print('PG471_STOP_ORACLE independentAssertions='+str(count)+' nativeMutation0=true productionPT0=true')

# Literal current cohort, separate from tested EXPECTED constants.
captures={u:b(u) for u in ['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service']}
for u,pid,inv in [('caddy.service','2273164','d3f960c22ef2455386519d18146139a8'),('schubert-nk-web.service','2267460','a0e695e907204a7eaf84ae16013493ad'),('schubert-nk-api.service','2265107','8d6e47b48a58468aaac34643bbeddb16'),('artemis.service','2145457','3e037033f5cd4cbd8ce1c9f8160f1238')]:
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
print('PG471_NATIVE_CONTROL_COMPLETE independentAssertions='+str(count)+' nativeMutation0=true')
