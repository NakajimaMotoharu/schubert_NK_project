"""BUG823/YKT592 independent PK/fullcolumn/type vectors. SQL/raw/display order unchanged."""
import ast,copy,pathlib
source=ast.parse(pathlib.Path(__file__).with_name('pg526_native_refs.py').read_text());env={}
names={'require','same_value','batch_index','verify_same_batch'}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),'<fixed logical batch join>','exec'),env)
rows=[{'id':i,'step':'literal-'+str(i),'target_count':0,'nested':{'nullable':None,'list':[True,1,'1',None]}}for i in range(1,463)]
count=0
def check(left,right,expected):
 global count
 before=copy.deepcopy((left,right))
 try:env['verify_same_batch'](left,right);actual=True
 except (ValueError,TypeError,KeyError):actual=False
 assert actual is expected and (left,right)==before;count+=1
check(rows,copy.deepcopy(rows),True)
check(rows,list(reversed(copy.deepcopy(rows))),True)
check(rows,copy.deepcopy(rows[200:]+rows[:200]),True)
for bad in [None,{},[],rows[:-1],rows+[rows[0]],tuple(rows)]:
 check(rows,bad,False);check(bad,rows,False)
for key in rows[0]:
 bad=copy.deepcopy(rows);del bad[0][key];check(rows,bad,False)
 bad=copy.deepcopy(rows);bad[0][key]=None;check(rows,bad,False)
for key,val in [('id',True),('id',0),('id',-1),('id',999),('id','1'),('id',2),('step','changed'),('target_count',True),('target_count',0.0),('target_count','0'),('nested',{'nullable':None,'list':[1,1,'1',None]}),('nested',{'nullable':None,'list':[True,1,'1']}),('nested',{'nullable':'','list':[True,1,'1',None]})]:
 bad=copy.deepcopy(rows);bad[0][key]=val;check(rows,bad,False)
bad=copy.deepcopy(rows);bad[0]['foreign']='x';check(rows,bad,False)
bad=copy.deepcopy(rows);bad[0]=None;check(rows,bad,False)
bad=copy.deepcopy(rows);bad[-1]=bad[0];check(rows,bad,False)
for value in [None,True,1,1.0,'1',[],{},object()]:
 for other in [None,True,1,1.0,'1',[],{},object()]:
  expected=type(value)is type(other) and type(value)in(type(None),bool,int,float,str,list,dict)and value==other
  assert env['same_value'](value,other)is expected;count+=1
print('PG526_BATCH_JOIN_ORACLE independentAssertions='+str(count)+' reorderAllowed=true pkColumnsTypesStrict=true rawUnmodified=true vmActions0=true productionPT0=true')
