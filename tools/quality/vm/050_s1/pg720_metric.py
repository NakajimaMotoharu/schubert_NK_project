"""Append 487 checkpoint and next existing-budget group; never allocate shared quota."""
import datetime
import json
import os
from pathlib import Path
import subprocess

T = Path(__file__).resolve().parents[4]
M = Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')


def main():
    template = json.loads((T / 'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_text())['eventTemplate']
    last = json.loads(M.read_bytes().splitlines()[-1])
    assert last['eventId'] == 'PGPT-20261008-0181'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip()
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    quota = {'fetchedAtJST': '2026-10-09T11:51:57+09:00', 'limitId': 'codex',
             'windowDurationMins': 10080, 'resetsAt': 1791987599, 'usedPercent': 59,
             'remainingPercent': 41, 'source': 'get_usage_limits'}
    items = []
    for number, kind, group, leaves, estimate, next_command in (
        (182, 'CHECKPOINT', 'PG713_CHANGED_EXPIRY_WHOLE_SIX', ['WBS-K01'],
         {'low': 1, 'base': 1.5, 'high': 2}, 'PG719 new readonly-v2 then whitelist public results'),
        (183, 'GROUP_START', 'PG715_NEW_SOURCE_ORDINARY_ROUTE', ['WBS-N15.04'],
         {'low': .83, 'base': 2, 'high': 4.17}, 'new current seven Backup private preserve; new ordinary parent observer-first')):
        e = json.loads(json.dumps(template))
        e.update(eventId=f'PGPT-20261008-{number:04}', previousEventId=f'PGPT-20261008-{number-1:04}',
                 executionId='PGPT-20261008-PG500', eventType=kind, groupId=group, timeJST=now,
                 wbsLeafIds=leaves, source='1ec19782a1afe22d1de75b05f4cd12b8a8a8a172',
                 run='PG713-719' if number == 182 else None, gitHead=head,
                 estimateAtGroupStartPp=estimate, remainingEstimatePp={'low':90.9,'base':269.8,'high':642.6},
                 estimateChangeReason='Existing K01/N15 budget subcampaign; no parent-child added budget or shared allocation',
                 quotaBefore=last['quotaBefore'] if number == 182 else quota,
                 quotaAfter=quota if number == 182 else None, observedSharedPp=1 if number == 182 else None,
                 sameQuotaWindow=True if number == 182 else None,
                 tokenMeasurementIds=['3458ae5585e6cfc52b745eb71896b8740ea3dfa86d5e9dfd1640336ebe667a9f'],
                 tokenCoverageNote='N/T null, no new explicit usage; PGPT/PMO unknown, shared quota not actualAllocatedPp',
                 nextCommand=next_command, workCategory='FULL_REGRESSION' if number == 182 else 'NATIVE_CONNECTION')
        if number == 182:
            e.update(attemptResult='3502PT517suite/FESFlakyNotRun0/static6zero/main1614; signed PG715/finite deploy0/all21 post0; receipt BUG923 under separate readonly correction',
                     elapsedSeconds=1050, externalJobWaitSeconds=None,
                     timeOverlapNote='Approximate full-run elapsed17:30; exact runtime retained in raw manifest, wait not inferred',
                     actualPaths=['PG715 signed187 -> PG718 unused -> PG717 verify/activate -> PG719 full21 actual0'],
                     failureIds=['BUG-923','YKT-692'],
                     unaccepted=['current-source genuine parent/native', 'whole coverage100/CHR/formal/handover'],
                     formalRunDelta=None)
        items.append(e)
    with M.open('ab') as f:
        for e in items:
            f.write((json.dumps(e, ensure_ascii=False)+'\n').encode())
        f.flush(); os.fsync(f.fileno())
    print(json.dumps({'appended': [e['eventId'] for e in items], 'actualAllocatedPp': None, 'tokens': None}))


if __name__ == '__main__':
    main()
