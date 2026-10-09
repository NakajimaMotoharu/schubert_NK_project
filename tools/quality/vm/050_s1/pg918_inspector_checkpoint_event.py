"""Full closure checkpoint then existing Inspector host budget continuation, not new cost."""
import datetime,json,os,subprocess
from pathlib import Path
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
if __name__=='__main__':
    last=json.loads(M.read_bytes().splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0239'
    full=json.loads((W/'pg915-snapshot-six-host-v1/manifest.safe.json').read_bytes());assert full['actualExit']==0
    e=json.loads(json.dumps(last));e.update(eventId='PGPT-20261008-0240',previousEventId=last['eventId'],eventType='CHECKPOINT',timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),gitHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source=full['candidateSource'],run='PG915/916',
        actualPaths=['fresh3550PT/523suite/1632main/FESflakyNotRun0/static6zero/nullable-format0; same frozen source and JAR/session/blob independent0','Snapshot206L31M1C320B all100; oldSnapshot22miss: 4 impossible false predicates removed by complete equivalent state proof,18 prior missed outcomes independently tested','currentVM e016 unchanged/not deployed; old20native not imported; whole global/source native/formal pending'],
        attemptResult='FRESH_HOST_SUCCESS_SINGLE_CLASS_FOUR100_NOT_WHOLE_LEAF',elapsedSeconds=full['elapsedSeconds'],waitSeconds=None,
        quotaBefore=last['quotaAfter'],quotaAfter={'fetchedAtJST':'2026-10-10T06:43:00+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':85,'remainingPercent':15,'source':'get_usage_limits; minute precision only'},observedSharedPp=0,actualAllocatedPp=None,
        tokenMeasurementIds=['ae7a34ccd01f408542ba08a21fa885f47c9a9cbd90da5250e9d62030ee12beca'],tokenTotals=None,
        acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['one owned class independent contract and applicable four counters, not all24artifacts/dependencies'],'evidenceRefs':['evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG911-916-snapshot-host-v1/manifest.json']},
        technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'coverageBySource':[{'source':full['candidateSource'],'run':'PG915','snapshotCounters100':True,'wholeHostRemaining':full['remainingHostOnly'],'oldNativeImported':False}]},
        failureIds=[],retryCause=None,nextCommand='Continue same P00404 host contract: foreign-thread retirement rejection, fixed namespace freshness isolation, streaming budget exhaustion with resource postconditions')
    cont=json.loads(json.dumps(e));cont.update(eventId='PGPT-20261008-0241',previousEventId=e['eventId'],eventType='GROUP_CONTINUE',groupId='P00404_INSPECTOR_SNAPSHOT_HOST_CONTRACT',wbsLeafIds=['WBS-P004-04'],run='PG919-not-executed',
        estimateAtGroupStartPp={'low':.5,'base':1.5,'high':3.5},estimateChangeReason='Same existing B-HOST budget continuation from0237, not additional global total; remaining Inspector owned files/query error outcomes observed in old source coordinates, remeasure fresh run/bytes before counting.',
        actualPaths=[],attemptResult=None,elapsedSeconds=None,acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':[],'evidenceRefs':[]},technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'coverageBySource':[]},workCategory='SELECTED_TEST',nextCommand='Freeze PT-INSPECTOR-919001..004 independent input/expected/resource oracle, then selected batch+static fresh output; no VM operation/source mixing')
    with M.open('ab')as f:
        for v in(e,cont):f.write((json.dumps(v,ensure_ascii=False)+'\n').encode())
        f.flush();os.fsync(f.fileno())
    print(json.dumps({'events':[e['eventId'],cont['eventId']],'acceptedDelta':0,'actualAllocatedPp':None,'N':None,'T':None}))
