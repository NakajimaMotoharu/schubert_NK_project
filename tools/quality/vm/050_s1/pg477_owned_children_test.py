"""Independent all-task child census, never opens /proc or signals a process."""
import ast,pathlib,types
tree=ast.parse(pathlib.Path(__file__).with_name('pg477_partial_handoff.py').read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['require','owned_children']]
assert len(nodes)==2
count=0
def check(value):
 global count
 count+=1
 if not value:raise AssertionError('all-task census')
task_names=['3412034','3412035'];rows={'3412034':'','3412035':'3412055 '};ticks=[21968172,21968172];passes=[0]
class Path:
 def __init__(self,p):self.p=p
 def __truediv__(self,x):return Path(self.p+'/'+str(x))
 @property
 def name(self):return self.p.rsplit('/',1)[-1]
 def iterdir(self):
  check(self.p=='/proc/3412034/task')
  passes[0]+=1
  values=task_names if passes[0]==1 else second[0]
  return [Path(self.p+'/'+n) for n in values]
 def read_text(self):
  check(self.p.endswith('/children'));return rows[self.p.split('/')[-2]]
def tick(pid):check(pid==3412034);return ticks.pop(0)
second=[task_names.copy()]
env={'pathlib':types.SimpleNamespace(Path=lambda p:Path(p)),'tick':tick}
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<all-task fixed oracle>','exec'),env)
fn=env['owned_children']
def run():ticks[:]=[21968172,21968172];passes[0]=0;return fn(3412034)
check(run()==['3412055'])
rows['3412035']='';check(run()==[])
rows['3412034']='12 ';rows['3412035']='8 ';check(run()==['8','12'])
def reject():
 global count
 try:run()
 except ValueError:count+=1;return
 raise AssertionError('malformed child census accepted')
rows['3412034']='3412055 ';rows['3412035']='3412055 ';reject()
rows['3412034']=''
for value in ['0','-1','foreign','3412055 foreign','+3412055']:
 rows['3412035']=value;reject()
rows['3412035']='3412055 ';second[0]=['3412034'];reject();second[0]=task_names.copy()
task_names[:]=[];second[0]=[];reject()
task_names[:]=['3412034','3412035'];second[0]=task_names.copy()
ticks[:]=[21968172,21968173];passes[0]=0
try:fn(3412034);raise AssertionError('identity drift accepted')
except ValueError:count+=1
print('PG477_OWNED_CHILDREN_TEST independentAssertions='+str(count)+' procRead0=true actualSignals0=true productionPT0=true')
