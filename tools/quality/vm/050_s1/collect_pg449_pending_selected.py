"""Source-frozen retained-revoke SQL selection. Never genuine-wire/native/full/formal acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg449-pending-selected-v2'
frozen = work / 'pg449-pending-selected-v2-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG449-pending-selected-v2'
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
modules, coverage = {}, {}
for module, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'), (5, 7, 10, 111, 26, 43), strict=True):
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
        path = out / 'junit' / module / report.name
        path.parent.mkdir(parents=True, exist_ok=True)
        E.indent(safe)
        E.ElementTree(safe).write(path, encoding='utf-8', xml_declaration=True)
        count += int(suite.get('tests'))
    assert count == expected
    modules[module] = {'tests': count, 'suites': len(reports), 'failures': 0, 'errors': 0, 'skipped': 0}
    static = E.parse(frozen / module / 'spotbugsXml.xml').getroot()
    assert not static.findall('BugInstance') and int(static.find('Errors').get('errors')) == 0
    for cls in E.parse(frozen / module / 'site/jacoco/jacoco.xml').findall('.//class'):
        if cls.get('name').startswith('dev/codex/schubert/nk/web/revocation/'):
            coverage[cls.get('name').rsplit('/', 1)[-1]] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in cls.findall('counter')}
assert len(coverage) == 8 and all(c['missed'] == 0 for value in coverage.values() for c in value.values())
assert sum(m['tests'] for m in modules.values()) == 202 and sum(m['suites'] for m in modules.values()) == 22
manifest = {
    'id': 'PG449-pending-selected-v2', 'formal': False, 'fullRun': False, 'native': False,
    'sourceHead': '1a61825129bef39ee952f926a02cea7f2c8c61ec', 'sourceDirty': 'PendingRevocationRepository/ClaimedRevocation/RevocationFailureCode/independent Test/preflight tool',
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')), 'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')),
    'branch': 'dev-foundation', 'startedAt': prefix.with_suffix('.started').read_text().strip(), 'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg449_selected.sh pending-selected-v2 1a61825129bef39ee952f926a02cea7f2c8c61ec FieldCodecTest,StorageAttributeGuardTest,FixedServiceIdentityTest,DatabaseMigrationTest,StartupSchemaProjectionTest,InboxInspectionProgressBoundaryTest,LogCleanupProgressBoundaryTest,InspectionParentBoundaryTest,OutboxCleanupBoundaryTest,StepCleanupBoundaryTest,AuthSessionRevocationServiceTest,AuthSessionServiceTest,AuthenticationContextVerifierTest,AdminCommandAuthenticatorTest,LogoutInboxServiceTest,WebRequestTraceTest,RevocationPayloadCodecTest,PendingRevocationRepositoryTest,BackupStepRepositoryTest,BatchRunRepositoryTest,CleanupDatabaseSessionTest,CleanupStepValuesTest; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'preflight': 'validate_selected_suites.py invoked with the same explicit selector as the runner; exact six-module check passed before launch',
    'exitCode': 0, 'tests': 202, 'suites': 22, 'modules': modules, 'coverage': coverage, 'staticAnalysis': {'modules': 6, 'findings': 0},
    'bugs': ['BUG-625', 'BUG-626', 'BUG-627'], 'ykt': ['YKT-442', 'YKT-443', 'YKT-444'], 'qa': ['QA-050'], 'ssc': ['SSC-171'],
    'testIds': ['RERUN004A..I', 'RERUN003A..G', 'RERUN002', 'RERUN001-F'],
    'expected': 'Literal 5/30/300/900-second backoff and 100 saturation, NULL/past expiry retained, unique lease CAS/due/100/SKIP LOCKED, corrupt oversize original preserved without queue poisoning, all JDBC owners rollback; codec isolation',
    'actual': 'All nine independent PostgreSQL/fault SQL tests and inherited 193-test selection passed; no remote calls yet',
    'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'before': [ {'id': 'PG449-pending-before-v1', 'exitCode': 1, 'logSha256': '69ca0b0c3f844056c0d420245d684e8bf2761d81771f2d5c3bfe1a8fe3d90128', 'bugs': ['BUG-625'], 'scope': 'API selector gate; Web not run'},
        {'id': 'PG449-pending-before-v2', 'exitCode': 1, 'logSha256': '644e75e191008c4602ba22cb6a74d85c7ce322063cd1ead17ca3dd9a416dd827', 'bugs': ['BUG-626'], 'scope': 'Web oversized SQL error; Batch not run'},
        {'id': 'PG449-pending-selected-v1', 'exitCode': 1, 'logSha256': 'ffeab61095e6b20ce844082431287c7ffa547eddead4a53df43f3194b1886bb7', 'bugs': ['BUG-627'], 'scope': 'Web PT passed/static3; Batch not run'} ],
    'redaction': 'JUnit properties/stdout/stderr/provider text omitted; no runtime secret/context/cookie/token/key/dump/raw log',
    'limitations': ['Genuine-wire proof and DB-before-remote ownership not connected', 'Local Logout/HTTP drain/key retention/full Web native/CHR and same-source whole-group full regression pending', 'Formal PT-WEB-20260925-24/1964PT/53scope unchanged'],
}
manifest['files'] = [{'path': str(path.relative_to(root)), 'sha256': sha(path)} for path in sorted(out.rglob('*')) if path.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 202, 'coverageClasses': 8, 'manifestSha256': sha(out / 'manifest.json')}))
