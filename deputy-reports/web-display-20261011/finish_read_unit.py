"""Record an explicitly reviewed single display unit; does not run or certify old tests."""
import datetime
import hashlib
import json
from pathlib import Path
import sys

path = Path(sys.argv[1])
result = json.loads(path.read_text())
quota = json.loads(sys.argv[2])
review = json.loads(sys.argv[3])
end = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
result.update(review)
result.update({
    'endJST': end.isoformat(),
    'wallElapsedSeconds': (end - datetime.datetime.fromisoformat(result['beginJST'])).total_seconds(),
    'externalJobWaitSeconds': 0,
    'role': 'temporary-web-display-deputy',
    'threadId': '01a12810-342a-75e1-a67b-a9d115b04bc2', 'responseId': None,
    'readFiles': [{'path': p, 'sha256': hashlib.sha256(Path(p).read_bytes()).hexdigest()}
                  for p in result['readOnlyAllowlist']],
    'originalEstimate': None, 'revisedRemainingPredictionPp': None,
    'productionChanges': [], 'testsRun': [], 'attemptCount': 0,
    'quotaAfter': quota,
    'sharedSameWindowNonnegativeDeltaPp': max(0, quota['primary']['usedPercent'] - result['quotaBefore']['usedPercent'])
        if quota['primary']['resetsAt'] == result['quotaBefore']['resetsAt'] else None,
    'leafActualSpentPp': None, 'N': None, 'T': None, 'publicTokenUsage': None,
    'wholeLeafAccepted': False, 'moduleQualityPassed': False,
    'checkpoint': str(path),
})
path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(result['wbs'] + ' read-only checkpoint saved')
