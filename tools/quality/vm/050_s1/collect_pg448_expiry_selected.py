"""Capture frozen RERUN001 independently executed SQL/wire/fault cases; never formal acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg448-expiry-selected-v2'
frozen = work / 'pg448-expiry-selected-v2-frozen'
out = root / 'evidence/01_PT/007_NK-AUT-001/evidence/provisional/PG448-expiry-selected-v2'
assert not out.exists()
assert prefix.with_suffix('.exit').read_text().strip() == '0'
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log
assert log.count('BugInstance size is 0') == 6
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
names = {'AuthSessionRevocationService', 'LogoutInboxService', 'AuthenticationContextVerifier'}
modules, coverage, cases = {}, {}, []
for name, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'),
                          (5, 7, 10, 29, 10, 8), strict=True):
    target = frozen / name
    reports = sorted((target / 'surefire-reports').glob('TEST-*.xml'))
    count = 0
    for report in reports:
        suite = E.parse(report).getroot()
        assert all(int(suite.get(k)) == 0 for k in ('failures', 'errors', 'skipped'))
        assert int(suite.get('tests')) == len(suite.findall('testcase'))
        safe = E.Element('testsuite', {k: suite.get(k) for k in
                                     ('name', 'tests', 'failures', 'errors', 'skipped', 'time')})
        for case in suite.findall('testcase'):
            assert all(child.tag in ('system-out', 'system-err') for child in case)
            E.SubElement(safe, 'testcase', {k: case.get(k) for k in ('name', 'classname', 'time')})
            if case.get('name').startswith('rerun001'):
                cases.append({'method': case.get('name'), 'junit': 'junit/' + name + '/' + report.name})
        path = out / 'junit' / name / report.name
        path.parent.mkdir(parents=True, exist_ok=True)
        E.indent(safe)
        E.ElementTree(safe).write(path, encoding='utf-8', xml_declaration=True)
        count += int(suite.get('tests'))
    assert count == expected
    modules[name] = {'tests': count, 'suites': len(reports), 'failures': 0, 'errors': 0, 'skipped': 0}
    bugs = E.parse(target / 'spotbugsXml.xml').getroot()
    assert not bugs.findall('BugInstance') and int(bugs.find('Errors').get('errors')) == 0
    for c in E.parse(target / 'site/jacoco/jacoco.xml').findall('.//class'):
        simple = c.get('name').rsplit('/', 1)[-1]
        if simple in names:
            coverage[simple] = {x.get('type'): {'missed': int(x.get('missed')),
                                              'covered': int(x.get('covered'))} for x in c.findall('counter')}
assert set(coverage) == names and all(x['missed'] == 0 for c in coverage.values() for x in c.values())
assert {c['method'] for c in cases} == {
    'rerun001ExpiryBoundaryFencesAtomicallyAndPreservesErrorReplay',
    'rerun001CurrentClockIsReadAfterSessionLock',
    'rerun001ExpiryFaultsRollbackFenceAuditAndInboxTogether',
    'rerun001PriorTouchIsCurrentAndLateVerifierCannotUndoFence'}
manifest = {
    'id': 'PG448-expiry-selected-v2', 'formal': False, 'fullRun': False, 'native': False,
    'sourceHead': 'c560e5f8e7deb67af6c5c9feca37fc3962b3d91c',
    'sourceDirty': 'API revocation/Logout caller and two independent SQL/wire/fault test classes',
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')),
    'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')), 'branch': 'dev-foundation',
    'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg448_expiry_selected_v1.sh v2; six explicit modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report; eight named suites; failIfNoTests=true',
    'exitCode': 0, 'modules': modules, 'tests': 69, 'suites': 8, 'coverage': coverage,
    'staticAnalysis': {'modules': 6, 'findings': 0}, 'testCases': cases,
    'testIds': ['RERUN001-A..E', 'PT-AUT-008-R01..05', 'PT-AUT-LOGOUT-INBOX-001..007', 'PT-AUT-007'],
    'qa': ['QA-050'], 'ssc': ['SSC-171'], 'bugs': ['BUG-618'], 'ykt': ['YKT-437'],
    'before': {'id': 'PG448-expiry-before-v1', 'tests': 2, 'failures': 2, 'exitCode': 1,
               'logSha256': 'dbda036d301df589d4721474e466c3e14cf42846b89ee2a268719e8fd4e3c133'},
    'expected': 'Independent UI232/234 literal 280byte/SQL at expiry +/-1us; EXPIRED reason/0102 audit/ERROR atomic; immutable old-message0102/new-message0200; clock moves during lock; prior TOUCH extension and delayed verification rejected after current fence; all seven update/audit/Inbox/close faults rollback; current null boundaries',
    'actual': 'All independent wire/SQL/fault/lock/concurrency and legacy/ADMIN assertions passed; no provider exception data retained',
    'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'redaction': 'JUnit properties/stdout/stderr/provider text omitted; no key/token/session/cookie/password/raw log/dump',
    'limitations': ['Same-source security full regression required', 'Web nullable pending/retry/revoke key/local destruction and native full business assembly pending', 'Formal run24/1964PT/53scope unchanged'],
}
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 69, 'coverageClasses': 3, 'manifestSha256': sha(out / 'manifest.json')}))
