"""487 actual full/sign/baseline checkpoint then fresh same-source native campaign estimate."""
import datetime
import json
import os
from pathlib import Path
import subprocess

T=Path(__file__).resolve().parents[4]
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    with M.open('rb')as f:
        f.seek(max(0,os.fstat(f.fileno()).st_size-65536));tail=f.read()
    assert tail.endswith(b'\n');last=json.loads(tail.splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0190'
    h=json.loads((W/'pg748-closing-six-host-v1/manifest.safe.json').read_bytes())
    s=json.loads((W/'pg750-candidate-build-v1.safe.json').read_bytes())
    assert h['actualExit']==0 and h['candidateSource']==s['candidateSource'] and s['signatureVerified']is True
    assert (W/'pg751-completed-baseline-v1.exit').read_bytes()==b'0\n'
    template=json.loads((T/'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_bytes())['eventTemplate']
    quota={'fetchedAtJST':'2026-10-09T14:09:41+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':62,'remainingPercent':38,'source':'get_usage_limits'}
    rows=[]
    for n in (191,192):
        e=json.loads(json.dumps(template));e.update(eventId=f'PGPT-20261008-{n:04}',previousEventId=f'PGPT-20261008-{n-1:04}',executionId=last['executionId'],
            timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),source=h['candidateSource'],
            eventType='CHECKPOINT'if n==191 else'GROUP_START',groupId=last['groupId']if n==191 else'PG750_CHANGED_SOURCE_CURRENT_NATIVE_ROUTE',
            wbsLeafIds=['WBS-K01']if n==191 else['WBS-N15.01','WBS-N15.04'],
            estimateAtGroupStartPp=last['estimateAtGroupStartPp']if n==191 else{'low':.83,'base':2,'high':4.17},
            estimateChangeReason='Existing source-revalidation subcampaign only; no added parent/common budget'if n==192 else None,
            remainingEstimatePp=last['remainingEstimatePp'],quotaBefore=last['quotaBefore']if n==191 else quota,quotaAfter=quota if n==191 else None,
            observedSharedPp=0 if n==191 else None,sameQuotaWindow=True if n==191 else None,
            tokenMeasurementIds=['821be4388ba445e7a9bb27f2c8aaffc45652da83cf6da0f71a48b0e7ce0239f4'],
            tokenCoverageNote='N/T unavailable. Shared62->62 at integer quota resolution is not zero actual tokens; PGPT/PMO/review allocation null.',
            workCategory='FULL_REGRESSION'if n==191 else'NATIVE_CONNECTION',
            nextCommand='clean fixed pg752_compile.py -> immutablestage/unusedPG750stage -> verify/post -> activate once/independentwhole21 -> new same-source ordinary/native')
        if n==191:e.update(run='PG748/750/751',elapsedSeconds=h['elapsedSeconds'],externalJobWaitSeconds=None,
            timeOverlapNote='Exact build wall1052.436s; model active/external job waiting not separately allocated.',
            attemptResult='full3513/519/static6zero/1616actual0; signed187/SQL28/history29; currentwhole21/534/nine ADMIN/resource0actual0',
            acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['fresh full-six same source','selected twoJAR/other four byte join','signed new candidate187','currentwhole21/nineprivate/authenticated resources0'],
                'evidenceRefs':['evidence/01_PT/018_NK-OPS-001/589_PG748_750_全6資格・署名候補仕様.md','evidence/01_PT/018_NK-OPS-001/590_PG751_current原値全21・九ADMIN保全仕様.md']},
            technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],
                'coverageBySource':[{'source':h['candidateSource'],'hostOnlyRemaining':h['remainingHostOnly'],'nativeStreams':0,'oldNativeNotImported':True}]},
            unaccepted=['candidate not deployed','new source genuine parent/ownedstop/current closing/Inspector','global100/allCHR/formal/handover'])
        rows.append(e)
    with M.open('ab')as f:
        for e in rows:f.write((json.dumps(e,ensure_ascii=False)+'\n').encode())
        f.flush();os.fsync(f.fileno())
    print(json.dumps({'appended':[e['eventId']for e in rows],'actualAllocatedPp':None,'N':None,'T':None}))


if __name__=='__main__':main()
