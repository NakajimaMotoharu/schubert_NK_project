"""Pre-implementation487 estimate: same owner completion wiring/diagnostics; no extra parent fee."""
import datetime
import json
import os
from pathlib import Path
import subprocess

T=Path(__file__).resolve().parents[4]
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')


def main():
    with M.open('rb')as f:f.seek(max(0,os.fstat(f.fileno()).st_size-65536));tail=f.read()
    assert tail.endswith(b'\n');last=json.loads(tail.splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0200'
    e=json.loads((T/'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_bytes())['eventTemplate']
    e.update(eventId='PGPT-20261008-0201',previousEventId=last['eventId'],executionId=last['executionId'],eventType='GROUP_START',groupId='SSC237_FULL_COMPLETION_WIRING_DIAGNOSTIC',
        timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
        source=last['source'],wbsLeafIds=['WBS-P018-08','WBS-N15.01'],estimateAtGroupStartPp={'low':.5,'base':1.5,'high':3},remainingEstimatePp=last['remainingEstimatePp'],
        estimateChangeReason='Existing owner leaf subset; no parent or duplicated K01/native total. Event after design/ledger but before production edit. Query160 is limited read-only median5.384ms, not timeout cause.',
        quotaBefore=last['quotaAfter'],workCategory='IMPLEMENTATION',failureIds=['BUG927','BUG938'],
        unaccepted=['whole boundary/source wiring and redacted phase diagnostics','selected/static/full new source','signed current source real genuine/native','global100/formal/handover'],
        nextCommand='Independent completion boundary fault/null/order vectors and real full evidence wiring; selected/static then fresh full same source; signed code-only/fresh same run resume',
        tokenMeasurementIds=['d38aa33905a3770643b6b56c2a35ab1066803a7c35d03f9d04788f80b6f1512f'],tokenCoverageNote='N/T missing, PGPT/PMO/review allocation unknown. No quota-to-token conversion.')
    with M.open('ab')as f:f.write((json.dumps(e,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    print(json.dumps({'eventId':e['eventId'],'estimateAtGroupStartPp':e['estimateAtGroupStartPp'],'individualCost':None}))


if __name__=='__main__':main()
