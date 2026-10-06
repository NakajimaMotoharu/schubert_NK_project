"""REC204 literal/fault vectors. No VM action and no Production PT credit."""
import contextlib,copy,json,pathlib,tempfile,types
from unittest.mock import patch
import pg496_timeout_owned as h
count=0
def check(value):
 global count
 count+=1
 if not value:raise AssertionError('REC204 vector '+str(count))
parent={'Id':'schubert-nk-morning-controller.service','LoadState':'loaded','ActiveState':'failed','SubState':'failed','MainPID':'0','ControlPID':'0','Job':'','InvocationID':'52accf6d68f44487b6e0b3635c20396f','ExecMainCode':'1','ExecMainStatus':'143','Result':'timeout','ExecMainStartTimestampMonotonic':'255346663838','ExecMainExitTimestampMonotonic':'257146663838','KillMode':'control-group','SendSIGKILL':'no','Restart':'no','Type':'oneshot','RemainAfterExit':'no'}
check(h.parent_value(parent));check(not h.parent_value(None))
for key in parent:
 for value in ['foreign',None,1]:
  v=dict(parent);v[key]=value
  if key in ['ExecMainExitTimestampMonotonic','KillMode','SendSIGKILL','Restart','Type','RemainAfterExit'] and value=='foreign':continue
  check(not h.parent_value(v))
 v=dict(parent);del v[key];check(not h.parent_value(v))
for extra in ['unknown','intent']:
 v=dict(parent);v[extra]='';check(not h.parent_value(v))
epoch=b'NKEPOCH1\nstate=INVALID\nboot_id=e07aa706-1acd-4e65-b309-d7f330f79d54\nepoch_id=4d35762d-54b4-4187-ab03-cc9b7e9e3baf\nrun_id=91a748b4-1abe-484c-9682-44f46429b324\ncutoff_utc=2026-10-06T12:06:14.564793Z\nactivation_id=179758d2-5b77-443a-a743-bf0065e732ea\npermit_sha256=-\n'
check(h.epoch_value(epoch,True));check(not h.epoch_value(epoch,False))
issued=epoch.replace(b'state=INVALID',b'state=ISSUED').replace(b'permit_sha256=-',b'permit_sha256='+b'1'*64)
check(h.epoch_value(issued,False));check(not h.epoch_value(issued,True))
for field in epoch.splitlines()[1:]:
 check(not h.epoch_value(epoch.replace(field+b'\n',b''),True))
 check(not h.epoch_value(epoch+field+b'\n',True))
 check(not h.epoch_value(epoch.replace(field,field.split(b'=')[0]+b'=foreign'),True))
for raw in [None,b'',epoch[:-1],b'\xff\n',epoch+b'unknown=x\n',issued.replace(b'1'*64,b'G'*64),issued.replace(b'1'*64,b'1'*63)]:check(not h.epoch_value(raw,True if raw is not issued else False))
check(h.ORDER==['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service'])
check(h.EXTRA==['schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service'])
check(h.EXPECTED=={'caddy.service':('4113865','b656fdfe067a4cb8a542708750af019c',25667027),'schubert-nk-web.service':('4108080','1dedba9e9ee648fb94eca6232385e018',25663790),'schubert-nk-api.service':('4105598','730085ab1173444b83c9bf2c8127c94e',25662174),'artemis.service':('3939714','12360e619aa7445684692c59badc7c51',25552139)})
def caddy_stop(fault=None,foreign=False,missing_predecessor=False,dependent=False):
 events=[];error=RuntimeError('literal fault');unit='caddy.service'
 before={'Id':unit,'LoadState':'loaded','ActiveState':'active','SubState':'running','MainPID':'4113865','ControlPID':'0','Job':'','InvocationID':'b656fdfe067a4cb8a542708750af019c','ExecMainCode':'0','ExecMainStatus':'0','Result':'success','ExecMainStartTimestampMonotonic':'256670270000','ExecMainExitTimestampMonotonic':'0','KillMode':'control-group','SendSIGKILL':'no','Restart':'no','Type':'simple','RemainAfterExit':'no'}
 after={**before,'ActiveState':'inactive','SubState':'dead','MainPID':'0','ExecMainCode':'1','ExecMainStatus':'0','ExecMainExitTimestampMonotonic':'257200000000'};current=dict(before)
 if dependent:current=dict(after)
 if foreign:current['InvocationID']='f'*32
 def event(name):
  events.append(name)
  if len(events)==fault:raise error
 def show(u):event('show');return dict(current)
 def stop(args,**kw):event('STOP');current.update(after);return types.SimpleNamespace(returncode=0)
 real_path=pathlib.Path
 class Proc:
  def __truediv__(self,key):return self
  def exists(self):return False
 with tempfile.TemporaryDirectory(prefix='pg496-oracle-') as tmp,contextlib.ExitStack() as s:
  root=real_path(tmp);(root/'units-before.private.json').write_text(json.dumps({unit:before}))
  s.enter_context(patch.object(h,'ROOT',root));s.enter_context(patch.object(h,'holder',lambda:(event('holder') or (777,123))))
  s.enter_context(patch.object(h,'parent',lambda:event('parent')));s.enter_context(patch.object(h,'show',show))
  s.enter_context(patch.object(h,'actor',lambda u,v:event('actor')));s.enter_context(patch.object(h,'kernel_empty',lambda u:event('kernel')))
  s.enter_context(patch.object(h,'save',lambda name,data:event('save:'+name)))
  s.enter_context(patch.object(h,'subprocess',types.SimpleNamespace(run=stop,DEVNULL=-3)))
  s.enter_context(patch.object(h,'pathlib',types.SimpleNamespace(Path=lambda value:Proc() if str(value)=='/proc' else real_path(value))))
  try:h.stop_one('schubert-nk-web.service' if missing_predecessor else unit);return events,None
  except (RuntimeError,ValueError) as failure:return events,failure
events,error=caddy_stop();check(error is None and events.count('STOP')==1)
check(events.index('save:caddy.service.stop-reserved.private')<events.index('STOP'))
check(events.index('STOP')<events.index('kernel')<events.index('save:caddy.service.stopped.private'))
for at in range(1,len(events)+1):
 failed,error=caddy_stop(at);check(isinstance(error,RuntimeError) and len(failed)==at)
 check('save:caddy.service.stopped.private' not in failed[:-1])
for kwargs in [{'foreign':True},{'missing_predecessor':True}]:
 failed,error=caddy_stop(**kwargs);check(isinstance(error,ValueError) and 'STOP' not in failed)
events,error=caddy_stop(dependent=True);check(error is None and 'STOP' not in events and 'save:caddy.service.stop-reserved.private' not in events)
check(events.index('kernel')<events.index('save:caddy.service.stopped.private'))
for at in range(1,len(events)+1):
 failed,error=caddy_stop(at,dependent=True);check(isinstance(error,RuntimeError) and len(failed)==at)
 check('STOP' not in failed and 'save:caddy.service.stopped.private' not in failed[:-1])
events,error=caddy_stop(dependent=True,foreign=True);check(isinstance(error,ValueError) and 'STOP' not in events)
print('PG496_PYTHON_ORACLE independentAssertions='+str(count)+' nativeMutation0=true productionPT0=true')
