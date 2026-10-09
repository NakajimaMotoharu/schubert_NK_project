"""487 continued group: immutable failure evidence and pre-selected-test budget."""
import datetime, json, os, subprocess
from pathlib import Path
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
if __name__=='__main__':
    last=json.loads(M.read_bytes().splitlines()[-1]); assert last['eventId']=='PGPT-20261008-0220'
    e=json.loads(json.dumps(last)); e.update(eventId='PGPT-20261008-0221',previousEventId=last['eventId'],
      timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
      gitHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),run='PG852/853v3 -> PG854',
      eventType='FAILURE_AND_GROUP_CHECKPOINT',workCategory='PGPT',
      wbsLeafIds=['WBS-P004-03','WBS-P017-02','WBS-P017-12'],
      quotaBefore=last['quotaAfter'],quotaAfter={'fetchedAtJST':'2026-10-10T00:59:00+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':76,'remainingPercent':24,'source':'get_usage_limits; exact clock unavailable'},
      observedSharedPp=1,actualAllocatedPp=None,attribution='UNKNOWN',tokenTotals=None,
      tokenMeasurementIds=['352bb97bda83bb3a3e68a3f2fa19b1474fdc5aea236bbd59b2c1838070a6e9b1'],
      tokenCoverageNote='NO_NEW_EXPLICIT_USAGE_RECORD N/T null; otherchat/PMO unknown; requested model not actual UI confirmation',
      elapsedSeconds=None,externalJobWaitSeconds=1800.022578,timeOverlapNote='Original parent elapsed only; work/observer wait overlap not allocated',
      attemptResult='RootDONE present but original PID1 timeout143, no genuine acceptance; old2a sameSession reproduction0',
      failureIds=['BUG968','BUG969','BUG970','YKT737','YKT738','YKT739','SSC240'],
      retryCause='complete removes active; completed OriginalProof reference still pending capability. Source240 uses typed completion data-only.',
      actualPaths=['Actual current832 API/Web/Caddy samepeer ready','PG849 A01 PASS native fixed source2a','DONE_AFTER IO before deadline; failed parent143 not normalized','PG852 full24/564batch/47startup/four owned live preserved','PG853v3 old2a independent sameSession complete -> pending reference IO actual0'],
      nextCommand='Commit candidate SSC240, run854 nine affected host suites; current completed original failedPID1 recovery with new exact ownership; never846847 failed parent',
      stopReason=None,pgptAllComplete=False)
    e['acceptedDelta']={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':[],'evidenceRefs':[]}
    e['unaccepted']=['SSC240 candidate not compiled/PT/native/full','Failed PID19c08 RootDONE not genuine','Four actors live -> normal owned recovery/native before next runtime','formal24/1964/53 unchanged']
    e['estimateChangeReason']='Existing N15 .83/2/4.17pp continued, no duplicate group addition. SSC240 correction found after failure; pre-implementation leaf re-estimate was not recorded, not backdated. Existing individual ownership verified P00403/P01702. Remaining90.9/269.8/642.6 uncalibrated unchanged; current implementation/test work not accepted.'
    with M.open('ab') as f: f.write((json.dumps(e,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    print(json.dumps({'event':e['eventId'],'sharedDelta':1,'N':None,'T':None,'accepted':0}))
