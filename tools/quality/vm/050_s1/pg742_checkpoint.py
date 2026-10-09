"""487 current ADMIN native acceptance; no business operation or token inference."""
import datetime
import json
import os
from pathlib import Path
import subprocess

T = Path(__file__).resolve().parents[4]
M = Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    with M.open('rb') as f:
        f.seek(max(0, os.fstat(f.fileno()).st_size - 65536))
        tail = f.read()
    assert tail.endswith(b'\n')
    last = json.loads(tail.splitlines()[-1])
    assert last['eventId'] == 'PGPT-20261008-0186'
    native = json.loads((W / 'pg739-current-nine-native-v1/manifest.safe.json').read_bytes())
    assert type(native['actualExit']) is int and native['actualExit'] == 0
    template = json.loads((T / 'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_text())['eventTemplate']
    e = dict(template)
    e.update(eventId='PGPT-20261008-0187', previousEventId=last['eventId'], executionId=last['executionId'],
             groupId=last['groupId'], eventType='CHECKPOINT',
             timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
             wbsLeafIds=last['wbsLeafIds'], source=native['source'], run='PG737-741',
             gitHead=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip(),
             estimateAtGroupStartPp=last['estimateAtGroupStartPp'], remainingEstimatePp=last['remainingEstimatePp'],
             quotaBefore=last['quotaBefore'],
             quotaAfter={'fetchedAtJST':'2026-10-09T13:09:00+09:00','limitId':'codex', 'windowDurationMins':10080,
                         'resetsAt':1791987599,'usedPercent':61,'remainingPercent':39,'source':'get_usage_limits'},
             observedSharedPp=1, sameQuotaWindow=True, actualAllocatedPp=None,
             tokenMeasurementIds=['95ef5832680f9ed170ed452d2b974e44f4d114af8ef46c2173beb77f7f07305e'],
             tokenCoverageNote='No explicit usage N/T null; parent/review/PMO shared quota not allocated.',
             workCategory='NATIVE_CONNECTION', attemptResult='737verify0/execute20;738independentfull21/resource0;739nine NoMatch0;741four safe receipts0',
             elapsedSeconds=1.644088, timeOverlapNote='Exact ADMIN Unit elapsed; parent active/external waiting/review time not separately measurable.',
             acceptedDelta={'closedIds':[],'reopenedIds':[], 'criteriaSatisfied':['currentADMINnormal20','independentwhole21/24/resources0','nine same-source native'],
                            'evidenceRefs':['evidence/01_PT/018_NK-OPS-001/evidence/PG737-current-admin-public-v1/manifest.json']},
             technicalMeasurementDelta={'newClosedIds':[], 'reopenedIds':[], 'scopeAddedIds':[], 'scopeRemovedIds':[],
                 'coverageBySource':[{'source':native['source'],'streams':9,'incrementalGain':{'LINE':24,'METHOD':0,'CLASS':0,'BRANCH':1},
                                     'remaining':{'LINE':924,'METHOD':179,'CLASS':12,'BRANCH':765}}]},
             actualPaths=['current legitimate existingADMIN20 -> input retirement -> whole21 normal post -> current nine native'],
             unaccepted=['terminal post-snapshot tails','legitimate ordinary Inspector fixture','global100/allCHR/formal/handover'],
             retryCause='Two-source terminal post-snapshot counterexample reviewed read-only under477; next synchronous CLOSING supplement.',
             nextCommand='SSC supplement before newcode: synchronous CLOSING for Inspector/Bootstrap and same-main Bootstrap termination port; independent tests then required fresh full regression/native')
    with M.open('ab') as f:
        f.write((json.dumps(e, ensure_ascii=False) + '\n').encode())
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps({'appended':e['eventId'], 'actualAllocatedPp':None, 'N':None,'T':None}))


if __name__ == '__main__':
    main()
