"""Save only deputy metrics from explicit public inputs; reads no private usage/rollouts."""
import datetime
import hashlib
import json
from pathlib import Path
import sys

report_dir = Path(__file__).parent
spec = json.loads(Path(sys.argv[1]).read_text())
quota = json.loads(sys.argv[2])
extra = json.loads(sys.argv[3])
end = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
begin = datetime.datetime.fromisoformat(spec['beginJST'])
files = []
for item in spec['production']:
    path = item['path']
    files.append({'path': path, 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                  'owner': item['owner']})
for path in spec['tests']:
    files.append({'path': path, 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()})
before = spec['quotaBefore']
after = quota['primary']
same = before['resetsAt'] == after['resetsAt']
result = {
    'wbs': spec['wbs'], 'baseCommit': spec['baseCommit'],
    'startSourceCommit': spec['startSourceCommit'],
    'changeCommitReference': '../commit-index.json maps the artifact commit after commit',
    'files': files, 'role': 'temporary-web-display-deputy',
    'threadId': '01a12810-342a-75e1-a67b-a9d115b04bc2', 'responseId': None,
    'beginJST': begin.isoformat(), 'endJST': end.isoformat(),
    'wallElapsedSeconds': (end - begin).total_seconds(), 'externalJobWaitSeconds': 0,
    'originalEstimate': spec.get('originalEstimate'),
    'userRevisedRemainingEstimatePp': spec['userRevisedRemainingPp'],
    'groupStartEstimateD': spec.get('groupStartD'),
    'estimateSourceHash': json.loads((report_dir / 'P016-25.01-metrics.json').read_text())
        ['revisedRemainingEstimate']['sourceHash'],
    'revisedResidualPredictionPp': None,
    'residualReason': 'Formal dependency/source/integration quality unverified; no guessed cost split',
    'quotaBefore': before, 'quotaAfter': quota,
    'sharedSameWindowNonnegativeDeltaPp': max(0, after['usedPercent'] - before['usedPercent']) if same else None,
    'sharedQuotaIsNotLeafActualCost': True, 'leafActualSpentPp': None,
    'N': None, 'T': None, 'publicTokenUsage': None,
    'moduleQualityPassed': False, 'wholeLeafAccepted': False,
}
result.update(extra)
(report_dir / (spec['wbs'].replace('WBS-', '') + '-metrics.json')).write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(spec['wbs'] + ' deputy metrics saved')
