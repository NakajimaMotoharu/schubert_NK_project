"""Append complete PGPT stage records; preserve existing collector/PMO state."""
import datetime
import fcntl
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EVENTS=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
V3=Path('/home/mini/codex/project1/work/PMO/hourly-monitor/wbs-reestimate-v3-PGPT-20261008-PG500.json')

def append(group,event_type,values):
    template=json.loads((ROOT/'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_bytes())['eventTemplate']
    with EVENTS.open('a+b') as f:
        fcntl.flock(f,fcntl.LOCK_EX);f.seek(0)
        lines=f.read().splitlines();last=json.loads(lines[-1])
        record=dict(template)
        number=int(last['eventId'].rpartition('-')[2])+1
        record.update(eventId=f'PGPT-20261008-{number:04d}',previousEventId=last['eventId'],
          executionId='PGPT-20261008-PG500',groupId=group,eventType=event_type,
          timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
          gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          source='40ef6e894573d2ffab1d1732124960f9c98d5f97',costRevision='PMO-remaining-v3-20261010',
          estimateRevisionSha256=hashlib.sha256(V3.read_bytes()).hexdigest(),
          attribution='UNKNOWN_SHARED_ACCOUNT',actualAllocatedPp=None,
          tokenCoverageNote='Explicit numeric response usage not available; no quota-to-token conversion; existing cursor retained',
          modelRequested='gpt-6.1-sol',reasoningRequested='high',modelObserved=None,reasoningObserved=None,
          modelVerificationMethod='Requested configuration; actual app settings unverified')
        record.update(values)
        f.seek(0,os.SEEK_END);f.write((json.dumps(record,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    return record['eventId']

if __name__=='__main__':
    # Stage allocation was fixed before command in0259. This checkpoint explicitly
    # records the delayed stage-start event rather than inventing a prior timestamp.
    print(append('V3_COLD_OFFLINE_BOOT','CHECKPOINT',{
      'wbsLeafIds':['WBS-N11'],'stage':'OFFLINE_BOOT_PRESERVATION','run':'PG997-offline-v1',
      'estimateAtGroupStartPp':{'low':.5,'base':1,'high':2},
      'estimateFrozenAt':'PGPT-20261008-0259 stageAllocation.WBS-N11.offlineBoot',
      'measurementDelay':'Dedicated stage event written after job start; estimate existed before start in0259; exact active/model and job wait split unavailable.',
      'attempt':1,'attemptResult':'RUNNING','workCategory':'RECOVERY',
      'actualPaths':['offline stable disk/backing identities and SHA capture; bounded compressed standalone copy running'],
      'unaccepted':['copy logical comparison pending','isolated boot not issued','cold current reauthentication pending'],
      'nextCommand':'Reattach exec session97866; compare must0/source stable, then new-only isolated management boot.'}))
