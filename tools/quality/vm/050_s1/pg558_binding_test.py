"""SSC223 exact owner/child/null vectors; no VM/signals."""
import ast,copy,pathlib
source=ast.parse(pathlib.Path(__file__).with_name('pg558_current_terminal_handoff.py').read_text())
env={};exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='identity'],type_ignores=[]),'<fixed new owner oracle>','exec'),env)
v={'pid':561260,'ticks':2040839,'argv':'independent-parent','uid':['0']*4,'parent':561258,'children':{561289}}
count=0
def check(value,expected):
 global count
 assert env['identity'](value,561260,2040839,'independent-parent',561258) is expected;count+=1
check(v,True);check(None,False);check({},False)
for key in v:
 x=copy.deepcopy(v);del x[key];check(x,False)
 x=copy.deepcopy(v);x[key]=None;check(x,False)
for key,value in [('pid',True),('pid',561261),('ticks',True),('ticks',2040840),('argv','other'),('uid',['0','0','1','0']),('parent',True),('parent',561259),('children',[561289]),('children',{None}),('children',{True})]:
 x=copy.deepcopy(v);x[key]=value;check(x,False)
x=copy.deepcopy(v);x['foreign']=True;check(x,False)

import re,types
from pathlib import Path
parser=ast.parse(Path(__file__).with_name('pg477_unit_references.py').read_text())
exec(compile(ast.Module(body=[v for v in parser.body if isinstance(v,ast.FunctionDef) and v.name=='exec_record'],type_ignores=[]),'<independent parser>','exec'),env)
env['re']=re
import pg557_native_owned_stop as witness
env['h']=types.SimpleNamespace(same_generation=witness.same_generation)
exec(compile(ast.Module(body=[v for v in source.body if isinstance(v,ast.FunctionDef) and v.name in {'peer_contract','same_configuration'}],type_ignores=[]),'<pure ownership/config>','exec'),env)
def primary_check(v):
 global count
 if not v:raise AssertionError('primary binding');count+=1
 count+=1

old={'Id':'caddy.service','LoadState':'loaded','InvocationID':'a'*32,'ExecMainStartTimestampMonotonic':'100','Type':'simple','Restart':'no','RemainAfterExit':'no','KillMode':'control-group','SendSIGKILL':'no','MainPID':'42'}
current={**old,'MainPID':'0','ExecMainCode':'1','ExecMainStatus':'0'}
before={'ExecStart':'{ path=/bin/tool ; argv[]=/bin/tool literal ; ignore_errors=no ; start_time=[START] ; stop_time=[n/a] ; pid=42 ; code=(null) ; status=0/0 }','User':'fixed'}
after={'ExecStart':'{ path=/bin/tool ; argv[]=/bin/tool literal ; ignore_errors=no ; start_time=[START] ; stop_time=[END] ; pid=42 ; code=exited ; status=0 }','User':'fixed'}
primary_check(env['same_configuration'](before,after,old,current,'END'))
for original,replacement in [('path=/bin/tool','path=/bin/foreign'),('literal','foreign'),('ignore_errors=no','ignore_errors=yes'),('[START]','[CHANGED]'),('[END]','[OTHER]'),('pid=42','pid=43'),('code=exited','code=killed'),('status=0','status=143')]:
 v=dict(after);v['ExecStart']=v['ExecStart'].replace(original,replacement);primary_check(not env['same_configuration'](before,v,old,current,'END'))
for v in [None,{},dict(after,User='foreign'),dict(after,Unknown='x'),dict(after,ExecStart=None)]:primary_check(not env['same_configuration'](before,v,old,current,'END'))
for key in ['Id','LoadState','InvocationID','ExecMainStartTimestampMonotonic','Type','Restart','RemainAfterExit','KillMode','SendSIGKILL','ExecMainCode','ExecMainStatus']:
 v=dict(current);v[key]='foreign';primary_check(not env['same_configuration'](before,after,old,v,'END'))



good=[{'pid':777,'application':'PG557-native-stop','user':'schubert_batch'}];locks=[{'pid':777,'mode':'ExclusiveLock'}]
primary_check(env['peer_contract']([],[]));primary_check(env['peer_contract'](good,locks))
for a,b in [(None,[]),([],None),(good,[]),([],locks),(good*2,locks),(good,locks*2),([dict(good[0],application='foreign')],locks),([dict(good[0],pid=True)],locks),(good,[dict(locks[0],mode='ShareLock')])]:primary_check(not env['peer_contract'](a,b))

print('PG558_HANDOFF_ORACLE independentAssertions='+str(count)+' currentOwnerAndChild=true signals0=true productionPT0=true')

# Exact current fixedpair and seven-payload/output inventory; no legacy wrapper replay.
source_text=pathlib.Path(__file__).with_name('pg558_current_terminal_handoff.py').read_text()
for literal in ['PID=900001;TICKS=4742627;CHILD=900030;CHILD_TICKS=4742750','64603','64601','64600','0.1.0-PG548','pg558-current-owned-handoff-v1']:
 assert literal in source_text
for forbidden in ['0.1.0-PG495','33502','20418217592','len(baseline[\'rows\'][\'schubert.batch_runs\'])==462']:
 assert forbidden not in source_text
assert source_text.index('owner(True);signal.pidfd_send_signal(child_fd')<source_text.index('owner(False);signal.pidfd_send_signal(parent_fd')
assert "execute(sys.argv[1]=='execute')" in source_text
assert 'require(not runtime.exists())' in source_text
assert 'not SAVE.exists()' in source_text and "open('x')" in source_text
print('PG558_BINDINGS currentProfile=true implicitExpiryFixtureRequired=true stops0=true')

exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name=='profile_matches'],type_ignores=[]),'<independent profile shape>','exec'),env)
profile={k:{'literal':'independent'}for k in ('units','configuration','dependencies','rows','startup','originals','backup','native','oldProofs')}
profile['pid1Stop']={k:{'JOB_ID':j}for k,j in [('expiry','64603'),('broker','64601'),('cleanup','64600')]}
actual=copy.deepcopy(profile);actual['pid1Stop']={k:[v]for k,v in profile['pid1Stop'].items()}
assert env['profile_matches'](actual,profile)
assert not env['profile_matches'](profile,profile)
assert not env['profile_matches'](None,profile)
assert not env['profile_matches'](actual,None)
for k in actual:
 bad=copy.deepcopy(actual);del bad[k];assert not env['profile_matches'](bad,profile)
 bad=copy.deepcopy(actual);bad[k]=None;assert not env['profile_matches'](bad,profile)
for k in profile['pid1Stop']:
 for v in ([],None,{},[profile['pid1Stop'][k]]*2,[{'JOB_ID':'foreign'}]):
  bad=copy.deepcopy(actual);bad['pid1Stop'][k]=v;assert not env['profile_matches'](bad,profile)
print('PG558_PROFILE_JOIN_ORACLE singletonRecordShape=true absentNullDuplicateForeignRejected=true')
