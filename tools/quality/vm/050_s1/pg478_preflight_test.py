"""Independent scalar output-bound oracle; never reads Root data or runs SQL."""
import ast,pathlib
tree=ast.parse(pathlib.Path(__file__).with_name('pg478_newrun_preflight.py').read_text())
defs=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='accepted'];assert len(defs)==1
env={};exec(compile(ast.Module(body=defs,type_ignores=[]),'<literal output bound>','exec'),env)
vectors=[(0,0,True),(0,18602489,True),(0,33554431,True),(0,33554432,True),(0,33554433,False),(0,-1,False),(1,0,False),(143,18602489,False),(255,33554432,False)]
for code,length,expected in vectors:assert env['accepted'](code,length)==expected
print('PG478_PREFLIGHT_TEST independentAssertions=9 privateDataRead0=true productionPT0=true')
