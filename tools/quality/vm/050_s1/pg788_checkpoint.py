"""487 single-writer immutable event0200: actual handoff/retirement and shared quota only."""
import datetime
import json
import os
from pathlib import Path
import subprocess

T=Path(__file__).resolve().parents[4]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')


def main():
    with M.open('rb')as f:f.seek(max(0,os.fstat(f.fileno()).st_size-65536));tail=f.read()
    assert tail.endswith(b'\n');previous=json.loads(tail.splitlines()[-1]);assert previous['eventId']=='PGPT-20261008-0199'
    for name in ('pg782-retained779-handoff-v1','pg786-stopped-current-v1','pg783-stage-v1','pg783-verify-v1','pg783-recover-v1','pg787-retired-post-v1'):assert (W/(name+'.exit')).read_bytes()==b'0\n'
    e=json.loads((T/'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_bytes())['eventTemplate']
    quota={'fetchedAtJST':'2026-10-09T17:17:56+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':67,'remainingPercent':33,'source':'get_usage_limits'}
    e.update(eventId='PGPT-20261008-0200',previousEventId=previous['eventId'],executionId=previous['executionId'],groupId=previous['groupId'],eventType='CHECKPOINT',
        timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),wbsLeafIds=previous['wbsLeafIds'],source=previous['source'],run='PG782/783/787',
        gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),sourceEvidenceRefs=['600_PG782_783_787_所有移譲・既存intent退役結果.md'],
        estimateAtGroupStartPp=previous['estimateAtGroupStartPp'],remainingEstimatePp=previous['remainingEstimatePp'],estimateChangeReason='N15.04 existing group; no parent/common extra fee. Recovery route closed but genuine/source completion unresolved.',
        acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['fixed two-actor pidfd handoff','existing INVALID three-intent-only actual retirement','new scopes normal release','independent full24-544/all39/root trees/kernel and resources0'], 'evidenceRefs':['600_PG782_783_787_所有移譲・既存intent退役結果.md']},
        actualPaths=['PG782 actual handoff0 old779close UNKNOWN/143','PG783 one actual retirement0 noUnitstop/revoke/start','PG787 independent fullpost0/current39/544/DB-advisory-FLOCK0'],
        unaccepted=['BUG927 genuine completion cause','BUG936 retained-server liveness prevention','newsource formal/native/CHR/global100/handover'],attempt=1,attemptResult='LIMITED_RECOVERY_ROUTE_CLOSED',failureIds=['BUG927','BUG936'],
        retryCause='New immutable pure gate/fixed namespace; legacy935 repeated receipt removed. Old failed/unknown returns preserved.',workCategory='RECOVERY',elapsedSeconds=55.974051,
        timeOverlapNote='Actual783 recovery wall; active model time/SSH wait allocation unknown; no token inference.',quotaBefore=previous['quotaAfter'],quotaAfter=quota,observedSharedPp=1,sameQuotaWindow=True,
        tokenMeasurementIds=['d38aa33905a3770643b6b56c2a35ab1066803a7c35d03f9d04788f80b6f1512f'],tokenCoverageNote='N/T null NO_NEW_EXPLICIT_USAGE_RECORD. Shared66->67 is not individually PGPT/PMO/review attributed.',
        nextCommand='Fix completion stage diagnostics/all retirement boundaries and fresh query cost; selected/full source qualification; signed code-only; fresh same9de2 one-use resume/genuine/native')
    with M.open('ab')as f:f.write((json.dumps(e,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    print(json.dumps({'eventId':e['eventId'],'actualAllocatedPp':None,'N':None,'T':None,'acceptedWbsDelta':0}))


if __name__=='__main__':main()
