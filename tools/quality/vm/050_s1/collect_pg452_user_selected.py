"""Actual frozen atomic User token/Version selection; no full/native/formal acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg452-user-selected-v1'
frozen = work / 'pg452-user-selected-v1-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG452-user-selected-v1'
source = '1034d60a329a4f1c0f4d7e20480408ce29e124db'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
assert prefix.with_suffix('.source').read_text().strip() == source
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
modules, coverage = {}, {}
for module, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'), (5, 7, 10, 51, 101, 43), strict=True):
    reports = sorted((frozen / module / 'surefire-reports').glob('TEST-*.xml'))
    count = 0
    for report in reports:
        suite = E.parse(report).getroot()
        assert all(int(suite.get(k)) == 0 for k in ('failures', 'errors', 'skipped'))
        assert int(suite.get('tests')) == len(suite.findall('testcase'))
        safe = E.Element('testsuite', {k: suite.get(k) for k in ('name', 'tests', 'failures', 'errors', 'skipped', 'time')})
        for case in suite.findall('testcase'):
            assert all(child.tag in ('system-out', 'system-err') for child in case)
            E.SubElement(safe, 'testcase', {k: case.get(k) for k in ('name', 'classname', 'time')})
        p = out / 'junit' / module / report.name
        p.parent.mkdir(parents=True, exist_ok=True)
        E.indent(safe)
        E.ElementTree(safe).write(p, encoding='utf-8', xml_declaration=True)
        count += int(suite.get('tests'))
    assert count == expected
    modules[module] = {'tests': count, 'suites': len(reports), 'failures': 0, 'errors': 0, 'skipped': 0}
    static = E.parse(frozen / module / 'spotbugsXml.xml').getroot()
    assert not static.findall('BugInstance') and int(static.find('Errors').get('errors')) == 0
    for cls in E.parse(frozen / module / 'site/jacoco/jacoco.xml').findall('.//class'):
        name = cls.get('name').rsplit('/', 1)[-1]
        if cls.findall('counter') and name in ('SessionOperationTokenLifecycle', 'SessionOperationToken', 'UserDetailViewModel', 'UserAdminController'):
            coverage[name] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in cls.findall('counter')}
assert len(coverage) == 4 and all(c['missed'] == 0 for value in coverage.values() for c in value.values())
assert sum(m['tests'] for m in modules.values()) == 217 and sum(m['suites'] for m in modules.values()) == 22
before = [{
    'id': 'PG452-user-before-v1', 'accepted': False, 'exitCode': 1,
    'executedTests': 174, 'failures': 1, 'errors': 2, 'skipped': 0,
    'notRun': ['Batch', 'Web static/coverage'],
    'logSha256': sha(work / 'pg452-user-before-v1.log'),
    'sourceFilesSha256': sha(work / 'pg452-user-before-v1.source-files.sha256'),
    'bytePreservation': str(work / 'pg452-user-before-v1-frozen'),
}]
assert (work / 'pg452-user-before-v1.exit').read_text().strip() == '1'
manifest = {
    'id': 'PG452-user-selected-v1', 'sourceHead': source, 'sourceDirty': 'PG-D366 atomic visible form issuance and independent group tests; BUG639 zero Version correction and literal positive test; no full User HTTP assembly yet',
    'formal': False, 'fullRun': False, 'native': False, 'branch': 'dev-foundation',
    'startedAt': prefix.with_suffix('.started').read_text().strip(), 'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg452_selected.sh user-selected-v1 ' + source + ' exact22Testclasses; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'testClasses': sorted({c.get('classname') for m in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch') for p in (frozen / m / 'surefire-reports').glob('TEST-*.xml') for c in E.parse(p).getroot().findall('testcase')}),
    'exitCode': 0, 'tests': 217, 'suites': 22, 'modules': modules, 'coverage': coverage, 'coverageExclusions': [], 'staticAnalysis': {'modules': 6, 'findings': 0},
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')), 'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')), 'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'testIds': ['TOKV209A', 'TOKV209B', 'TOKV209C', 'TOKV209D', 'TOKV209E', 'PT-USER-DETAIL009', 'TOKV207208 existing', 'PT-USER-DETAIL001..008 existing'],
    'qa': ['QA-049'], 'ssc': ['SSC-177'], 'bugs': ['BUG-639', 'BUG-640'], 'ykt': ['YKT-452', 'YKT-453'],
    'expected': 'Atomic actual visible form group; pending0..10/need1..4; no UUID or partial pending on shortage; only oldest consumed retirement with stable ties; original/group collision whole rollback; actual commit/close unknown reread;100competing groups5success95conflict/10UUID/10pending; explicit null and deleted boundaries; literal UDT320 valid Version0/max and no ID/active count weakening',
    'actual': '217PT/22suite/FES0/static6zero; changed and bound4 executable classes B68/L206/M33/C4 all missed0; original and 100 parallel SQL postconditions passed; Version0 direct display passed',
    'before': before, 'redaction': 'No JUnit properties/stdout/stderr, provider messages, raw logs, real credentials/cookie/context/token/key/dump',
    'limitations': ['Selected host session/User reference/API/PostgreSQL and independent JMS fixture only; no actual Artemis or native proof', 'Full User new/4mutation HTTP assembly and same-group full regression are still pending; this collector was added after frozen selection', 'Formal PT-WEB-20260925-24/1964PT/53scope unchanged'],
}
assert manifest['ssc'] == ['SSC-177'] and manifest['qa'] == ['QA-049']
assert manifest['bugs'] == ['BUG-639', 'BUG-640'] and manifest['ykt'] == ['YKT-452', 'YKT-453']
assert manifest['testIds'][:6] == ['TOKV209A', 'TOKV209B', 'TOKV209C', 'TOKV209D', 'TOKV209E', 'PT-USER-DETAIL009']
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 217, 'coverageClasses': 4, 'manifestSha256': sha(out / 'manifest.json')}))
