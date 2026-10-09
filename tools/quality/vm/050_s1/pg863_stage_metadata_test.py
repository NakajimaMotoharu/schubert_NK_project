"""Independent nine-field preservation and access-only counterexample."""
import ast,types
from pg863_stage_candidate_v3 import source
tree=ast.parse(source());payload=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
t=ast.parse(payload);fn=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='metadata');ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual metadata>','exec'),ns)
fields=['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'];values=dict(zip(fields,range(1,10)));s=types.SimpleNamespace(**values,st_atime_ns=10)
assert ns['metadata'](s)==[1,2,3,4,5,6,7,8,9]
assert ns['metadata'](types.SimpleNamespace(**values,st_atime_ns=11))==ns['metadata'](s)
for key in fields:
 x={**values,key:99};assert ns['metadata'](types.SimpleNamespace(**x,st_atime_ns=10))!=ns['metadata'](s)
assert 'q.lstat()==s'not in payload and 'metadata(q.lstat())==metadata(s)'in payload
print('STAGE863002 actual generated nine metadata + atime-only PASS; mutation0')
