"""Independent effective configuration and bounded pidfd fault vectors. No Root/VM/signal."""
import ast,pathlib,types,copy,re
source=pathlib.Path(__file__).with_name('pg477_partial_handoff.py').read_text()
tree=ast.parse(source)
selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['require','configuration','signal_one']]
assert len(selected)==3
count=0
def check(value):
 global count
 count+=1
 if not value:raise AssertionError('partial operator oracle')
all_units=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
morning='schubert-nk-morning-controller.service';inspector='schubert-nk-inbox-inspector.service';bootstrap='schubert-nk-bootstrap-admin.service'
old_rw='/run/schubert-nk /var/lib/schubert-nk/maintenance /srv/schubert-nk/backup /run/schubert-nk/pt-coverage/parent'
before={u:{'ExecStart':'old fixed','DropInPaths':'','ReadWritePaths':'','User':'fixed-user','NoNewPrivileges':'yes','ProtectSystem':'strict'} for u in all_units}
before[morning]['ReadWritePaths']=old_rw
def record(path,argv,historical=False):
 return '{ path='+path+' ; argv[]='+argv+' ; ignore_errors=no ; start_time=['+('old' if historical else 'n/a')+'] ; stop_time=['+('old' if historical else 'n/a')+'] ; pid='+('22' if historical else '0')+' ; code='+('exited' if historical else '(null)')+' ; status='+('0' if historical else '0/0')+' }'
for u in all_units:before[u]['ExecStart']=record('/usr/bin/java','/usr/bin/java fixed '+u,True)
before[morning]['ExecStart']=record('/usr/bin/java','/usr/bin/java fixed MorningProcessMain --resume 31100027-2222-4333-8444-555555555555',True)
prior='/opt/pgpt-tools-pg390/schubert-nk-inbox-inspector'
before[inspector]['ExecStart']=record(prior,prior,True)
before[bootstrap]['ExecStart']=record('/usr/bin/java','/usr/bin/java --enable-native-access=ALL-UNNAMED -cp fixed BootstrapAdminMain',True)
after=copy.deepcopy(before)
for u in all_units:after[u]['ExecStart']=record('/usr/bin/java','/usr/bin/java fixed '+u)
after[morning].update(ExecStart=record('/usr/bin/java','/usr/bin/java fixed MorningProcessMain'),DropInPaths='/etc/systemd/system/'+morning+'.d/pg477-native-coverage.conf')
target='/opt/schubert-nk/current/operations/bin/schubert-nk-inbox-inspector'
after[inspector].update(ExecStart=record(target,target),ReadWritePaths='/run/schubert-nk/pt-coverage/ordinary-inspector196')
after[bootstrap].update(ExecStart=record('/usr/bin/java','/usr/bin/java --enable-native-access=ALL-UNNAMED -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=BOOTSTRAP-${INVOCATION_ID}-ordinary -cp fixed BootstrapAdminMain'),ReadWritePaths='/run/schubert-nk/pt-coverage/ordinary-bootstrap196')
policy_source=ast.parse(pathlib.Path(__file__).with_name('pg477_unit_references.py').read_text())
rw_node=next(n for n in policy_source.body if isinstance(n,ast.FunctionDef) and n.name=='effective_rw')
extra=[n for n in policy_source.body if isinstance(n,ast.FunctionDef) and n.name in ['exec_record','after_exec','same_declaration','signed_declaration']]
policy={'re':re};exec(compile(ast.Module(body=[rw_node,*extra],type_ignores=[]),'<fixed RW>','exec'),policy)
drift=[False]
class File:
 def __init__(self,p):self.p=p
 def __truediv__(self,u):return File(self.p+'/'+u)
 def is_symlink(self):return False
 def read_bytes(self):return b'literal signed UTF8 \xc2\xa7\n'+(b'FOREIGN' if drift[0] and self.p.startswith('/etc/') else b'')
env={'ALL':all_units,'pathlib':types.SimpleNamespace(Path=lambda p:File(p))}
exec(compile(ast.Module(body=selected,type_ignores=[]),'<partial fixed operator>','exec'),env)
reader={'CONFIG':set(before[morning]),'show':lambda u,f:copy.deepcopy(after[u]),'effective_rw':policy['effective_rw'],'signed_declaration':policy['signed_declaration']}
proof={'configuration':before}
check(env['configuration'](reader,proof)==after)
def reject(fn,*args):
 global count
 try:fn(*args)
 except ValueError:count+=1;return
 raise AssertionError('invalid partial proof accepted')
good=copy.deepcopy(after)
for u in all_units:
 for key in ['User','NoNewPrivileges','ProtectSystem']:
  after[u][key]='foreign';reject(env['configuration'],reader,proof);after=copy.deepcopy(good)
for u in [morning,inspector,bootstrap]:
 after[u]['ReadWritePaths']+=' /foreign';reject(env['configuration'],reader,proof);after=copy.deepcopy(good)
 after[u]['ExecStart']+=' --resume foreign';reject(env['configuration'],reader,proof);after=copy.deepcopy(good)
 after[u]['DropInPaths']='/foreign.conf';reject(env['configuration'],reader,proof);after=copy.deepcopy(good)
after[morning]['ReadWritePaths']='/run/schubert-nk/pt-coverage/parent';reject(env['configuration'],reader,proof);after=copy.deepcopy(good)
after[bootstrap]['ExecStart']='fixed API alias';reject(env['configuration'],reader,proof);after=copy.deepcopy(good)
drift[0]=True;reject(env['configuration'],reader,proof);drift[0]=False
def run(fault=None):
 events=[];failure=RuntimeError('literal fault')
 def event(x):
  events.append(x)
  if fault==len(events):raise failure
 def tick(pid):check(pid==3412055);event('TICK');return 21968211
 def opening(pid,flags):check((pid,flags)==(3412055,0));event('OPEN');return 77
 def term(fd,sig,data,flags):check((fd,sig,data,flags)==(77,15,None,0));event('TERM')
 def register(fd,flag):check((fd,flag)==(77,1));event('REGISTER')
 def poll(ms):check(ms==15000);event('POLL');return [(77,1)]
 class Proc:
  def __truediv__(self,x):return self
  def exists(self):return False
 local=dict(env);local.update(tick=tick,save=lambda name,data:event('SAVE:'+name),os=types.SimpleNamespace(pidfd_open=opening,close=lambda fd:(check(fd==77),event('CLOSE'))),
  signal=types.SimpleNamespace(SIGTERM=15,pidfd_send_signal=term),select=types.SimpleNamespace(POLLIN=1,poll=lambda:types.SimpleNamespace(register=register,poll=poll)),
  pathlib=types.SimpleNamespace(Path=lambda *args:Proc()),time=types.SimpleNamespace(monotonic=lambda:0,sleep=lambda _:None))
 exec(compile(ast.Module(body=selected,type_ignores=[]),'<fixed signal seam>','exec'),local)
 try:local['signal_one'](3412055,21968211,'child-term-request.private');actual=None
 except RuntimeError as caught:check(caught is failure);actual=caught
 return events,actual
events,error=run();check(error is None)
check(events.index('TICK')<events.index('SAVE:child-term-request.private')<events.index('TERM')<events.index('CLOSE'))
for at in range(1,len(events)+1):
 failed,error=run(at);check(error is not None)
 if at<events.index('TERM')+1:check('TERM' not in failed)
check('SIGKILL' not in source)
print('PG477_PARTIAL_HANDOFF_TEST independentAssertions='+str(count)+' actualSignals0=true productionPT0=true')
