"""SSC210 exact owner/child/null vectors; no VM/signals."""
import ast,copy,pathlib
source=ast.parse(pathlib.Path(__file__).with_name('pg514_epoch_owned_handoff.py').read_text())
env={};exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='identity'],type_ignores=[]),'<fixed new owner oracle>','exec'),env)
v={'pid':309605,'ticks':995739,'argv':'independent-parent','uid':['0']*4,'parent':309603,'children':{309634}}
count=0
def check(value,expected):
 global count
 assert env['identity'](value,309605,995739,'independent-parent',309603) is expected;count+=1
check(v,True);check(None,False);check({},False)
for key in v:
 x=copy.deepcopy(v);del x[key];check(x,False)
 x=copy.deepcopy(v);x[key]=None;check(x,False)
for key,value in [('pid',True),('pid',309606),('ticks',True),('ticks',995740),('argv','other'),('uid',['0','0','1','0']),('parent',True),('parent',309604),('children',[309634]),('children',{None}),('children',{True})]:
 x=copy.deepcopy(v);x[key]=value;check(x,False)
x=copy.deepcopy(v);x['foreign']=True;check(x,False)
print('PG514_HANDOFF_ORACLE independentAssertions='+str(count)+' currentOwnerAndChild=true signals0=true productionPT0=true')
