"""Actual distinct newrun normal parent and four-owner fullseal rebound; no old success reuse."""
import ast
import inspect
import json
import re
from pyflakes.api import check
import pg2030_fresh_normal_warning_owned_stop_sources as previous
from pg2076_current_newrun_terminal_receipt import classify
from pg2070_current_newrun_observer import SOURCE as SOURCE,BOM as BOM
from pg1446_current_cold_stage import W

TOOLS='pg2090-current-newrun-owned-stop-tools-v1'
BEFORE='104b4b5733472426ecd1553d2d2adf37781af9467f0725c48292585c3fb82103'
__all__=['SOURCE','BOM','TOOLS','BEFORE','context','sources']


def context():
    seal=json.loads((W/'pg2085-native-augmented-newrun-full-seal-v1/manifest.safe.json').read_bytes());term=json.loads((W/'pg2076-current-newrun-terminal-receipt-v1/manifest.safe.json').read_bytes())
    if seal['actualExit']!=0 or term['actualExit']!=0 or seal['productionSource']!=SOURCE or seal['privateBeforeSha256']!=BEFORE or not seal['sqlOracleQualified']or not seal['currentFourOwnedLive']or seal['genuineCompletion']['completionCode']!=10 or not term['normalUnit0or10']:raise ValueError('actual same-source newrun full proof required')
    return BEFORE,seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc']


def projection_source():
    value=json.loads((W/'pg2087-current-newrun-parent-projection-v1.safe.json').read_bytes())
    if value['actualExit']!=0 or value['sealedBeforeSha256']!=BEFORE or value['source']!=SOURCE:raise ValueError('qualified current parent18 required')
    raw=previous.projection_source();tree=ast.parse(raw)
    node=next(n for n in tree.body if isinstance(n,ast.Assign))
    return raw.replace(ast.get_source_segment(raw,node),'EXPECTED='+repr(value['parentState18']),1)


def receipt_source():
    import pg2021_fresh_resume_terminal_receipt as normal
    live=json.loads((W/'pg2074-current-newrun-live-binding-v1/manifest.safe.json').read_bytes());state=json.loads((W/'pg2076-current-newrun-terminal-receipt-v1/manifest.safe.json').read_bytes())['parentState']
    raw='BINDING='+repr(live['binding'])+'\nGC='+repr(state)+'\n'+inspect.getsource(normal.classify).replace('def classify(','def _normal_classify(',1)+'\n'+inspect.getsource(classify)
    return raw+"\ndef completed(rows,done):\n    return classify(BINDING,GC,rows,done)\n"


def sources():
    before,owned,done,utc=context();old_before,old_owned,old_done,old_utc=previous.context();values={}
    pairs=[('pg2030','pg2090'),('Pg2030','Pg2090'),('PG2030','PG2090'),('pg2090-fresh-normal-warning-owned-stop-tools-v1',TOOLS),(old_before,before),(old_utc,utc),('pg2025-fresh-resume-full-live-seal-v1','pg2085-native-augmented-newrun-full-seal-v1'),('1eb0d77ce4704e7481ecc07beddcdf0c','2c37fef2a2ff48e7b6a05cfc23f84c19'),('4148e3e8-f107-431a-ab27-d6e6d1f1772e','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'),('2026-10-12T18:20:32.598894Z','2026-10-13T03:08:18.452473Z'),('e31b627c-c0e2-4120-bd64-c0777479e800','9026b2ab-bb42-49cd-a2bd-4c661049dce3')]
    numbers={'106318294326':'113070840714','108118294326':'114870840714','187092':'204748','503613':'588342',str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for unit,identity in old_owned.items():pairs.append((identity[1],owned[unit][1]));numbers[identity[0]]=owned[unit][0]
    for name,raw in previous.sources().items():
        name=name.replace('2030','2090')
        for old,new in pairs:raw=raw.replace(old,new)
        for old,new in numbers.items():raw=re.sub(r'\b'+re.escape(old)+r'\b',new,raw)
        # Positive body binding must never rewrite independent old-activation negatives.
        if name=='pg2090_parent_receipt.py':raw=receipt_source()
        elif name=='pg2090_warning_parent_projection.py':raw=projection_source()
        if name.endswith('.py'):
            if check(raw,'<actual newrun stop '+name+'>'):raise ValueError('complete newrun stop exports required')
            compile(raw,'<actual newrun stop>','exec')
        values[name]=raw
    return values
