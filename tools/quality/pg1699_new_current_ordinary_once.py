"""New single noargs root start, continuous original ten Ref, preserved old native14."""
import ast
import inspect
import pg1598_current_ordinary_once as engine
from pg1697_new_current_ordinary_before import payload as preflight
from pg1698_new_current_ordinary_observer import namespace

SLOT='pg1699-new-current-ordinary-once-v1'


def body():
    raw=engine.BODY
    for a,b in [('pg1597','pg1698'),('pg1598-current-ordinary-once-v1',SLOT),('4d6bcbddb417b76d27e52d5d9640752c300edccf','2741c4546afad6c1e8b6efbd53dfb58144edf7bb'),('e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c','195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'),('PG1544','PG1638'),('require(native==after[\'native\']and declaration','require(declaration'),('require(len(records)==10)','require(len(records)==14)')]:raw=raw.replace(a,b)
    tail='print(json.dumps(current))\nraise SystemExit(r.returncode)'
    if raw.count(tail)!=1:raise ValueError('one after-ref return boundary required')
    return raw.replace(tail,'')


def payload(hashes):
    raw=preflight();scope=next(n for n in ast.parse(raw).body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
    start=raw.index("parse_raw=(base/'pg477-completed-tools-v1/pg477_unit_references.py')",scope.end_lineno)
    end=raw.index("save=base/'pg1697-new-current-ordinary-before-v1'",start)
    before=raw[start:end]
    lines=raw.splitlines(keepends=True);final_start=next(i for i in range(scope.lineno-1,scope.end_lineno)if lines[i].startswith('finally:'))
    insertion='\n'.join(' '+line if line else line for line in(before+body()).splitlines())+'\n'
    raw=''.join(lines[:final_start])+insertion+''.join(lines[final_start:scope.end_lineno])+"\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    raw='WATCH_FILES='+repr(hashes)+'\n'+raw
    compile(raw,'<new source ordinary once continuously referenced>','exec')
    return raw


def main():
    raw=inspect.getsource(engine.main)
    raw=raw.replace('pg1597','pg1698').replace('pg1598-current-ordinary-once-v1',SLOT)
    ns={**engine.__dict__,'payload':payload,'namespace':namespace}
    exec(compile(raw,'<new current once noargs fixed transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
