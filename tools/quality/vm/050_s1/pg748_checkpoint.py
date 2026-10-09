"""487 selected checkpoint + required full-six start, exact source and shared quota only."""
import datetime
import json
import os
from pathlib import Path
import subprocess

T=Path(__file__).resolve().parents[4]
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')


def main():
    with M.open('rb')as f:
        f.seek(max(0,os.fstat(f.fileno()).st_size-65536));tail=f.read()
    assert tail.endswith(b'\n');last=json.loads(tail.splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0188'
    template=json.loads((T/'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_bytes())['eventTemplate']
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
    quota={'fetchedAtJST':'2026-10-09T13:39:01+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':62,'remainingPercent':38,'source':'get_usage_limits'}
    rows=[]
    for n in (189,190):
        e=json.loads(json.dumps(template));e.update(eventId=f'PGPT-20261008-{n:04}',previousEventId=f'PGPT-20261008-{n-1:04}',executionId=last['executionId'],
            timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),gitHead=head,source=head,
            eventType='CHECKPOINT'if n==189 else'GROUP_START',groupId=last['groupId']if n==189 else'SSC234_CHANGED_SOURCE_FULL_SIX',
            wbsLeafIds=['WBS-P018-08.01','WBS-P018-08.02','WBS-P018-08.03','WBS-P010-05','WBS-P004-04']if n==189 else['WBS-K01'],
            estimateAtGroupStartPp=last['estimateAtGroupStartPp']if n==189 else{'low':1,'base':1.5,'high':2},
            estimateChangeReason='0188 owner parent P018-08 resolved to child01..03, existing group total unchanged/no duplicated parent fees'if n==189 else'Existing K01 full-source subcampaign; no added whole budget',
            remainingEstimatePp=last['remainingEstimatePp'],quotaBefore=last['quotaBefore']if n==189 else quota,
            quotaAfter=quota if n==189 else None,observedSharedPp=1 if n==189 else None,sameQuotaWindow=True if n==189 else None,
            tokenMeasurementIds=['5d43aa597ec8451fa39c334324821d78a43affeaf7c232ed48ac861c5c40b708'],
            tokenCoverageNote='N/T unavailable; shared quota includes unknown PMO/review/other use, not individually allocated',
            workCategory='SELECTED_TEST'if n==189 else'FULL_REGRESSION',
            nextCommand='python3 -B tools/quality/vm/050_s1/pg748_closing_full.py -> actual0 then pg748_full_collect.py')
        if n==189:e.update(run='PG745/746',attemptResult='88PT/12suite/FES0/static2zero;terminal27L18B5M1C100;Inspector39L22B10M1C100;latest-only literal oracle0',
            failureIds=['BUG-925','YKT-694'],retryCause='Old743 root prefix;744 excluded dependency no-tests gate;745 fixed two-leaf selected, old failures preserved',
            acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['same-body closing lifecycle independent contract','same Bootstrap main termination port','selected88/static2zero','latest-only oracle'],'evidenceRefs':['evidence/01_PT/018_NK-OPS-001/587_PG743_SSC234同期closing・同main単体仕様.md','evidence/01_PT/018_NK-OPS-001/588_PG746_748_closing資格・全6回帰仕様.md']},
            technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':['SSC234/FixedNativeCoverageTerminal'],'scopeRemovedIds':[],
                'coverageBySource':[{'source':'e24b246d5d83762650eda5574188d3b4f59fe501','newFamilyMissed':0,'covered':{'LINE':27,'METHOD':5,'CLASS':1,'BRANCH':18},'nativePending':True}]},
            unaccepted=['changed-source full six','new candidate deployment/current native','global100/allCHR/formal/handover'])
        rows.append(e)
    with M.open('ab')as f:
        for e in rows:f.write((json.dumps(e,ensure_ascii=False)+'\n').encode())
        f.flush();os.fsync(f.fileno())
    print(json.dumps({'appended':[e['eventId']for e in rows],'actualAllocatedPp':None,'N':None,'T':None}))


if __name__=='__main__':main()
