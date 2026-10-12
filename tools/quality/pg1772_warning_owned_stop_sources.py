"""Same-source/current-generation owned stop from qualified WARNING-original.

BUG1162/YKT930/SSC278; manager failure remains failure. No Root rerun, new
permit or generic failed-parent admission. All existing eight-stop gates remain.
"""
import inspect
import json
import re
from pg1446_current_cold_stage import W
import pg1703_new_source_owned_stop_sources as prior
from pg1770_next_day_full_warning_seal import warning_completion
from pg1762_next_day_done_receipt import EXPECTED,OLD

SOURCE=prior.SOURCE
TOOLS='pg1772-warning-owned-stop-tools-v1'


def context():
    envelope=json.loads((W/'pg1770-next-day-full-warning-seal-v1/manifest.safe.json').read_bytes())
    seal=envelope.get('guest');capture=json.loads((W/'pg1765-warning-terminal-capture-v2/manifest.safe.json').read_bytes())
    if envelope.get('actualExit')!=0 or type(seal)is not dict or seal.get('actualExit')!=0 or seal.get('productionSource')!=SOURCE or seal.get('sqlOracleQualified')is not True or seal.get('currentFourOwnedLive')is not True or capture.get('actualExit')!=0:raise ValueError('whole current independent seal and captured failed manager required')
    receipt=seal.get('genuineCompletion')
    if type(receipt)is not dict or receipt.get('genuinePid1Failure')is not True or receipt.get('managerFailureRetained')is not True or receipt.get('genuineRootDone')is not True or receipt.get('genuinePid1StartDone')is not False or receipt.get('completionOutcome')!='WARNING' or receipt.get('wholeAccepted')is not False:raise ValueError('manager failure and warning original must stay separate')
    end=receipt.get('endMonotonicUs')
    if type(end)is not int or not EXPECTED['start']<end<=EXPECTED['start']+1800000000:raise ValueError('actual original completion budget required')
    digest=seal.get('privateBeforeSha256');owned=seal.get('observedOwned');utc=seal.get('doneEndUtc')
    if type(digest)is not str or re.fullmatch('[a-f0-9]{64}',digest)is None or type(utc)is not str:raise ValueError('actual sealed bytes/time required')
    if type(owned)is not dict or set(owned)!={'caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service'}:raise ValueError('four current roles required')
    for value in owned.values():
        if type(value)is not list or len(value)!=4 or type(value[0])is not str or not value[0].isdecimal()or int(value[0])<=1 or type(value[1])is not str or re.fullmatch('[a-f0-9]{32}',value[1])is None or type(value[2])is not int or value[2]<=0 or type(value[3])is not str or re.fullmatch('[a-f0-9]{64}',value[3])is None:raise ValueError('complete current generation required')
    observed=capture.get('guest',{}).get('retainedRoot',{})
    if observed.get('InvocationID')!=EXPECTED['invocation']or observed.get('ExecMainStatus')!='10'or observed.get('Result')!='exit-code':raise ValueError('failure not captured for current Root')
    return digest,owned,receipt,utc


def bind(raw):
    digest,owned,receipt,utc=context();old_digest,old_owned,old_receipt,old_utc=prior.context()
    for a,b in [(old_digest,digest),(old_utc,utc),('pg1702-new-source-completed-seal-v1','pg1770-next-day-full-warning-seal-v1'),(prior.TOOLS,TOOLS),('pg1703','pg1772'),('Pg1703','Pg1772'),('PG1703','PG1772')]+[(OLD[k],EXPECTED[k])for k in ('invocation','run','cutoff','activation')]:raw=raw.replace(a,b)
    raw=raw.replace(OLD['cutoff'].replace('Z','+00:00'),EXPECTED['cutoff'].replace('Z','+00:00'))
    values={str(OLD['start']):str(EXPECTED['start']),str(OLD['start']+1800000000):str(EXPECTED['start']+1800000000),str(old_receipt['endMonotonicUs']):str(receipt['endMonotonicUs']),OLD['job']:EXPECTED['job'],'302199':'389748'}
    for unit,identity in old_owned.items():
        raw=raw.replace(identity[1],owned[unit][1]);values[identity[0]]=owned[unit][0]
    for a,b in values.items():raw=re.sub(r'\b'+re.escape(a)+r'\b',b,raw)
    return raw


def sources():
    result={}
    for name,raw in prior.sources().items():
        name=name.replace('1703','1772');raw=bind(raw)
        if name=='pg1772_parent_receipt.py':
            raw='EXPECTED='+repr(EXPECTED)+'\n'+inspect.getsource(warning_completion)+'''
def completed(rows,done):
    if type(rows)is not list or any(type(r)is not dict for r in rows):raise ValueError('complete rows required')
    cursors=[r.get('__CURSOR')for r in rows]
    if any(type(c)is not str or not c for c in cursors)or len(set(cursors))!=len(cursors):raise ValueError('unique actual journal cursors required')
    if any(r.get('JOB_RESULT')not in (None,'failed')for r in rows):raise ValueError('manager failure may not become done')
    return warning_completion(rows,done)
'''
        elif name=='Pg1772NativeStop.java':
            raw=raw.replace('MaintenanceCompletion.Outcome.SUCCESS','MaintenanceCompletion.Outcome.WARNING')
            raw=raw.replace('genuineParentDone=true\\n','genuineParentWarningOriginal=true\\nmanagerFailureRetained=true\\n')
        elif name=='Pg1772OriginalTupleTest.java':
            raw=raw.replace('Outcome.SUCCESS','Outcome.__OLD_SUCCESS__').replace('Outcome.WARNING','Outcome.SUCCESS').replace('Outcome.__OLD_SUCCESS__','Outcome.WARNING')
        if any(v in raw for v in [OLD['invocation'],OLD['run'],OLD['activation'],str(OLD['start']),'pg1702-new-source-completed-seal-v1']):raise ValueError('old Root authority survived binding')
        if name.endswith('.py'):compile(raw,'<actual WARNING owned stop helper>','exec')
        result[name]=raw
    return result
