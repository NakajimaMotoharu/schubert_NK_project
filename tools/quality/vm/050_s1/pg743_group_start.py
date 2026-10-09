"""487 supplementary group within existing production owner leaf budgets; one event only."""
import datetime
import json
import os
from pathlib import Path
import subprocess

T = Path(__file__).resolve().parents[4]
M = Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')


def main():
    with M.open('rb') as f:
        f.seek(max(0, os.fstat(f.fileno()).st_size - 65536)); tail = f.read()
    assert tail.endswith(b'\n')
    last = json.loads(tail.splitlines()[-1]); assert last['eventId'] == 'PGPT-20261008-0187'
    e = json.loads((T / 'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_bytes())['eventTemplate']
    e.update(eventId='PGPT-20261008-0188',previousEventId=last['eventId'],executionId=last['executionId'],
             eventType='GROUP_START',groupId='SSC234_FINITE_CLOSING_SAME_MAIN',
             timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
             wbsLeafIds=['WBS-P018-08','WBS-P010-05','WBS-P004-04'],
             source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
             estimateAtGroupStartPp={'low':0.5,'base':1.5,'high':3},
             estimateChangeReason='Existing production owner leaf subset, no added total/parent or duplicated native cost. Late event after initial TDD files/format but before selected qualification; not falsely represented as pre-code timestamp.',
             remainingEstimatePp=last['remainingEstimatePp'],quotaBefore=last['quotaAfter'],
             workCategory='IMPLEMENTATION',unaccepted=['selected/static/fullhost','collector latest-only/realVM newsource','global formal'],
             nextCommand='clean source fixed -> pg743_closing_selected.py -> independent XML/counters -> closing collector -> required fresh full/native',
             tokenCoverageNote='Explicit token usage unavailable; no inference from shared quota. Late GROUP_START timing retained.')
    with M.open('ab') as f:
        f.write((json.dumps(e,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    print(json.dumps({'appended':e['eventId'],'estimatePp':e['estimateAtGroupStartPp'],'actualAllocatedPp':None}))


if __name__ == '__main__':main()
