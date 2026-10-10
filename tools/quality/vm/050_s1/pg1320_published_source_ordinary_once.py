"""One new ordinary Root, current769; observer required, original1800s preserved."""
import ast
import hashlib
import inspect
import json
import pg1319_published_source_ordinary_before as current
import pg1239_fresh_ordinary_once as previous
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST


def payload():
    W=current.previous.previous.transport.W;P=current.previous.previous.transport.P
    pre=json.loads((W/'pg1319-published-ordinary-before-v1.safe.json').read_bytes())
    if pre['actualExit']!=0 or pre['productionSource']!=SOURCE or not pre['ordinaryNoargs']:raise ValueError('actual current source before required')
    before=pre['privateBeforeSha256']
    if type(before)is not str or len(before)!=64 or any(c not in '0123456789abcdef'for c in before):raise ValueError('closed before SHA required')
    bundle=P/'pg1318-observer-stage-v1';expected={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in bundle.iterdir()}
    if set(expected)!={'pg1318_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'}:raise ValueError('exact current observer closure required')
    return compose(before,expected)


def compose(before,expected):
    if type(before)is not str or len(before)!=64 or any(c not in '0123456789abcdef'for c in before):raise ValueError('closed before SHA required')
    names={'pg1318_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'}
    if type(expected)is not dict or set(expected)!=names or any(type(v)is not str or len(v)!=64 or any(c not in '0123456789abcdef'for c in v)for v in expected.values()):raise ValueError('exact observer SHA closure required')
    code=current.payload();tree=ast.parse(code)
    block=next(n for n in tree.body if isinstance(n,ast.Try)and isinstance(n.body[0],ast.For))
    prefix=code[:sum(len(x)for x in code.splitlines(keepends=True)[:block.lineno-1])]
    snapshot=next(n for n in block.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
    definition=ast.get_source_segment(code,snapshot)
    definition='\n'.join(x[1:]if x.startswith(' ')else x for x in definition.splitlines())
    body=previous.BODY.replace('pg1237','pg1318').replace('pg1238-fresh-day-ordinary-before-v1','pg1319-published-ordinary-before-v1').replace('pg1239-fresh-ordinary-once-v1','pg1320-published-ordinary-once-v1').replace('PG1239-fresh-ordinary-once-v1','PG1320-published-ordinary-once-v1')
    body=body.replace(previous.BEFORE,before).replace('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE).replace('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',DIGEST).replace('PG1068','PG1292')
    body=body.replace("frozen['current']==after and frozen['ordinaryNoargs']and frozen['existingSuccessfulInspectorStepsForDate']==0","frozen['current']==pub_after and frozen['ordinaryNoargs']and type(frozen['existingSuccessfulInspectorStepsForDate'])is int and frozen['existingSuccessfulInspectorStepsForDate']>=0")
    body=body.replace("frozen['newJstDate']","frozen['jstDate']").replace("'newJstDate':","'jstDate':")
    body=body.replace("not pathlib.Path(retirement.TARGET).exists()","not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg492-once-resume.conf').exists()")
    body=body.replace("declaration=env['exec_record'](after['configuration']", "declaration=env['exec_record'](pub_after['configuration']")
    # The exact immutable parser is reused only as a declaration decoder.
    parser=current.BODY[:current.BODY.index("morning='schubert-nk-morning-controller.service'")]
    result='WATCH_FILES='+repr(expected)+'\n'+prefix+'\n'+definition+'\n'+parser+'\n'+body
    compile(result,'<new current-source one ordinary Root>','exec');return result


def main():
    W=current.previous.previous.transport.W
    if not(W/'pg1318-watch-v1.started').exists()or(W/'pg1318-watch-v1.exit').exists():raise ValueError('existing live qualified observer required')
    watch=W/'pg1318-parent-watch-v1.private.jsonl'
    if not watch.exists()or not watch.stat().st_size:raise ValueError('actual watch frames required')
    env=dict(current.previous.__dict__);env['payload']=payload
    code=inspect.getsource(current.previous.main).replace('pg1315-ordinary-publication-independent-v1','pg1320-published-ordinary-once-v1')
    exec(compile(code,'<new one-start actual transport>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
