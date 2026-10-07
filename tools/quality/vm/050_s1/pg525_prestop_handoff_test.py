"""SSC213 exact owner/child/null vectors; no VM/signals."""
import ast,copy,pathlib
source=ast.parse(pathlib.Path(__file__).with_name('pg525_prestop_owned_handoff_v1.py').read_text())
env={};exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='identity'],type_ignores=[]),'<fixed new owner oracle>','exec'),env)
v={'pid':560210,'ticks':1926229,'argv':'independent-parent','uid':['0']*4,'parent':560208,'children':{560239}}
count=0
def check(value,expected):
 global count
 assert env['identity'](value,560210,1926229,'independent-parent',560208) is expected;count+=1
check(v,True);check(None,False);check({},False)
for key in v:
 x=copy.deepcopy(v);del x[key];check(x,False)
 x=copy.deepcopy(v);x[key]=None;check(x,False)
for key,value in [('pid',True),('pid',560211),('ticks',True),('ticks',1926230),('argv','other'),('uid',['0','0','1','0']),('parent',True),('parent',560209),('children',[560239]),('children',{None}),('children',{True})]:
 x=copy.deepcopy(v);x[key]=value;check(x,False)
x=copy.deepcopy(v);x['foreign']=True;check(x,False)

exec(compile(ast.Module(body=[v for v in source.body if isinstance(v,ast.FunctionDef) and v.name=='peer_contract'],type_ignores=[]),'<fixed peer contract>','exec'),env)
def peercheck(v):
 global count
 if not v:raise AssertionError('fixed peer')
 count+=1
good=[{'pid':777,'application':'PG524-native-stop','user':'schubert_batch'}];locks=[{'pid':777,'mode':'ExclusiveLock'}]
peercheck(env['peer_contract']([],[]));peercheck(env['peer_contract'](good,locks))
for a,b in [(None,[]),([],None),(good,[]),([],locks),(good*2,locks),(good,locks*2),([dict(good[0],application='foreign')],locks),([dict(good[0],pid=True)],locks),(good,[dict(locks[0],mode='ShareLock')])]:peercheck(not env['peer_contract'](a,b))
print('PG525_PRESTOP_HANDOFF_ORACLE independentAssertions='+str(count)+' ownerPeerContract=true vmActions0=true productionPT0=true')
