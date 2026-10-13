"""Current immutable normal-resume owner graph; receipts are attached after body binding."""
import ast
import json
import re
from pyflakes.api import check
import pg2274_current_signed_owned_sources as previous
from pg1446_current_cold_stage import W
from pg2364_current_resume_terminal import payload as terminal_payload

SOURCE=previous.SOURCE
BOM=previous.BOM
TOOLS='pg2374-current-resume-owned-stop-tools-v1'


def context():
    seal=json.loads((W/'pg2368-current-resume-full-seal-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2364-current-resume-terminal-v1/manifest.safe.json').read_bytes())
    if any(v['actualExit']!=0 or v['productionSource']!=SOURCE for v in [seal,term])or not seal['sqlOracleQualified']or not seal['currentFourOwnedLive']or not term['normalUnit0or10']:raise ValueError('actual same-source current fullseal/normal receipt required')
    return seal['privateBeforeSha256'],seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc']


def emit_receipt(live,state):
    raw=terminal_payload({**live['binding'],'rootPid':live['rootPid']})
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='classify']
    if len(nodes)!=1:raise ValueError('exact current normal receipt declaration required')
    return 'BINDING='+repr(live['binding'])+'\nGC='+repr(state)+'\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+"\ndef completed(rows,done):\n    return classify(BINDING,GC,rows,done)\n"


def emit(ctx,live,state,fields):
    old_before,old_owned,old_done,old_utc=previous.context();before,owned,done,utc=ctx
    old_live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes());old_b=old_live['binding'];b=live['binding']
    pairs=[(previous.TOOLS,TOOLS),('pg2274','pg2374'),('Pg2274','Pg2374'),('PG2274','PG2374'),('pg2242-newboot-fresh-day-full-seal-v1','pg2368-current-resume-full-seal-v1'),(old_before,before),(old_utc,utc)]
    pairs.extend((old_b[k],b[k])for k in ['invocation','run','cutoff','activation'])
    numbers={str(old_b['start']):str(b['start']),str(old_b['start']+1800000000):str(b['start']+1800000000),old_b['job']:b['job'],str(old_live['rootPid']):str(live['rootPid']),str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for unit,v in old_owned.items():pairs.append((v[1],owned[unit][1]));numbers[v[0]]=owned[unit][0]
    result={}
    for name,raw in previous.sources().items():
        name=name.replace('2274','2374')
        if name=='pg2374_parent_receipt.py':raw=emit_receipt(live,state)
        elif name=='pg2374_warning_parent_projection.py':raw=previous.prior.projection_source(fields)
        else:
            for a,z in pairs:raw=raw.replace(a,z)
            for a,z in numbers.items():raw=re.sub(r'\b'+re.escape(a)+r'\b',z,raw)
        if name.endswith('.py'):
            if check(raw,'<current actual owned graph '+name+'>'):raise ValueError('all current owned globals required')
            compile(raw,'<current signed owned graph>','exec')
        result[name]=raw
    return result


def sources():
    live=json.loads((W/'pg2362-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2364-current-resume-terminal-v1/manifest.safe.json').read_bytes())
    projection=json.loads((W/'pg2372-current-resume-parent-projection-v1.safe.json').read_bytes());ctx=context()
    if live['actualExit']!=0 or projection['actualExit']!=0 or projection['sealedBeforeSha256']!=ctx[0]or projection['source']!=SOURCE:raise ValueError('actual current identity/projection required')
    return emit(ctx,live,term['parentState'],projection['parentState18'])
