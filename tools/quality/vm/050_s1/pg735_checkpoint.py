"""487 actual same-source DONE/STOP/native checkpoint and next existing ADMIN budget."""
import datetime
import json
import os
from pathlib import Path
import subprocess

T=Path(__file__).resolve().parents[4]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')


def main():
    with M.open('rb')as f:
        f.seek(max(0,os.fstat(f.fileno()).st_size-65536));tail=f.read()
    assert tail.endswith(b'\n');last=json.loads(tail.splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0184'
    done=json.loads((W/'pg725-completed-readonly-v1.safe.json').read_bytes())
    native=json.loads((W/'pg730-current-eight-native-v1/manifest.safe.json').read_bytes())
    assert done['actualExit']==native['actualExit']==0 and done['productionSource']==native['productionSource']
    template=json.loads((T/'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_text())['eventTemplate']
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    quota={'fetchedAtJST':'2026-10-09T12:29:21+09:00','limitId':'codex','windowDurationMins':10080,
           'resetsAt':1791987599,'usedPercent':60,'remainingPercent':40,'source':'get_usage_limits'}
    result=[]
    for number,kind,group,leaves,estimate in (
        (185,'CHECKPOINT','PG715_NEW_SOURCE_ORDINARY_ROUTE',['WBS-N15.04'],last['estimateAtGroupStartPp']),
        (186,'GROUP_START','PG715_CURRENT_ADMIN_NATIVE',['WBS-N15.02'],{'low':.83,'base':2,'high':4.17})):
        e=json.loads(json.dumps(template))
        e.update(eventId=f'PGPT-20261008-{number:04}',previousEventId=f'PGPT-20261008-{number-1:04}',executionId=last['executionId'],
                 eventType=kind,groupId=group,timeJST=now,wbsLeafIds=leaves,source=done['productionSource'],
                 run='PG722-730'if number==185 else None,gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
                 estimateAtGroupStartPp=estimate,remainingEstimatePp=last['remainingEstimatePp'],
                 quotaBefore=last['quotaBefore']if number==185 else quota,quotaAfter=quota if number==185 else None,
                 observedSharedPp=1 if number==185 else None,sameQuotaWindow=True if number==185 else None,
                 tokenMeasurementIds=['aa380390503269075d544550ee4c668db133d83afd4ae79c38ab902819f3999c'],
                 tokenCoverageNote='N/T null: no explicit usage; shared59->60 not attributable to PGPT/PMO',workCategory='NATIVE_CONNECTION',
                 nextCommand='PG736 full21 readonly534/six ADMIN preservation -> new current existing-only ADMIN20 -> independentpost/new9native')
        if number==185:
            e.update(attemptResult='PG725 genuine0/1794.547089s<1800;PG726 sameCurrentA01PASS0;PG728ownedstop22.231016s0;PG729all24/resources0;PG730eight NoMatch0',
                     elapsedSeconds=1794.547089,externalJobWaitSeconds=None,timeOverlapNote='Parent wall elapsed exactPID1; model-active/external-wait attribution unavailable',
                     actualPaths=['ordinary sameRoot API-Web-Caddy genuineDONE/currentA01 -> orderedownedstop -> independentresource0 -> same-source8native'],
                     acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['current source ordinary-genuine DONE','sameCurrent A01 DIF001only','ownedstop/full24-resources0','eight exact-source native qualified'],'evidenceRefs':['evidence/01_PT/018_NK-OPS-001/evidence/PG722-current-native-public-v1/manifest.json']},
                     technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],
                     'coverageBySource':[{'source':done['productionSource'],'streams':8,'gain':native['gain'],
                     'remaining':{'LINE':948,'METHOD':179,'CLASS':12,'BRANCH':766}}]},
                     failureIds=['BUG-924','YKT-693'],retryCause='Offline typed proof False==0; corrected before native; no business replay',
                     unaccepted=['current Bootstrap/Inspector and negative matrix','coverage100/allCHR/formal/handover'],formalRunDelta=None)
        else:
            e['estimateChangeReason']='Existing N15.02 subcampaign; old source bootstrap result not imported, no new total/parent-child fee'
        result.append(e)
    with M.open('ab')as f:
        for e in result:f.write((json.dumps(e,ensure_ascii=False)+'\n').encode())
        f.flush();os.fsync(f.fileno())
    print(json.dumps({'appended':[e['eventId']for e in result],'actualAllocatedPp':None,'tokens':None}))


if __name__=='__main__':main()
