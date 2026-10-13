"""Exact actual normal WARNING parent/GC and current four-owner rebound, never failed-parent fallback."""
import ast
import inspect
import json
import re
from pg1446_current_cold_stage import W
from pg1833_readonly_parent_state_sources import sources as previous_sources,context as old_context
from pg2021_fresh_resume_terminal_receipt import classify
from pg2015_completed_run_fresh_resume_once import SOURCE,BOM

TOOLS='pg2030-fresh-normal-warning-owned-stop-tools-v1'
BEFORE='8a7d42b110a047d60a3b10d948cf51731dab4b37b59d85052332acaa42942788'


def context():
    seal=json.loads((W/'pg2025-fresh-resume-full-live-seal-v1/manifest.safe.json').read_bytes());term=json.loads((W/'pg2021-fresh-resume-terminal-receipt-v1/manifest.safe.json').read_bytes())
    if seal['actualExit']!=0 or term['actualExit']!=0 or seal['productionSource']!=SOURCE or term['productionSource']!=SOURCE or seal['privateBeforeSha256']!=BEFORE or seal['sqlOracleQualified']is not True or seal['currentFourOwnedLive']is not True or seal['genuineCompletion']['completionCode']!=10 or term['normalUnit0or10']is not True:raise ValueError('actual same source normal warning full seal required')
    return BEFORE,seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc']


def projection_source():
    value=json.loads((W/'pg2027-fresh-sealed-parent-fields-v1.safe.json').read_bytes())
    if value['actualExit']!=0 or value['sealedBeforeSha256']!=BEFORE or value['source']!=SOURCE:raise ValueError('exact immutable current parent state18 required')
    state=value['parentState18']
    return 'EXPECTED='+repr(state)+'''
def qualify_warning_parent(fields,configuration=False):
    expected=dict(EXPECTED)
    if configuration:expected['SuccessExitStatus']='10'
    if type(fields)is not dict or fields!=expected:raise ValueError('exact current normal GC parent schema refused')
    return {'currentManagerGc':True,'normalUnit0or10':True,'stopAuthority':False}
'''


def receipt_source():
    live=json.loads((W/'pg2019-fresh-resume-live-binding-complete-v1/manifest.safe.json').read_bytes());state=json.loads((W/'pg2021-fresh-resume-terminal-receipt-v1/manifest.safe.json').read_bytes())['parentState']
    return 'BINDING='+repr(live['binding'])+'\nGC='+repr(state)+'\n'+inspect.getsource(classify)+'''
def completed(rows,done):
    return classify(BINDING,GC,rows,done)
'''


def sources():
    before,owned,done,utc=context();old_before,old_owned,old_done,old_utc=old_context();result={}
    pairs=[('pg1833','pg2030'),('Pg1833','Pg2030'),('PG1833','PG2030'),('pg2030-warning-owned-stop-tools-v1',TOOLS),(old_before,before),(old_utc,utc),('pg1770-next-day-full-warning-seal-v1','pg2025-fresh-resume-full-live-seal-v1'),('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',SOURCE),('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',BOM),('PG1638','PG1846'),('pg1638','pg1846'),('b5a12ee25dc44ec49b08f5d084b4052f','1eb0d77ce4704e7481ecc07beddcdf0c'),('9adbf05a-61d0-408b-b51d-ab19c7e5b16a','e31b627c-c0e2-4120-bd64-c0777479e800')]
    numbers={'81404764713':'106318294326','83204764713':'108118294326','127250':'187092','389748':'503613',str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for unit,identity in old_owned.items():pairs.append((identity[1],owned[unit][1]));numbers[identity[0]]=owned[unit][0]
    for name,raw in previous_sources().items():
        name=name.replace('1833','2030')
        for old,new in pairs:raw=raw.replace(old,new)
        for old,new in numbers.items():raw=re.sub(r'\b'+re.escape(old)+r'\b',new,raw)
        if name=='pg2030_warning_parent_projection.py':raw=projection_source()
        elif name=='pg2030_parent_receipt.py':raw=receipt_source()
        elif name=='pg2030_native_owned_stop.py':
            node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='parent_receipt');body=ast.get_source_segment(raw,node)
            old="require(receipt['genuinePid1Failure']is True and receipt['genuinePid1StartDone']is False and receipt['genuineRootDone']is True and receipt['managerFailureRetained']is True and receipt['completionOutcome']=='WARNING'and receipt['endMonotonicUs']==107890801314)"
            if body.count(old)!=1:raise ValueError('one actual parent receipt predicate required')
            body=body.replace(old,"require(receipt['genuinePid1StartDone']is True and receipt['genuineRootDone']is True and receipt['normalUnit0or10']is True and receipt['completionCode']==10 and receipt['endMonotonicUs']==107890801314)")
            body=body.replace("'actualPid1JobDone':False,'parentOrdinaryExit0':False,'genuineRootWarningOriginal':True,'managerFailureRetained':True","'actualPid1JobDone':True,'parentOrdinaryExit0':False,'genuineRootWarningOriginal':True,'normalUnit0or10':True,'managerExitCodeObserved':None")
            raw=raw.replace(ast.get_source_segment(raw,node),body,1)
        elif name=='Pg2030NativeStop.java':
            old='genuineParentWarningOriginal=true\\nmanagerFailureRetained=true\\n'
            if raw.count(old)!=1:raise ValueError('one complete normal source seal required')
            raw=raw.replace(old,'genuineParentDone=true\\nnormalUnit0or10=true\\n')
        if name.endswith('.py'):
            from pyflakes.api import check
            if check(raw,'<actual fresh normal stop '+name+'>'):raise ValueError('all actual stop globals required')
            compile(raw,'<fresh source current normal warning stop>','exec')
        result[name]=raw
    return result
