"""Independent literal counterexamples for actual generated placement guard."""
import ast,copy
from pg863_stage_candidate_v2 import source
s=source();tree=ast.parse(s);payload=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
t=ast.parse(payload);fn=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='validate_baseline')
ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual generated guard>','exec'),ns)
guard=ns['validate_baseline']
b={'rows':{'schubert.batch_runs':list(range(564)),**{f'schubert.t{i}':[]for i in range(23)}},'configuration':{f'u{i}':{f'p{j}':'x'for j in range(32)}for i in range(10)},'units':{'u':'stopped'},'trees':{'original':{'metadata':[1,2], 'sha256':'literal'}}}
guard(copy.deepcopy(b),b,[])
bad=[]
for field in ('rows','configuration','units','trees'):
 x=copy.deepcopy(b);x[field]={};bad.append(x)
x=copy.deepcopy(b);x['rows']['schubert.batch_runs']=list(range(534));bad.append(x)
x=copy.deepcopy(b);x['configuration']['u0']['extra']='x';bad.append(x)
x=copy.deepcopy(b);x['trees']['original']['sha256']='foreign';bad.append(x)
for x in bad+[None]:
 try:guard(x,b,[])
 except (AssertionError,TypeError):pass
 else:raise AssertionError('invalid guard accepted')
try:guard(b,b,['foreign.conf'])
except AssertionError:pass
else:raise AssertionError('runtime accepted')
assert payload.index('before=protected()') < payload.index('root.mkdir(')
assert 'pg863-stage-v2' in s and 'pg863-candidate-stage-v2' in s
assert 'pg861-runtime841-retired-post-v1/after.private.json' in payload
print('STAGE863001 actual-payload normal+9 rejection cases PASS; VM mutation0')
