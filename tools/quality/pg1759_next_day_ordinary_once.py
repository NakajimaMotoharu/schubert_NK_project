"""One next-business-day ordinary start, prior DONE preserved not resumed."""
import ast
import inspect
import json
import pg1598_current_ordinary_once as engine
from pg1699_new_current_ordinary_once import body as previous_body
from pg1757_new_day_readonly_before import payload as preflight
from pg1758_next_day_observer import namespace

SLOT='pg1759-next-day-ordinary-once-v1'

def payload(hashes):
    raw=preflight();scope=next(n for n in ast.parse(raw).body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
    body=previous_body().replace('pg1698','pg1758').replace('pg1699-new-current-ordinary-once-v1',SLOT).replace('require(len(records)==14)','require(len(records)==20)')
    body=body.replace("persist('before.private.json',after)","persist('before.private.json',{**after,'native':native,'investigationBusinessDay':day})")
    # Fresh full-source readiness is host-preflight; same live context still reruns whole/day guard.
    marker=" save=base/'pg1757-next-business-day-before-v1'"
    start=raw.index(marker);lines=raw.splitlines(keepends=True)
    final_start=next(i for i in range(scope.lineno-1,scope.end_lineno)if lines[i].startswith('finally:'))
    prefix=raw[:start]
    final=''.join(lines[final_start:scope.end_lineno])
    raw=prefix+'\n'.join(' '+l if l else l for l in body.splitlines())+'\n'+final+"\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    raw='WATCH_FILES='+repr(hashes)+'\n'+raw
    from pyflakes.api import check
    if check(raw,'<next-day once whole/day actual source>'):raise ValueError('actual complete static gate required')
    compile(raw,'<one next-day start with continuous ten Ref>','exec');return raw

def main():
    # Current Test snapshot full qualified; unchanged Main/runtime independently proven.
    full=json.loads((engine.W/'pg1756-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    result=full.get('result',{})
    if full.get('actualExit')!=0 or result.get('tests')!=3618 or result.get('changedClasses')!=[]or result.get('addedClasses')!=[]:
        raise ValueError('current whole Test source and equal Main required before observer/start')
    raw=inspect.getsource(engine.main).replace('pg1597','pg1758').replace('pg1598-current-ordinary-once-v1',SLOT)
    ns={**engine.__dict__,'payload':payload,'namespace':namespace}
    exec(compile(raw,'<next-day one-start transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
