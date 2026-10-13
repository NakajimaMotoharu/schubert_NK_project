"""Immutable same-source current owned stop graph; attach independent receipts last."""
import ast
import json
from pyflakes.api import check
import pg2374_current_resume_owned_sources as prior
from pg1446_current_cold_stage import W
from pg2446_question_current_observer import SOURCE,BOM
from pg2452_question_current_terminal import payload as terminal_payload

TOOLS='pg2458-question-current-owned-stop-tools-v1'


def context():
    seal=json.loads((W/'pg2456-question-current-full-seal-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2452-question-current-terminal-v1/manifest.safe.json').read_bytes())
    if any(v['actualExit']!=0 or v['productionSource']!=SOURCE for v in [seal,term])or not seal['sqlOracleQualified']or not seal['currentFourOwnedLive']or not term['normalUnit0or10']:
        raise ValueError('actual whole current source terminal/DB/four owners required')
    return seal['privateBeforeSha256'],seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc']


def emit_receipt(live,state):
    raw=terminal_payload({**live['binding'],'rootPid':live['rootPid']})
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name in {'classify','_normal_classify'}]
    if len(nodes)!=2:raise ValueError('two pure current independent receipt functions required')
    return 'BINDING='+repr(live['binding'])+'\nGC='+repr(state)+'\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+"\ndef completed(rows,done):\n    return classify(BINDING,GC,rows,done)\n"


def emit(ctx,live,state,fields):
    result={}
    for name,raw in prior.emit(ctx,live,state,fields).items():
        name=name.replace('pg2374','pg2458').replace('Pg2374','Pg2458')
        if name=='pg2458_parent_receipt.py':raw=emit_receipt(live,state)
        else:
            for a,b in [(prior.TOOLS,TOOLS),('pg2374','pg2458'),('Pg2374','Pg2458'),('PG2374','PG2458'),
                        ('pg2368-current-resume-full-seal-v1','pg2456-question-current-full-seal-v1'),
                        (prior.SOURCE,SOURCE),(prior.BOM,BOM),('PG2126','PG2428'),('pg2126','pg2428')]:raw=raw.replace(a,b)
        if name.endswith('.py'):
            if check(raw,'<whole current owned stop '+name+'>'):raise ValueError('actual current export closure required')
            compile(raw,'<current owned stop graph>','exec')
        result[name]=raw
    return result


def sources():
    live=json.loads((W/'pg2450-question-current-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2452-question-current-terminal-v1/manifest.safe.json').read_bytes())
    projection=json.loads((W/'pg2472-question-current-parent-projection-v1.safe.json').read_bytes());ctx=context()
    if live['actualExit']!=0 or projection['actualExit']!=0 or projection['sealedBeforeSha256']!=ctx[0]or projection['source']!=SOURCE:
        raise ValueError('actual current binding/fullseal/parent18 required')
    return emit(ctx,live,term['parentState'],projection['parentState18'])
