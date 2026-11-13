"""Local synthetic quota-boundary tests only: never API receipts, remote phases, source jobs or resets."""
from pathlib import Path
import copy, datetime, hashlib, importlib.util, json, tempfile

r = Path.cwd()
path = r/'evidence/01_PT/018_NK-OPS-001/input/2565_haruka_common60_controller.py'
spec = importlib.util.spec_from_file_location('haruka_guard_tool_under_test', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
now = datetime.datetime.now(datetime.timezone.utc)
future = int(now.timestamp())+3600
base = dict(schema='PGPT_FRESH_QUOTA_V1', observedAtUTC=now.isoformat(),
            ordinaryUsageAllowed=True,
            primary=dict(usedPercent=10, remainingPercent=90, windowDurationMins=10080, resetsAt=future),
            secondary=None)
cases = []

def rejects(value, label, file):
    file.write_text(json.dumps(value))
    try:
        module.fresh(file)
    except ValueError:
        cases.append(dict(id=label, result='PASS', expected='REJECT', actual='REJECT'))
        return
    raise AssertionError(label+' must reject')

with tempfile.TemporaryDirectory(prefix='synthetic-limit-unit-only-') as tmp:
    file = Path(tmp)/'synthetic-not-api-receipt.json'
    file.write_text(json.dumps(base))
    assert module.fresh(file)['primary']['remainingPercent']==90
    cases.append(dict(id='TOOL-HARUKA-Q01', result='PASS', expected='ALLOW90', actual='ALLOW90'))
    v = copy.deepcopy(base); v['primary'].update(usedPercent=90,remainingPercent=10)
    rejects(v,'TOOL-HARUKA-Q02',file)
    v = copy.deepcopy(base); v['secondary']=dict(usedPercent=90,remainingPercent=10,windowDurationMins=300,resetsAt=future)
    rejects(v,'TOOL-HARUKA-Q03',file)
    v = copy.deepcopy(base); v['ordinaryUsageAllowed']=False
    rejects(v,'TOOL-HARUKA-Q04',file)
    v = copy.deepcopy(base); v['primary']=None
    rejects(v,'TOOL-HARUKA-Q05',file)
    v = copy.deepcopy(base); v['observedAtUTC']=(now-datetime.timedelta(minutes=10)).isoformat()
    rejects(v,'TOOL-HARUKA-Q06',file)
    for changes in [dict(usedPercent=-1,remainingPercent=101),dict(usedPercent=101,remainingPercent=-1),dict(windowDurationMins=0)]:
        v = copy.deepcopy(base); v['primary'].update(changes)
        rejects(v,'TOOL-HARUKA-Q07-'+str(len(cases)),file)
    v = copy.deepcopy(base); v['observedAtUTC']=(now+datetime.timedelta(minutes=10)).isoformat()
    rejects(v,'TOOL-HARUKA-Q08',file)

e = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG30678-haruka-new-tool-local-guard-checks-v1'
assert not e.exists()
e.mkdir()
m = dict(actualExit=0, atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         cases=cases, assertionsPassed=len(cases), failures=0,
         sourceInputs={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                       [path,r/'tools/quality/pmo_quota_binding.py']},
         expectedOrigin='literal thresholds10/90/unavailable/stale/malformed; no production expected generator',
         fixtures='SYNTHETIC_LOCAL_TEMP_ONLY_NEVER_LIVE_API_OBSERVATIONS',
         actualApiCalls=0, remoteConnections=0, sourceJobsStarted=0, productTestsExecuted=0,
         resetsOrPurchases=0, coverage=None, formalAcceptanceAdded=0)
(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,localToolAssertions=len(cases),productTestsExecuted=0,remoteConnections=0)))
