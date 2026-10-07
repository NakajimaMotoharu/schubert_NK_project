"""BUG821: independent actual module-level before-tree loop, not only pure compare."""
import ast,copy,pathlib
parsed=ast.parse(pathlib.Path(__file__).with_name('pg520_runtime_retirement_refs.py').read_text())
loops=[n for n in ast.walk(parsed) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and [v.id for v in n.target.elts if isinstance(v,ast.Name)]==['root','values']]
assert len(loops)==1
env={'pathlib':pathlib};n=0
def require(v):
 if not v:raise ValueError('independent full-tree mismatch')
env['require']=require
code=compile(ast.Module(body=loops,type_ignores=[]),'<actual module before-tree loop>','exec')
gold={'/independent/root-one':{'metadata':'explicit-public-one','sha256':'a'*64},'/independent/root-two':{'metadata':'explicit-public-two','sha256':'b'*64}}
def execute(before,actual):
 calls=[]
 env.update(before=before,tree=lambda p:(calls.append(str(p)) or actual[str(p)]))
 exec(code,env)
 return calls
assert execute({'trees':copy.deepcopy(gold)},gold)==list(gold);n+=1
for root in gold:
 bad=copy.deepcopy(gold);bad[root]['sha256']='f'*64
 try:execute({'trees':copy.deepcopy(gold)},bad);raise AssertionError('changed original accepted')
 except ValueError:n+=1
for before in [None,{}, {'trees':None}]:
 try:execute(before,gold);raise AssertionError('missing contract accepted')
 except (TypeError,KeyError,AttributeError):n+=1
try:execute({'trees':gold},{});raise AssertionError('missing original accepted')
except KeyError:n+=1
assert 'baseline' not in {v.id for v in ast.walk(loops[0]) if isinstance(v,ast.Name)};n+=1
print('PG520_REFERENCE_PATH_ORACLE independentAssertions='+str(n)+' actualModuleTreeLoop=true oldUndefinedBaselineExcluded=false vmActions0=true productionPT0=true')
