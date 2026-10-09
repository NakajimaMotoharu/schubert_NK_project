"""487 Inspector partial checkpoint and bounded required common boundary test group."""
import datetime,json,os,subprocess
from pathlib import Path
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl');W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
if __name__=='__main__':
    last=json.loads(M.read_bytes().splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0241'
    r=json.loads((W/'pg919-inspector-selected-v1/run.safe.json').read_bytes());assert r['actualExit']==0
    e=json.loads(json.dumps(last));e.update(eventId='PGPT-20261008-0242',previousEventId=last['eventId'],eventType='CHECKPOINT',timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),gitHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source=r['source'],run='PG919',actualPaths=['fresh66PT/8suite/FES0/staticbatch0/all343main bytes match915','Files131L26M1C38B and Publisher134L25M1C46B all100; NativeReader branch24/24,129lines4miss remain real OS','four new independent foreign owner/stale namespace/deadline/drain cancellation oracles passed; no main/VM changes'],attemptResult='TWO_CLASS_FOUR100_OTHER_NATIVE_LINES_PENDING_NOT_WHOLE',failureIds=[],retryCause=None,
        quotaBefore=last['quotaAfter'],quotaAfter={'fetchedAtJST':'2026-10-10T06:56:00+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':85,'remainingPercent':15,'source':'get_usage_limits; minute precision only'},observedSharedPp=0,actualAllocatedPp=None,tokenMeasurementIds=['38bcb4b0c617574843dc35786b2995756ba6e684a2f350db1722ecbfd1aab5fd'],tokenTotals=None,elapsedSeconds=None,
        acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['two owned class negative/resource oracles and four counters; not all24/dependencies'],'evidenceRefs':['evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG919-inspector-host-v1/manifest.json']},technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'coverageBySource':[{'source':r['source'],'run':'PG919','differentTestSourceSameMainByteDiagnostic':True,'twoClassFour100':True,'nativeReaderMissedLines':4,'formal':False}]})
    start=json.loads(json.dumps(e));start.update(eventId='PGPT-20261008-0243',previousEventId=e['eventId'],eventType='GROUP_START',groupId='COMMON_CLOSED_BOUNDARY_NEGATIVE',wbsLeafIds=['WBS-P018-03.02','WBS-P018-08.02'],run='PG922-not-executed',
        estimateAtGroupStartPp={'low':.15,'base':.5,'high':1.2},estimateChangeReason='Bounded subset within existing .67/1.67/3.67 each .02 leaf, not additional total/parent or native fees. Existing small B-HOST planning unit .1/.35/.8 for instrumentation null boundary and .05/.15/.4 for daemon invalid invocation. LOW uncalibrated, actual tokens/allocated pp unknown.',
        actualPaths=[],acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':[],'evidenceRefs':[]},technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'coverageBySource':[]},attemptResult=None,
        nextCommand='Freeze independent default-JVM factory null rejection and invalid daemon invocation/no I/O tests; selected bootstrap static/counters; no argv/env/agent/authority mutation')
    with M.open('ab')as f:
        for v in(e,start):f.write((json.dumps(v,ensure_ascii=False)+'\n').encode())
        f.flush();os.fsync(f.fileno())
    print(json.dumps({'events':[e['eventId'],start['eventId']],'allocatedPp':None,'N':None,'T':None,'acceptedDelta':0}))
