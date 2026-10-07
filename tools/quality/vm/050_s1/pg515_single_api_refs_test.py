"""Independent SSC209 namespace/stop fault oracles. No VM or live authority."""
import contextlib, copy, importlib.util, json, pathlib, sys, tempfile, types
from unittest.mock import patch
sys.modules.setdefault('dbus',types.SimpleNamespace())
import pg515_single_api_refs as h
count=0
h.revoked_phase=False
def check(v):
 global count
 count+=1
 if not v:raise AssertionError('single API independent oracle')
root='/run/schubert-nk/startup';epoch='31100027-4444-4333-8444-555555555555'
original={root:{'metadata':[28,1,0,0,16832,2,120,100,100],'sha256':None}}
for name in ['epoch.current',epoch+'.permit',epoch+'.owner',epoch+'.API.start.intent']:
 original[root+'/'+name]={'metadata':[28,len(original)+1,0,0,33152,1,0,100,100],'sha256':'b'*64}
check(h.startup_preserved(original,original))
after=copy.deepcopy(original);del after[root+'/'+epoch+'.API.start.intent'];after[root]['metadata'][6:]=[100,200,200]
check(h.startup_preserved(after,original))
for p in [None,{},dict(after,**{root+'/permit-start.intent':original[root]}),dict(after,**{root+'/'+epoch+'.WEB.start.intent':original[root]})]:check(not h.startup_preserved(p,original))
for path in after:
 for k in range(9):
  bad=copy.deepcopy(after);bad[path]['metadata'][k]+=1
  check(h.startup_preserved(bad,original)==(path==root and k in [6,7,8]))
 bad=copy.deepcopy(after);bad[path]['sha256']='a'*64;check(not h.startup_preserved(bad,original))
check(h.ORDER==['schubert-nk-expiry-cleanup.service','schubert-nk-cleanup.service','artemis.service'])
check(h.kernel_actor(['38602'],['','']))
for actors in [None,[],['38602','38602'],['38602','999'],['999'],{'38602'}]:check(not h.kernel_actor(actors,['']))
for children in [None,[],['999'],['','999'],[None],{' '}]:check(not h.kernel_actor(['38602'],children))
import pg515_confirm_ma as ma
args=[b'/opt/jdk-25.0.4/bin/java',b'-cp',b'/fixed/private/classes',b'Pg515SingleApiRecovery',b'recover',b'']
check(ma.actor_arguments(args))
for v in [None,[],args[:-1],args[:-2]+[b'verify',b''],[b'/foreign']+args[1:],args[:-3]+[b'Other',b'recover',b'']]:check(not ma.actor_arguments(v))
import os
row=['1:','FLOCK','ADVISORY','WRITE','777','00:01:123','0','EOF'];dev=os.makedev(0,1)
check(ma.lock_match(row,777,dev,123))
for k in range(1,6):
 v=list(row);v[k]='foreign';check(not ma.lock_match(v,777,dev,123))
for v in [None,[],row[:5]]:check(not ma.lock_match(v,777,dev,123))
# Import pure already-reviewed witness definitions only, never their runtime main or authorization.
here=pathlib.Path(__file__).parent
import ast
source=ast.parse((here/'pg481_native_owned_stop.py').read_text())
defs=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in {'terminal','same_generation','normal_terminal'}]
h.FIELDS=set('Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'.split(','))
exec(compile(ast.Module(body=defs,type_ignores=[]),'<pure terminal fixtures>','exec'),h.__dict__)
def cycle(unit,dependent=False,fault=None,foreign=False,missing_previous=False):
 events=[];failure=RuntimeError('independent injected fault')
 def event(name):
  events.append(name)
  if len(events)==fault:raise failure
 before={'Id':unit,'LoadState':'loaded','ActiveState':'active','SubState':'running' if unit=='artemis.service' else 'exited','Job':'','MainPID':'38602' if unit=='artemis.service' else '0','ControlPID':'0','InvocationID':'0608718743a74668a5e5bd87cf30f6b5' if unit=='artemis.service' else '1'*32,'Type':'simple' if unit=='artemis.service' else 'oneshot','Restart':'on-failure' if unit=='artemis.service' else 'no','RemainAfterExit':'no' if unit=='artemis.service' else 'yes','Result':'success','ExecMainCode':'0' if unit=='artemis.service' else '1','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'3965781145','ExecMainExitTimestampMonotonic':'0' if unit=='artemis.service' else '4186555892','KillMode':'control-group','SendSIGKILL':'no'}
 after={**before,'ActiveState':'inactive','SubState':'dead','MainPID':'0'}
 if unit=='artemis.service':after.update(ExecMainCode='1',ExecMainStatus='143',ExecMainExitTimestampMonotonic='6000000000')
 current=dict(after if dependent else before)
 if foreign:current['InvocationID']='f'*32
 realpath=pathlib.Path
 class Gone:
  def exists(self):return False
 with tempfile.TemporaryDirectory(prefix='pg513-stop-oracle-') as tmp,contextlib.ExitStack() as stack:
  saved=realpath(tmp)
  if not missing_previous:
   for u in h.ORDER[:h.ORDER.index(unit)]:(saved/(u+'.stopped.private')).touch()
  stack.enter_context(patch.object(h,'ROOT',saved));stack.enter_context(patch.object(h,'baseline',{'units':{unit:before}},create=True))
  stack.enter_context(patch.object(h,'owner',(777,888,{}),create=True))
  stack.enter_context(patch.object(h,'identity',lambda:event('identity')))
  stack.enter_context(patch.object(h,'holder',lambda:(event('holder') or (777,888,{}))))
  stack.enter_context(patch.object(h,'values',lambda:event('values')))
  stack.enter_context(patch.object(h,'actor',lambda u,v:event('actor')))
  stack.enter_context(patch.object(h,'kernel',lambda u:event('kernel'),create=True))
  stack.enter_context(patch.object(h,'show',lambda u,f:(event('show') or dict(current)),create=True))
  stack.enter_context(patch.object(h,'save',lambda n,d:event('save:'+n)))
  stack.enter_context(patch.object(h,'broker_stop',lambda b,a:event('brokerFullWitness')))
  def stop(args,**kwargs):event('STOP');current.update(after);return types.SimpleNamespace(returncode=0)
  stack.enter_context(patch.object(h,'subprocess',types.SimpleNamespace(run=stop,DEVNULL=-3)))
  stack.enter_context(patch.object(h,'pathlib',types.SimpleNamespace(Path=lambda p:Gone() if str(p)=='/proc/38602' else realpath(p))))
  try:h.stop(unit);return events,None
  except (RuntimeError,ValueError) as err:return events,err
for unit in h.ORDER:
 events,err=cycle(unit);check(err is None and events.count('STOP')==1)
 stop_at=events.index('STOP');after_kernel=[i for i,n in enumerate(events) if n=='kernel' and i>stop_at]
 check(events.index('save:'+unit+'.stop-reserved.private')<stop_at and after_kernel and after_kernel[0]<events.index('save:'+unit+'.stopped.private'))
 for fault in range(1,len(events)+1):
  failed,err=cycle(unit,fault=fault);check(isinstance(err,RuntimeError) and len(failed)==fault)
  check('save:'+unit+'.stopped.private' not in failed[:-1])
 events,err=cycle(unit,foreign=True);check(isinstance(err,ValueError) and 'STOP' not in events)
 if unit!=h.ORDER[0]:events,err=cycle(unit,missing_previous=True);check(isinstance(err,ValueError) and 'STOP' not in events)
events,err=cycle('artemis.service',dependent=True);check(err is None and 'STOP' not in events and 'brokerFullWitness' in events)
for fault in range(1,len(events)+1):
 failed,err=cycle('artemis.service',dependent=True,fault=fault);check(isinstance(err,RuntimeError) and 'STOP' not in failed)
# Independent SS343 textual canonical vector and phase-specific metadata.
raw=('NKEPOCH1\nstate=ISSUED\nboot_id='+epoch+'\nepoch_id='+epoch+'\nrun_id='+epoch+
 '\ncutoff_utc=2026-09-27T15:00:00.000000Z\nactivation_id='+epoch+'\npermit_sha256='+'b'*64+'\n').encode()
expected=raw.replace(b'state=ISSUED',b'state=INVALID').replace(b'permit_sha256='+b'b'*64,b'permit_sha256=-')
check(h.canonical_invalid(raw)==expected)
for invalid in [None,b'',b'corrupt',raw.replace(b'ISSUED',b'INVALID'),raw+b'foreign=1\n',raw.replace(b'permit_sha256=',b'permit_hash='),raw[:-1]]:
 try:h.canonical_invalid(invalid);raise AssertionError('invalid vector accepted')
 except ValueError:check(True)
h.revoked_phase=True;h.invalid_hash='f'*64;h.invalid_length=300
changed=copy.deepcopy(original);current=root+'/epoch.current'
changed[current]['metadata'][1]=777;changed[current]['metadata'][6:]=[300,201,202];changed[current]['sha256']='f'*64
check(h.startup_preserved(changed,original))
for k in range(9):
 bad=copy.deepcopy(changed);bad[current]['metadata'][k]+=1
 check(h.startup_preserved(bad,original)==(k in [1,7,8]))
for path in changed:
 if path in [root,current]:continue
 bad=copy.deepcopy(changed);bad[path]['sha256']='a'*64;check(not h.startup_preserved(bad,original))
h.revoked_phase=False;check(not h.startup_preserved(changed,original))
print('PG515_REFERENCE_ORACLE independentAssertions='+str(count)+' orderedStopAndFault=true dependentStopNotReissued=true vmActions0=true productionPT0=true')
