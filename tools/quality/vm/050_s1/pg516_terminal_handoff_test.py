"""SSC210 exact owner/child/null vectors; no VM/signals."""
import ast,copy,pathlib
source=ast.parse(pathlib.Path(__file__).with_name('pg516_terminal_owned_handoff.py').read_text())
env={};exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='identity'],type_ignores=[]),'<fixed new owner oracle>','exec'),env)
v={'pid':310706,'ticks':1180403,'argv':'independent-parent','uid':['0']*4,'parent':310704,'children':{310735}}
count=0
def check(value,expected):
 global count
 assert env['identity'](value,310706,1180403,'independent-parent',310704) is expected;count+=1
check(v,True);check(None,False);check({},False)
for key in v:
 x=copy.deepcopy(v);del x[key];check(x,False)
 x=copy.deepcopy(v);x[key]=None;check(x,False)
for key,value in [('pid',True),('pid',310707),('ticks',True),('ticks',1180404),('argv','other'),('uid',['0','0','1','0']),('parent',True),('parent',310705),('children',[310735]),('children',{None}),('children',{True})]:
 x=copy.deepcopy(v);x[key]=value;check(x,False)
x=copy.deepcopy(v);x['foreign']=True;check(x,False)

import re,types
from pathlib import Path
parser=ast.parse(Path(__file__).with_name('pg477_unit_references.py').read_text())
exec(compile(ast.Module(body=[v for v in parser.body if isinstance(v,ast.FunctionDef) and v.name=='exec_record'],type_ignores=[]),'<independent parser>','exec'),env)
env['re']=re
import pg481_native_owned_stop as witness
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



good=[{'pid':777,'application':'PG515-fixed-recovery','user':'schubert_batch'}];locks=[{'pid':777,'mode':'ExclusiveLock'}]
primary_check(env['peer_contract']([],[]));primary_check(env['peer_contract'](good,locks))
for a,b in [(None,[]),([],None),(good,[]),([],locks),(good*2,locks),(good,locks*2),([dict(good[0],application='foreign')],locks),([dict(good[0],pid=True)],locks),(good,[dict(locks[0],mode='ShareLock')])]:primary_check(not env['peer_contract'](a,b))

print('PG516_HANDOFF_ORACLE independentAssertions='+str(count)+' currentOwnerAndChild=true signals0=true productionPT0=true')
