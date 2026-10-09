"""One append-only487 actual parent/Backup checkpoint; no quota token conversion."""
import datetime
import json
import os
from pathlib import Path
import subprocess

T=Path(__file__).resolve().parents[4]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')


def main():
    last=json.loads(M.read_bytes().splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0183'
    event=json.loads((T/'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_text())['eventTemplate']
    post=json.loads((W/'pg724-retention-post-v1.safe.json').read_bytes());assert post['actualExit']==0
    start=json.loads((W/'pg722-start-v1.safe.json').read_bytes());assert start['clientExit']==0
    assert start['MainPID']=='2468821' and start['InvocationID']=='2aff8ecf3b7d4d15b24a8af0f73a8745'
    event.update(eventId='PGPT-20261008-0184',previousEventId=last['eventId'],executionId=last['executionId'],
                 groupId=last['groupId'],eventType='CHECKPOINT',timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
                 wbsLeafIds=last['wbsLeafIds'],source=post['productionSource'],run='PG722-ordinary/PG724-retention',
                 gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
                 estimateAtGroupStartPp=last['estimateAtGroupStartPp'],remainingEstimatePp=last['remainingEstimatePp'],
                 quotaBefore=last['quotaBefore'],quotaAfter={'fetchedAtJST':'2026-10-09T12:01:10+09:00',
                 'limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':59,'remainingPercent':41,'source':'get_usage_limits'},
                 observedSharedPp=0,sameQuotaWindow=True,workCategory='NATIVE_CONNECTION',
                 actualPaths=['current PG715 ordinary one-shot observer-first start -> same-parent real BackupSUCCESS2/otherSKIP8'],
                 attemptResult='PG721 private archive0/PG722prepare0/PG723stage0-watch active/PG722start client0; PG724 independent534 rows/524 preserved/one retention deleted/protected5/all6 old bundles preserved0',
                 unaccepted=['actual current parent DONE/API-Web-Caddy/A01','ownedstop/native exact source','global100/CHR/formal/handover'],
                 tokenMeasurementIds=['1c447ec6826d64785a77fef0cd85b5ad22a4e1da91c6358e9951d832edf0cf6b'],
                 tokenCoverageNote='N/T unavailable; source explicit usage absent, sharedquota change0 not PGPT0tokens',
                 nextCommand='reattach observer47840/A01wait69236, originaldeadline129349297774; then PG725 genuine/PG728stop/PG729post/PG730native')
    with M.open('ab') as f:f.write((json.dumps(event,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    print(json.dumps({'eventId':event['eventId'],'tokens':None,'actualAllocatedPp':None}))


if __name__=='__main__':main()
