"""Recover only exact shared-window deltas from the published WBS66 event receipts."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

from pg998_metrics import EVENTS, canonical_fields
from pmo_quota_binding import digest, utc
from pmo_quota_legacy_end import metric_end_fields

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')


def event_number(event):
    return int(event['eventId'].rsplit('-', 1)[1])


def observe(row):
    receipt = row['quotaReceipt']
    value = receipt['observation']
    assert receipt['sha256'] == digest(value)
    return value


def main():
    start = json.loads(next(D.glob('613_共有枠*')).read_bytes())
    state = start['values']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == state['source']
    rows = [json.loads(line) for line in EVENTS.read_bytes().splitlines()]
    assert rows[-1]['eventId'] == start['eventId']
    starts = defaultdict(list)
    for row in rows:
        if row['eventType'] == 'GROUP_START':
            starts[row['groupId']].append(row)
    ends = [
        row for row in rows
        if 5708 < event_number(row) <= 6132 and row.get('groupBoundary') == 'END'
        and row.get('postTerminalReceiptVerified') is True
        and isinstance(row.get('quotaAfter'), dict)
        and row['quotaAfter'].get('schema') == 'PGPT_FRESH_QUOTA_V1'
    ]
    corrections = []
    for row in ends:
        beginning, = starts[row['groupId']]
        before = observe(beginning)
        after = observe(row)
        assert beginning['source'] == row['source'] and beginning['run'] == row['run']
        assert event_number(beginning) < event_number(row)
        assert utc(before['observedAtUTC']) <= utc(row['terminalAtUTC']) <= utc(after['observedAtUTC'])
        assert row['quotaBefore'] in (None, before['primary']) and row['quotaAfter'] == after
        first, last = before['primary'], after['primary']
        same = all(first[key] == last[key] for key in ('resetsAt', 'windowDurationMins'))
        measured = last['usedPercent'] - first['usedPercent'] if same else None
        assert (measured is None or measured >= 0) and row['observedSharedPp'] is None
        assert row['quotaWindowReportedBeforeGuard'] == dict(sameQuotaWindow=same, observedSharedPp=measured)
        fixed = metric_end_fields(dict(row, quotaBefore=before['primary'], sameQuotaWindow=same, observedSharedPp=measured), before)
        guarded, _ = canonical_fields(fixed, 'GROUP_END')
        assert guarded['observedSharedPp'] == measured
        assert guarded['sameQuotaWindow'] is (True if same else None)
        corrections.append(dict(originalStartEvent=beginning['eventId'], originalEndEvent=row['eventId'],
                                groupId=row['groupId'], before=first, after=last,
                                beforeAt=before['observedAtUTC'], afterAt=after['observedAtUTC'],
                                startReceiptSha256=digest(before), endReceiptSha256=digest(after),
                                exactSameWindow=same, correctedObservedSharedPp=measured,
                                originalFlatStartOmitted=row['quotaBefore'] is None,
                                actualAllocatedPp=None, tokenTotals=None))
    values = Counter(row['correctedObservedSharedPp'] for row in corrections)
    assert len(corrections) == 45 and values == {0: 23, 1: 2, None: 20}
    assert sum(row['originalFlatStartOmitted'] for row in corrections) == 33
    # Each difference is a shared observation; overlapping groups cannot be summed into chat usage.
    manifest = dict(actualExit=0, source=state['source'], productionCoreMain=state['productionCoreMain'],
                    interval={'exclusiveStart': 'PGPT-20261008-5708', 'inclusiveEnd': 'PGPT-20261008-6132'},
                    inputEndRows=45, sameWindowZero=23, sameWindowOne=2, incomparable=20,
                    originalFlatStartOmitted=33, initialVerifierExit=1,
                    initialVerifierIssue='Mature start receipts existed for all 45; 33 end rows omitted repeated flat starts.',
                    corrections=corrections, estimateOrAcceptanceChange=False, historicalEventsChanged=False,
                    groupSumClaim=None, actualAllocatedPp=None, tokenTotals=None, externalOperations=0,
                    terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = E / state['run']
    out.mkdir()
    path = out / 'manifest.json'
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), records=45))


if __name__ == '__main__':
    main()
