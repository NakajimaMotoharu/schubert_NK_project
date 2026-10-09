"""487 host checkpoint and necessary full-six start, existing budgets not double-added."""
import datetime, json, os, subprocess
from pathlib import Path

M = Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
if __name__ == '__main__':
    last = json.loads(M.read_bytes().splitlines()[-1])
    assert last['eventId'] == 'PGPT-20261008-0237'
    r = json.loads((W/'pg911-snapshot-selected-v5/run.safe.json').read_bytes())
    assert r['actualExit'] == 0
    e = json.loads(json.dumps(last))
    e.update(eventId='PGPT-20261008-0238', previousEventId=last['eventId'], eventType='CHECKPOINT',
        timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
        gitHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), source=r['source'],
        run='PG911v1/v2/v3/v4/v5; PG912/913/914',
        actualPaths=['v1 offline root prefix not-run1; v2 cache byte refusal then corrected cache13/348; fixture F1 preserved',
          'v3 actual0/44PT/static0 same old main bytes; diagnostic914 line/method/class100 branch5 remaining, differing test-source not formal',
          'PG-D407 four equivalent predicates removed; literal state partition and reachable expiry Remainno; v4 fresh45PT0',
          'v5 fresh affected14suites actual0; same-source XML/source hashes/static retained, whole regression pending'],
        failureIds=['BUG-996','BUG-997'], retryCause='Old root-am offline command; old dependency snapshot; live fixture inherited terminal default. Distinct failures/cache-only preparation kept, no expectation relaxation.',
        attemptResult='NEW_CANDIDATE_SELECTED_SUCCESS_NOT_GLOBAL',
        quotaBefore=last['quotaAfter'], quotaAfter={'fetchedAtJST':'2026-10-10T06:21:00+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':85,'remainingPercent':15,'source':'get_usage_limits; minute precision only'},
        observedSharedPp=1, actualAllocatedPp=None, tokenMeasurementIds=['dabf497bb1c9d1493aca1cc01845d800ac5c29d18783a2cfdaaaddda24ec9228'],
        tokenTotals=None, acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['independent finite state predicate equivalence and selected affected callers'],'evidenceRefs':['evidence/01_PT/018_NK-OPS-001/612_Inspector状態判定_独立PT追加仕様.md']},
        technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'coverageBySource':[]},
        elapsedSeconds=None, workCategory='SELECTED_TEST',nextCommand='Pin final candidate and start PG915 fresh six; qualify PG916 from same run only',
        remainingEstimatePp={'low':90.9,'base':269.8,'high':642.6},
        estimateChangeReason='P00404 existing .5/1.5/3.5 remains; selected/comparison retries separate failures, no inferred token/time allocation; total uncalibrated unchanged.')
    start=json.loads(json.dumps(e))
    start.update(eventId='PGPT-20261008-0239', previousEventId=e['eventId'],eventType='GROUP_START',groupId='PGD407_451_FRESH_SIX',
        run='PG915-not-executed', wbsLeafIds=['WBS-K01.01'], estimateAtGroupStartPp={'low':1.0,'base':1.5,'high':2.0},
        estimateChangeReason='Required new main source full-six trigger, existing K01 budget subset not additional total. PG857 old source output not reused.',
        actualPaths=[],failureIds=[],retryCause=None,attemptResult=None,acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':[],'evidenceRefs':[]},
        workCategory='FULL_REGRESSION',nextCommand='python3 -B tools/quality/vm/050_s1/pg915_snapshot_full.py; after actual0 python3 -B tools/quality/vm/050_s1/pg916_snapshot_full_collect.py')
    with M.open('ab') as f:
        for v in (e,start): f.write((json.dumps(v,ensure_ascii=False)+'\n').encode())
        f.flush();os.fsync(f.fileno())
    print(json.dumps({'events':[e['eventId'],start['eventId']],'allocatedPp':None,'N':None,'T':None,'acceptedDelta':0}))
