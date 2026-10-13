"""Same-source current normal owner graph; tuple fixed from independent new fullseal."""
import ast
import json
import re
from pg1446_current_cold_stage import W
import pg2090_current_newrun_owned_stop_sources as prior
from pg2182_newsource_terminal_receipt import payload as terminal_payload
from pg2176_newsource_normal_observer import SOURCE,BOM

TOOLS='pg2188-newsource-owned-stop-tools-v1'


def context():
    seal=json.loads((W/'pg2186-newsource-full-live-seal-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2182-newsource-terminal-receipt-v1/manifest.safe.json').read_bytes())
    if seal['actualExit']!=0 or term['actualExit']!=0 or seal['productionSource']!=SOURCE or not seal['sqlOracleQualified']or not seal['currentFourOwnedLive']or seal['genuineCompletion']['completionCode']!=10 or not term['normalUnit0or10']:
        raise ValueError('actual same newsource terminal/DB/fourowner fullseal required')
    return seal['privateBeforeSha256'],seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc']


def projection_source():
    value=json.loads((W/'pg2187-newsource-parent-projection-v1.safe.json').read_bytes())
    before,_,_,_=context()
    if value['actualExit']!=0 or value['sealedBeforeSha256']!=before or value['source']!=SOURCE:raise ValueError('independent current parent18 required')
    raw=prior.projection_source();tree=ast.parse(raw);n=next(n for n in tree.body if isinstance(n,ast.Assign))
    return raw.replace(ast.get_source_segment(raw,n),'EXPECTED='+repr(value['parentState18']),1)


def receipt_source():
    live=json.loads((W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes())
    state=json.loads((W/'pg2182-newsource-terminal-receipt-v1/manifest.safe.json').read_bytes())['parentState']
    return emit_receipt(live,state)


def emit_receipt(live,state):
    binding={**live['binding'],'rootPid':live['rootPid']}
    raw=terminal_payload(binding);tree=ast.parse(raw)
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'_normal_classify','classify'}]
    if len(nodes)!=2:raise ValueError('whole actual pure receipt declarations required')
    return 'BINDING='+repr(live['binding'])+'\nGC='+repr(state)+'\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+"\ndef completed(rows,done):\n    return classify(BINDING,GC,rows,done)\n"


def sources():
    before,owned,done,utc=context();old_before,old_owned,old_done,old_utc=prior.context()
    live=json.loads((W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes());b=live['binding']
    pairs=[('pg2090','pg2188'),('Pg2090','Pg2188'),('PG2090','PG2188'),('pg2188-current-newrun-owned-stop-tools-v1',TOOLS),(old_before,before),(old_utc,utc),('pg2085-native-augmented-newrun-full-seal-v1','pg2186-newsource-full-live-seal-v1'),('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE),('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7',BOM),('PG1846','PG2126'),('pg1846-manifest.sig','pg2126-manifest.sig'),('2c37fef2a2ff48e7b6a05cfc23f84c19',b['invocation']),('a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75',b['run']),('2026-10-13T03:08:18.452473Z',b['cutoff']),('9026b2ab-bb42-49cd-a2bd-4c661049dce3',b['activation'])]
    numbers={'113070840714':str(b['start']),'114870840714':str(b['start']+1800000000),'204748':b['job'],'588342':str(live['rootPid']),str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for unit,v in old_owned.items():pairs.append((v[1],owned[unit][1]));numbers[v[0]]=owned[unit][0]
    result={}
    for name,raw in prior.sources().items():
        name=name.replace('2090','2188')
        for old,new in pairs:raw=raw.replace(old,new)
        for old,new in numbers.items():raw=re.sub(r'\b'+re.escape(old)+r'\b',new,raw)
        if name=='pg2188_parent_receipt.py':raw=receipt_source()
        elif name=='pg2188_warning_parent_projection.py':raw=projection_source()
        if name.endswith('.py'):
            from pyflakes.api import check
            if check(raw,'<actual newsource ownedstop '+name+'>'):raise ValueError('whole actual exports required')
            compile(raw,'<actual newsource ownedstop>','exec')
        result[name]=raw
    return result
