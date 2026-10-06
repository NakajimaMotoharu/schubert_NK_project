"""Literal pidfd authority/order/fault matrix. Extract definitions, no VM or real signal."""
import ast,pathlib,types,json,contextlib
source=pathlib.Path(__file__).with_name('pg477_handoff.py').read_text()
tree=ast.parse(source)
body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='interrupt_owned']
assert len(body)==1
checks=0
def check(value):
 global checks
 checks+=1
 if not value:raise AssertionError('independent handoff control')
class Path:
 def __truediv__(self,other):return self
 def exists(self):return False
 def read_text(self):return ''
def run(fault=None):
 events=[];error=RuntimeError('literal fault');state={'ten':'fixed stopped generations'};owner={'pid':3409258,'ticks':21847391};saved=[]
 def event(name):
  events.append(name)
  if fault==len(events):raise error
 def save(name,data):event('SAVE:'+name);saved.append(name)
 def holder():event('HOLDER');return owner.copy()
 def states():event('STATES');return state.copy()
 def fail(value):
  if not value:raise ValueError('fixed refused')
 def fd_open(pid,flags):check((pid,flags)==(3409258,0));event('OPEN');return 77
 def term(fd,sig,data,flags):check((fd,sig,data,flags)==(77,15,None,0));event('TERM')
 def register(fd,mask):check((fd,mask)==(77,1));event('REGISTER')
 def poll(ms):check(ms==15000);event('POLL');return [(77,1)]
 env={'readback':lambda mode,label:event('READ:'+mode+':'+label),'no_sessions':lambda:event('NO_SESSIONS'),'require':fail,'holder':holder,'all_terminal':states,'save':save,
  'json':json,'PID':3409258,'TICKS':21847391,'os':types.SimpleNamespace(pidfd_open=fd_open,close=lambda fd:(check(fd==77),event('CLOSE'))),
  'signal':types.SimpleNamespace(SIGTERM=15,pidfd_send_signal=term),'select':types.SimpleNamespace(POLLIN=1,poll=lambda:types.SimpleNamespace(register=register,poll=poll)),
  'pathlib':types.SimpleNamespace(Path=lambda *args:Path()),'time':types.SimpleNamespace(monotonic=lambda:0,sleep=lambda _:None)}
 exec(compile(ast.Module(body=body,type_ignores=[]),'<independent fixed interruption>','exec'),env)
 try:env['interrupt_owned'](owner,state);actual=None
 except RuntimeError as caught:check(caught is error);actual=caught
 return events,saved,actual
events,saved,error=run();check(error is None)
check(events.index('READ:snapshot:before-term')<events.index('SAVE:term-request.private')<events.index('TERM')<events.index('READ:verify:after-term')<events.index('SAVE:interrupted.private'))
check(events.count('TERM')==1 and 'CLOSE' in events)
for at in range(1,len(events)+1):
 failed,saved,error=run(at);check(error is not None)
 check('interrupted.private' not in saved)
 if at<events.index('TERM')+1:check('TERM' not in failed)
calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
check(not any(isinstance(n.func,ast.Attribute) and n.func.attr in ['kill','killpg','unlink','replace','rename'] for n in calls))
check('SIGKILL' not in source and "pidfd_send_signal(fd,signal.SIGTERM,None,0)" in source)
print('PG477_HANDOFF_TEST independentAssertions='+str(checks)+' productionPT0=true actualSignals0=true')
