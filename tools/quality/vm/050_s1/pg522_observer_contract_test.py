"""Independent operator-only current profile/atime/generation/durable guard checks."""
import ast,pathlib,types,copy
R=pathlib.Path(__file__).parent;checks=0
def check(v):
 global checks
 checks+=1
 assert v,'PG522 independent check '+str(checks)
observer=ast.parse((R/'pg522_watch_parent.py').read_text())
env={};nodes=[n for n in observer.body if isinstance(n,ast.FunctionDef) and n.name in {'metadata9','same'}]
check(len(nodes)==2);exec(compile(ast.Module(body=nodes,type_ignores=[]),'<operator pure functions>','exec'),env)
fields=['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns']
literal=[2,71,0,0,0o100644,1,50,1000,2000]
def vector(values,atime):
 s=types.SimpleNamespace(**dict(zip(fields,values)),st_atime_ns=atime)
 return types.SimpleNamespace(stat=lambda:s)
check(env['metadata9'](vector(literal,1))==tuple(literal))
check(env['metadata9'](vector(literal,999))==tuple(literal))
for i in range(9):
 values=literal.copy();values[i]+=1;check(env['metadata9'](vector(values,1))!=tuple(literal))
a={'MainPID':'17','InvocationID':'a'*32,'startTicks':240,'race':False}
check(env['same'](a,copy.deepcopy(a)))
for key in ['MainPID','InvocationID','startTicks']:
 b=copy.deepcopy(a);b[key]='foreign';check(not env['same'](a,b))
b=copy.deepcopy(a);b['race']=True;check(not env['same'](a,b))
text=(R/'pg522_watch_parent.py').read_text()
check('before==metadata9(ca)' in text and 'before==ca.stat()' not in text)
check("assert role in roots and same(roots[role],aa)" in text)
check("deadline=min(deadline,int(m['ExecMainStartTimestampMonotonic'])/1e6+1860)" in text)
check("'wholeMorningAccepted':False" in text and "'automaticStop':False" in text)
for name in ['pg522_prepare_observer_v1.py','pg522_external_resume_once.py']:
 outer=ast.parse((R/name).read_text())
 payload=next(n.value.value for n in outer.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'payload','PAYLOAD'} for t in n.targets))
 ast.parse(payload)
 check('/pg521-runtime-resume-v2' in payload)
 check('479f6c1def5b869850c43bf708355a362ec6c80dd5ec5652a40627e4ba9ead80' in payload)
 check('f72d6c82d7ab352e415b3d9547ec83cf5c3a0a9d80a77a1d795720e8f9f8991e' in payload)
 check('pg504' not in payload and '67fa28' not in payload)
 if name.startswith('pg522_external'):
  check("len(before['rows']['schubert.batch_runs'])==452" in payload)
  check("before['unitFiles'].items()" in payload)
  check("len(list(pathlib.Path('/run/schubert-nk/pt-coverage').iterdir()))==15" in payload)
  check(payload.index("persist('external-start-guard.private.json'")<payload.index("['/usr/bin/systemctl','start','--no-block'"))
  check(payload.count("['/usr/bin/systemctl','start','--no-block'")==1)
  check("'originalBudgetSeconds':1800" in payload and "'repeatForbidden':True" in payload)
print('PG522_OPERATOR_ORACLE independentAssertions='+str(checks)+' atimeExcluded=true sameRootGenerationRequired=true oneDurableStart=true productionPT0=true')
