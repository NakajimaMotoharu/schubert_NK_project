"""Qualify the one old progress sentence and persist only redacted scan receipts."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re

ENTRY = Path(__file__).resolve()
s = spec_from_file_location('g07_weblog_origins', ENTRY.with_name('5207_g07_weblog_session_origins.py'))
origins = module_from_spec(s)
s.loader.exec_module(origins)
r = origins.r
B = origins.B
PROGRESS = 'documents/400_PGPT/450_品質/460_基盤残件・再開優先順.md'


def ground_progress(candidate, scan):
    assert candidate['path'] == PROGRESS and candidate['rule'] == 'generic-api-key'
    exact = B.git('cat-file', 'blob', candidate['blob']).splitlines()[candidate['line'] - 1]
    before = B.git('show', f"{scan['fromCommit']}:{PROGRESS}").splitlines()
    assert B.sha(exact) == candidate['lineSha256'] and before.count(exact) == 1
    a, z = candidate['startColumn'] - 1, candidate['endColumn']
    assert exact[:a].endswith(b'G07remaining3315+')
    assert exact[z:].strip() == b'andcontinuous-v2.'
    assert re.fullmatch(rb'[0-9]{2}[Aa]ctual[A-Z][a-z]{5}[A-Z][a-z]{8}, freshquota[0-9]{2}percent ', exact[a:z])
    assert b'formal1964-53/newleaf0/effortnull/' in exact[:a]
    return dict(kind='Exact legacy progress and quota-percentage prose', path=PROGRESS,
                originalCommit=scan['fromCommit'], originalLine=before.index(exact) + 1,
                reportedLine=candidate['line'], unchangedLineSha256=candidate['lineSha256'],
                writeCandidateText=False)


def main():
    scan = B.load(r.OUT / 'scan-terminal.json')
    initial = B.load(r.OUT / 'qualified-cached-initial.json')
    assert initial['trackedBlobVersions'] == 187 and scan['commits'] == 14
    assert initial['unresolvedCandidates'] == 1 and initial['unqualifiedBinary'] == 0
    [candidate] = B.load(r.OUT / 'remaining-origins.json')
    proof = ground_progress(candidate, scan)
    extra = r.OUT / 'additional-build-origins.json'
    B.write(extra, [dict(candidate, ground=proof)])
    counts = initial['categories'].copy()
    counts[proof['kind']] = 1
    final = dict(initial, categories=counts, confirmedSecrets=0, unresolvedCandidates=0,
                 resultQualifiedForRange=True, additionalOrigins=B.ref(extra))
    assert sum(counts.values()) == scan['findingsCount'] == 55
    B.write(r.OUT / 'qualified-final-private-detail.json', final)
    compact = r.load('g07_weblog_compact_retain', '5184_g07_jdbc_metrics_retain_compact.py')
    r.configure(compact.w)
    compact.DETAILS = ('scan-terminal.json', 'qualified-cached-initial.json',
                       'qualified-final-private-detail.json', 'classified-findings.json',
                       'remaining-origins.json', 'binary-qualification.json',
                       'additional-build-origins.json')
    compact.main()


if __name__ == '__main__':
    main()
