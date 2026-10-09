"""487 execution-only checkpoint/new full qualification budget, no quota-token inference."""
import datetime,json,os,subprocess
from pathlib import Path
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
if __name__=='__main__':
    last=json.loads(M.read_bytes().splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0221'
    e=json.loads(json.dumps(last));e.update(eventId='PGPT-20261008-0222',previousEventId=last['eventId'],timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),gitHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),eventType='GROUP_START_AND_TECHNICAL_CHECKPOINT',groupId='SSC240-451-FRESH-SIX',run='PG854v4/855v2/856v2 -> PG857',
      wbsLeafIds=['WBS-P004-03','WBS-P017-02','WBS-P017-12','WBS-K01.01'],estimateAtGroupStartPp={'low':1.0,'base':1.5,'high':2.0},estimateAtGroupStartTokenN=None,
      estimateChangeReason='K01 fresh six 1/1.5/2 within existing budget, not added to global90.9/269.8/642.6. N15 recovery .83/2/4.17 continues separate existing scope. Shared/PMO attribution unknown; no double allocation.',
      quotaBefore=last['quotaAfter'],quotaAfter={'fetchedAtJST':'2026-10-10T01:26:14+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':77,'remainingPercent':23,'source':'clock+get_usage_limits'},observedSharedPp=1,actualAllocatedPp=None,attribution='UNKNOWN',
      tokenMeasurementIds=['b2d584d48a0f46f4753a11d8c4cd3d7122ed2ad7b23d2b33563c734111ccb5b2'],tokenTotals=None,
      tokenCoverageNote='N/T null NO_NEW_EXPLICIT_USAGE_RECORD; 0221 fetchedAt00:59 had no clock proof and is not used as exact time; current fresh time01:26:14. Shared77 not individual usage.',
      acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':[],'evidenceRefs':[]},
      technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'coverageBySource':[{'source':'305a0e21f9802f3020eb4ba22b000b8eccef36ed','run':'PG854v4','newMethodScope':'three reference methods/two lambda applicable missed0','classWhole100':False,'tests':98,'suites':9,'staticBatch':0,'formal':False}]},
      actualPaths=['855v2 current full32/24-564/47/four same owned live preserved actual0 SHA289e9e…','856v2 installed832 fullABI Werror/independent151 fault/Python3/DB ownership actual0; stage0; verify currently pending','SS240241 design-only PR78/main8d5b verified'],
      attemptResult='Selected98 and actual current owner proof increased; completed-failed recovery not accepted until new scopes/post0; whole857 not run yet',failureIds=['BUG968','BUG969','BUG970','BUG971','BUG972','SSC240','SSC241'],retryCause='972 missing import full javac rejected; corrected new-only v2 passes fullABI before any VM operation',elapsedSeconds=None,externalJobWaitSeconds=None,timeOverlapNote='Grouped elapsed/work vs waiting not fully measured; do not infer from clock',nextCommand='Reattach current856 verify; after normal0 recover once; independentpost/resources0/runtime841 retire. Fresh857/858 all counters from new full run only, old selected/source diagnostic not counted.',stopReason=None,pgptAllComplete=False)
    with M.open('ab')as f:f.write((json.dumps(e,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    print(json.dumps({'event':e['eventId'],'quotaUsed':77,'actualAllocatedPp':None,'N':None,'T':None,'accepted':0}))
