"""SSC207 identity negative vectors; never signal or connect to a VM."""
import ast,copy,pathlib
source=ast.parse(pathlib.Path(__file__).with_name('pg501_cold_owned_handoff.py').read_text())
env={};exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='identity'],type_ignores=[]),'identity contract','exec'),env)
v={'pid':1804,'ticks':162765,'argv':'literal-parent','uid':['0']*4,'parent':1802,'children':{1830}}
checks=0
def check(value,expected):
 global checks
 assert env['identity'](value,1804,162765,'literal-parent',1802) is expected;checks+=1
check(v,True);check(None,False);check({},False)
for key in v:
 x=copy.deepcopy(v);del x[key];check(x,False)
 x=copy.deepcopy(v);x[key]=None;check(x,False)
for key,value in [('pid',1805),('pid',True),('ticks',162766),('ticks',True),('argv','foreign'),('uid',['0','1','0','0']),('parent',1803),('children',[1830])]:
 x=copy.deepcopy(v);x[key]=value;check(x,False)
x=copy.deepcopy(v);x['unexpected']=True;check(x,False)
print('PG501_HANDOFF_ORACLE independentAssertions='+str(checks)+' signals0=true productionPT0=true')
