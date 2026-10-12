"""Keep original ten Ref around all protected calls; new slot after old refusal."""
import ast
import pg1598_current_ordinary_once as prior
from pg1596_current_ordinary_before import payload as preflight

BODY=prior.BODY.replace('pg1598-current-ordinary-once-v1','pg1600-current-ordinary-once-v2')
tail="print(json.dumps(current))\nraise SystemExit(r.returncode)"
if BODY.count(tail)!=1:raise ValueError('one after-close client result required')
BODY=BODY.replace(tail,'')

def payload(hashes):
    raw=preflight();tree=ast.parse(raw)
    scope=next(n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
    start=raw.index("require(native==after['native'])",scope.end_lineno)
    end=raw.index("save=base/'pg1596-current-ordinary-before-v1'",start)
    before=raw[start:end]
    # Insert the formerly post-finally preparation inside the Ref-owned try.
    lines=raw.splitlines(keepends=True);final_start=next(i for i in range(scope.lineno-1,scope.end_lineno)if lines[i].startswith('finally:'))
    insertion='\n'.join(' '+line if line else line for line in(before+BODY).splitlines())+'\n'
    raw=''.join(lines[:final_start])+insertion+''.join(lines[final_start:scope.end_lineno])+"\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    raw='WATCH_FILES='+repr(hashes)+'\n'+raw
    compile(raw,'<current once with continuous metadata refs>','exec');return raw
