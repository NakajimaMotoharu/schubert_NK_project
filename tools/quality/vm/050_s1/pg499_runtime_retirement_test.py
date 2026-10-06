"""Independent fixed retirement config/full-value matrix. No VM authority or Production PT."""
import ast,copy,pathlib,re
path=pathlib.Path(__file__).with_name('pg499_runtime_retirement_refs.py');parsed=ast.parse(path.read_text());env={'pathlib':pathlib,'re':re}
nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('require','compare')];exec(compile(ast.Module(body=nodes,type_ignores=[]),'fixed pure compare','exec'),env)
policy=pathlib.Path(__file__).with_name('pg477_unit_references.py');node=next(n for n in ast.parse(policy.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record');exec(compile(ast.Module(body=[node],type_ignores=[]),'closed parser','exec'),env)
env.update(MORNING='schubert-nk-morning-controller.service',NATIVE=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf'))
checks=0
def check(v):
 global checks
 checks+=1
 if not v:raise AssertionError('retirement vector '+str(checks))
def record(argv,aux='start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0'):return '{ path=/usr/bin/java ; argv[]='+argv+' ; ignore_errors=no ; '+aux+' }'
plain='/usr/bin/java fixed dev.codex.schubert.nk.batch.file.MorningProcessMain';argv=plain+' --resume 91a748b4-1abe-484c-9682-44f46429b324'
before={'units':{'literal':'full18'},'rows':{'literal':['allcolumns']},'trees':{'literal':'allbytes'},'unitFiles':{'base':'pinned'},'current':'/opt/schubert-nk/releases/0.1.0-PG495','configuration':{env['MORNING']:{'ExecStart':record(argv),'DropInPaths':str(env['NATIVE'])+' /run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf','ReadWritePaths':'base three plus fixed native','User':'root'},'schubert-nk-api.service':{'ExecStart':record('/usr/bin/java api','start_time=[old] ; stop_time=[old] ; pid=42 ; code=exited ; status=143'),'DropInPaths':'root-owned','User':'schubert-api'}}}
after=copy.deepcopy(before);after['configuration'][env['MORNING']].update(ExecStart=record(plain),DropInPaths=str(env['NATIVE']));after['configuration']['schubert-nk-api.service']['ExecStart']=record('/usr/bin/java api')
env['compare'](before,before,False);check(True);env['compare'](before,after,True);check(True)
def denied(actual,changed=True):
 try:env['compare'](before,actual,changed)
 except ValueError:check(True);return
 raise AssertionError('foreign retirement accepted')
for key in ('units','rows','trees','unitFiles','current'):
 v=copy.deepcopy(after);v[key]='foreign';denied(v)
for unit in after['configuration']:
 for key in after['configuration'][unit]:
  v=copy.deepcopy(after);v['configuration'][unit][key]='foreign';denied(v)
  v=copy.deepcopy(after);del v['configuration'][unit][key];denied(v)
for suffix in [' --resume foreign',' extra',' --resume 91a748b4-1abe-484c-9682-44f46429b324']:
 v=copy.deepcopy(after);v['configuration'][env['MORNING']]['ExecStart']=record(plain+suffix);denied(v)
denied(after,False);denied(before,True)
v=copy.deepcopy(after);v['configuration'][env['MORNING']]['ExecStart']=record(plain).replace('start_time=[n/a]','start_time=n/a');denied(v)
check(not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and (n.func.attr in ('unlink','remove','rename') or n.func.attr=='replace' and isinstance(n.func.value,ast.Name) and n.func.value.id=='os') for n in ast.walk(parsed)) and not any(isinstance(n,ast.Constant) and n.value=='daemon-reload' for n in ast.walk(parsed)))
print('PG499_RUNTIME_RETIRE_ORACLE independentAssertions='+str(checks)+' nativeMutation0=true productionPT0=true')
