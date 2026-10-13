"""One current-boot same-run four-owner stop graph; immutable actual tuple required."""
import ast
import json
import re
import types
from pyflakes.api import check
import pg2188_newsource_owned_stop_sources as prior
from pg2234_newboot_fresh_day_terminal import payload as terminal_payload
from pg2208_current_newboot_cold_sources import BOOT
from pg1446_current_cold_stage import W
from pg2176_newsource_normal_observer import SOURCE

TOOLS='pg2246-newboot-owned-stop-tools-v1'
BOM=prior.BOM


def context():
    seal=json.loads((W/'pg2242-newboot-fresh-day-full-seal-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2234-newboot-fresh-day-terminal-v1/manifest.safe.json').read_bytes())
    if any(v['actualExit']!=0 or v['productionSource']!=SOURCE for v in [seal,term])or not seal['sqlOracleQualified']or not seal['currentFourOwnedLive']or not term['normalUnit0or10']:
        raise ValueError('actual current same-boot fullseal and genuine terminal required')
    return seal['privateBeforeSha256'],seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc']


def emit_receipt(live,state):
    binding={**live['binding'],'rootPid':live['rootPid']}
    raw=terminal_payload(binding)
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name in {'_normal_classify','classify'}]
    if len(nodes)!=2:raise ValueError('whole immutable terminal declarations required')
    return 'BINDING='+repr(live['binding'])+'\nGC='+repr(state)+'\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+"\ndef completed(rows,done):\n    return classify(BINDING,GC,rows,done)\n"


def projection_source(fields):
    raw=prior.prior.projection_source();tree=ast.parse(raw)
    node=next(n for n in tree.body if isinstance(n,ast.Assign))
    return raw.replace(ast.get_source_segment(raw,node),'EXPECTED='+repr(fields),1)


def emit_sources(new_context,live,state,fields):
    before,owned,done,utc=new_context;old_before,old_owned,old_done,old_utc=prior.context()
    old_live=json.loads((W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes());old_b=old_live['binding'];b=live['binding']
    # Compose historical body only. Receipts are attached afterwards unchanged;
    # do not replace their negative UUIDs with this run's positive identifiers.
    base=types.FunctionType(prior.sources.__code__,{**prior.__dict__,'receipt_source':lambda:'HISTORICAL_BODY_ONLY=True\n','projection_source':lambda:'HISTORICAL_BODY_ONLY=True\n'})()
    pairs=[(prior.TOOLS,TOOLS),('pg2188','pg2246'),('Pg2188','Pg2246'),('PG2188','PG2246'),('pg2186-newsource-full-live-seal-v1','pg2242-newboot-fresh-day-full-seal-v1'),(old_before,before),(old_utc,utc),('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),('3d69f5af6bac46b1a5407591c4a79a0d',BOOT.replace('-',''))]
    pairs.extend((old_b[k],b[k])for k in ['invocation','run','cutoff','activation'])
    numbers={str(old_b['start']):str(b['start']),str(old_b['start']+1800000000):str(b['start']+1800000000),old_b['job']:b['job'],str(old_live['rootPid']):str(live['rootPid']),str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for unit,v in old_owned.items():pairs.append((v[1],owned[unit][1]));numbers[v[0]]=owned[unit][0]
    result={}
    for name,raw in base.items():
        name=name.replace('2188','2246')
        for old,new in pairs:raw=raw.replace(old,new)
        for old,new in numbers.items():raw=re.sub(r'\b'+re.escape(old)+r'\b',new,raw)
        if name=='pg2246_parent_receipt.py':raw=emit_receipt(live,state)
        elif name=='pg2246_warning_parent_projection.py':raw=projection_source(fields)
        if name.endswith('.py'):
            if check(raw,'<actual newboot current '+name+'>'):raise ValueError('whole current owned exports required')
            compile(raw,'<current same-peer owned scope>','exec')
        result[name]=raw
    return result


def sources():
    live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2234-newboot-fresh-day-terminal-v1/manifest.safe.json').read_bytes())
    projection=json.loads((W/'pg2244-newboot-parent-projection-v1.safe.json').read_bytes())
    ctx=context()
    if live['actualExit']!=0 or projection['actualExit']!=0 or projection['sealedBeforeSha256']!=ctx[0]or live['binding']['boot']!=BOOT.replace('-',''):
        raise ValueError('actual current boot/projection/run binding required')
    return emit_sources(ctx,live,term['parentState'],projection['parentState18'])
