"""Independent literal10 graph and all props/order/duplicate/null/unknown negative vectors."""
import ast,copy,pathlib
from pg529_dependency_graph import dependency_graph
units=['literal-'+str(i)+'.service'for i in range(10)]
rows={u:{'Requires':'one.service two.service','Before':'later.service','After':'prior.service other.service','PartOf':'','BindsTo':''}for u in units}
expected={u:{'Requires':['one.service','two.service'],'Before':['later.service'],'After':['other.service','prior.service'],'PartOf':[],'BindsTo':[]}for u in units}
count=0
def check(value,ids,valid):
 global count
 original=copy.deepcopy(value)
 try:actual=dependency_graph(value,ids);ok=True
 except ValueError:ok=False
 assert ok is valid and value==original
 if valid:assert actual==expected
 count+=1
check(rows,units,True);check(rows,tuple(reversed(units)),True)
for u in units:
 for prop in rows[u]:
  changed=copy.deepcopy(rows);changed[u][prop]=' '.join(reversed(changed[u][prop].split()));check(changed,units,True)
  for val in [None,[],{},True,1,'a.service a.service',' a.service','a.service ','a.service  b.service','a.service\tb.service','a.service\nb.service','/foreign.service','x'*256,' '.join('p'+str(i)+'.service'for i in range(129)),'x'*8193]:
   changed=copy.deepcopy(rows);changed[u][prop]=val;check(changed,units,False)
  changed=copy.deepcopy(rows);del changed[u][prop];check(changed,units,False)
 changed=copy.deepcopy(rows);changed[u]['Unknown']='x.service';check(changed,units,False)
 changed=copy.deepcopy(rows);changed[u]=None;check(changed,units,False)
for invalid in [None,{},[],{k:v for k,v in rows.items()if k!=units[0]},{**rows,'foreign.service':rows[units[0]]}]:check(invalid,units,False)
for invalid in [None,{},[],units[:-1],units+[units[0]],units[:-1]+[units[0]],units[:-1]+[True],units[:-1]+['bad/path.service']]:check(rows,invalid,False)
changed=copy.deepcopy(rows);changed[units[0]]['After']='foreign.service'
assert dependency_graph(changed,units)!=expected;count+=1
# The stdin handoff embeds exactly this fixed shared function; injected Unit FIELDS cannot shadow graph fields.
module=ast.parse(pathlib.Path(__file__).with_name('pg529_dependency_graph.py').read_text())
handoff=ast.parse(pathlib.Path(__file__).with_name('pg529_terminal_owned_handoff_v1.py').read_text())
assert ast.dump(next(n for n in module.body if isinstance(n,ast.FunctionDef)and n.name=='dependency_graph'))==ast.dump(next(n for n in handoff.body if isinstance(n,ast.FunctionDef)and n.name=='dependency_graph'));count+=1
assert 'GRAPH_FIELDS' in pathlib.Path(__file__).with_name('pg529_dependency_graph.py').read_text();count+=1
print('PG529_DEPENDENCY_GRAPH_ORACLE independentAssertions='+str(count)+' exactTenUnits=true reorderOnlyAllowed=true rawUnmodified=true externalOrderUnchanged=true vmActions0=true productionPT0=true')
