"""Operator phase fault/order tests: in-memory managers only, never VM/process actions or PT credit."""
import copy,contextlib,pathlib,subprocess,tempfile,types
from unittest.mock import patch
import pg466_handoff as h
count=0
def check(b):
    global count
    count+=1
    if not b:raise AssertionError('handoff control vector '+str(count))
def fixture(fault=None):
    events=[];states={};injected=RuntimeError('fixed phase fault')
    def event(name):
        events.append(name)
        if fault is not None and len(events)==fault:raise injected
    for unit in h.ALL:
        live=unit in ('schubert-nk-api.service','artemis.service')
        states[unit]={'Id':unit,'ControlPID':'0','Job':'','Result':'success','MainPID':'1338494' if unit=='schubert-nk-api.service' else '1227864' if live else '0','InvocationID':'9269078370384fdaab05ca9a0fcd50bd' if unit=='schubert-nk-api.service' else 'c784737af61e48778d0c8fa2c4f68037' if live else 'a'*32,'ActiveState':'active' if live or unit in ('schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service') else 'inactive','SubState':'running' if live else 'exited'}
    def holder():event('holder');return {'locks':{'maintenance.lock':[0,28,1974],'startup-admission.lock':[0,28,1975]},'oldCloseUnknown':True}
    def show(unit):event('show:'+unit);return copy.deepcopy(states[unit])
    def stop(args,**kw):
        unit=args[-1];event('STOP:'+unit);states[unit].update(MainPID='0',ControlPID='0',Job='',ActiveState='failed' if unit=='schubert-nk-api.service' else 'inactive',Result='exit-code' if unit=='schubert-nk-api.service' else 'success');return subprocess.CompletedProcess(args,0)
    changes={'holder':holder,'show':show,'empty_kernel':lambda unit:event('kernel:'+unit),'readback':lambda mode,label:event('readback:'+mode+':'+label),'save':lambda name,data:event('save:'+name),'web_stopped':lambda:(b'literal web capture',{'ordinaryStopData':True}), 'command':lambda args,**kw:b'literal API capture','witness':lambda *args:{'ordinaryStopData':True,'unitSuccess':False,'oldToolCloseSuccess':False},'all_terminal':lambda:(event('allNine') or {'nine':'literal'})}
    return events,changes,stop,injected
def run_isolate(fault=None):
    events,changes,stop,error=fixture(fault)
    with tempfile.TemporaryDirectory(prefix='pg466-control-') as tmp,contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(h,'ROOT',pathlib.Path(tmp)))
        for key,value in changes.items():stack.enter_context(patch.object(h,key,value))
        stack.enter_context(patch.object(h,'subprocess',types.SimpleNamespace(run=stop,DEVNULL=subprocess.DEVNULL)))
        try:h.isolate();return events,None
        except RuntimeError as actual:check(actual is error);return events,actual
events,error=run_isolate();check(error is None)
check([e[5:] for e in events if e.startswith('STOP:')]==['schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service','artemis.service'])
check(events.index('save:captured-before.private')<events.index('STOP:schubert-nk-api.service'))
check(events.index('readback:verify:after-isolation')<events.index('save:isolated.private'))
for at in range(1,len(events)+1):
    failed,actual=run_isolate(at);check(actual is not None and len(failed)==at)
    check('save:isolated.private' not in failed[:-1])
# Each malformed initial capture must prevent the very first stop.
for key,value in [('MainPID','1338495'),('InvocationID','b'*32),('ControlPID','1'),('Job','99'),('Result','timeout'),('ActiveState','failed'),('SubState','start')]:
    e,changes,stop,error=fixture();original=changes['show']
    def wrong(unit,key=key,value=value):
        state=original(unit)
        if unit=='schubert-nk-api.service':state[key]=value
        return state
    changes['show']=wrong
    with tempfile.TemporaryDirectory(prefix='pg466-refusal-') as tmp,contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(h,'ROOT',pathlib.Path(tmp)))
        for k,v in changes.items():stack.enter_context(patch.object(h,k,v))
        stack.enter_context(patch.object(h,'subprocess',types.SimpleNamespace(run=stop,DEVNULL=subprocess.DEVNULL)))
        try:h.isolate();raise AssertionError('invalid capture accepted')
        except ValueError:check(not any(x.startswith('STOP:') for x in e))
# pidfd TERM path is simulated with a literal fd; no os/signal global module is patched.
with tempfile.TemporaryDirectory(prefix='pg466-term-control-') as tmp,contextlib.ExitStack() as stack:
    root=pathlib.Path(tmp);(root/'isolated.private').touch();events=[]
    stack.enter_context(patch.object(h,'ROOT',root));stack.enter_context(patch.object(h,'all_terminal',lambda:events.append('allNine')));stack.enter_context(patch.object(h,'readback',lambda mode,label:events.append('readback')))
    def private_save(name,data):
        events.append(name)
        if name=='term-request.private':(root/name).touch()
    stack.enter_context(patch.object(h,'holder',lambda:{'pid':1438705,'locks':{'m':'literal'}}));stack.enter_context(patch.object(h,'save',private_save))
    stack.enter_context(patch.object(h,'os',types.SimpleNamespace(pidfd_open=lambda pid,flag:(check(pid==1438705 and flag==0) or 77),close=lambda fd:(check(fd==77),events.append('fdClosed')))))
    stack.enter_context(patch.object(h,'signal',types.SimpleNamespace(SIGTERM=15,pidfd_send_signal=lambda fd,sig,data,flags:(check((fd,sig,data,flags)==(77,15,None,0)),events.append('TERM')))))
    stack.enter_context(patch.object(h,'select',types.SimpleNamespace(POLLIN=1,poll=lambda:types.SimpleNamespace(register=lambda fd,event:check((fd,event)==(77,1)),poll=lambda timeout:(check(timeout==15000) or [(77,1)])))))
    class ProcPath:
        def __truediv__(self,other):return self
        def exists(self):return False
        def read_text(self):return ''
    stack.enter_context(patch.object(h,'pathlib',types.SimpleNamespace(Path=lambda p:ProcPath())))
    stack.enter_context(patch.object(h,'command',lambda args,**kw:b'0\n'))
    h.terminate();check(events.index('allNine')<events.index('term-request.private')<events.index('TERM')<events.index('fdClosed')<events.index('interrupted.private'))
print('PG466_HANDOFF_CONTROL_PASS independentAssertions='+str(count)+' productionPT0=true nativeMutation=false')
