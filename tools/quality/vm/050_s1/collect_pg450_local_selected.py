"""Frozen local Logout SQL/fatal selection. Never native/full/formal acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg450-local-selected-v1'
frozen = work / 'pg450-local-selected-v1-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG450-local-selected-v1'
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
assert prefix.with_suffix('.source').read_text().strip() == 'adf261fb782f0902b8634639273e22da65728d75'
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
modules, coverage = {}, {}
for module, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'), (5, 7, 10, 111, 77, 43), strict=True):
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
        name = cls.get('name').rsplit('/', 1)[-1]
        if cls.findall('counter') and ('/revocation/' in cls.get('name') or name in ('JdbcWebSessionStore', 'SessionStoreException', 'EncryptedWebSessionRepository')):
            coverage[name] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in cls.findall('counter')}
assert len(coverage) == 16 and all(c['missed'] == 0 for value in coverage.values() for c in value.values())
assert sum(m['tests'] for m in modules.values()) == 253 and sum(m['suites'] for m in modules.values()) == 28
selector = 'FieldCodecTest,StorageAttributeGuardTest,FixedServiceIdentityTest,DatabaseMigrationTest,StartupSchemaProjectionTest,InboxInspectionProgressBoundaryTest,LogCleanupProgressBoundaryTest,InspectionParentBoundaryTest,OutboxCleanupBoundaryTest,StepCleanupBoundaryTest,AuthSessionRevocationServiceTest,AuthSessionServiceTest,AuthenticationContextVerifierTest,AdminCommandAuthenticatorTest,LogoutInboxServiceTest,WebRequestTraceTest,RevocationPayloadCodecTest,PendingRevocationRepositoryTest,RevocationRetryCoordinatorTest,LocalLogoutCoordinatorTest,EncryptedWebSessionRepositoryTest,JdbcWebSessionStoreTest,SpringWebSessionTest,SessionOperationTokenLifecycleTest,BackupStepRepositoryTest,BatchRunRepositoryTest,CleanupDatabaseSessionTest,CleanupStepValuesTest'
manifest = {
    'id': 'PG450-local-selected-v1', 'formal': False, 'fullRun': False, 'native': False,
    'sourceHead': 'adf261fb782f0902b8634639273e22da65728d75',
    'sourceDirty': 'LocalLogoutCoordinator/session atomic retain-delete/SessionStoreException fatal/SQL boundary guards and independent tests',
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')), 'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')),
    'branch': 'dev-foundation', 'startedAt': prefix.with_suffix('.started').read_text().strip(), 'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg450_selected.sh local-selected-v1 adf261fb782f0902b8634639273e22da65728d75 ' + selector + '; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'preflight': 'Same exact selector accepted six module source Test-class inventory before execution',
    'exitCode': 0, 'tests': 253, 'suites': 28, 'modules': modules, 'coverage': coverage,
    'coverageExclusions': [], 'staticAnalysis': {'modules': 6, 'findings': 0}, 'qa': ['QA-050'], 'ssc': ['SSC-171'],
    'bugs': ['BUG-628'], 'ykt': ['YKT-445'], 'testIds': ['RERUN006A..H', 'RERUN006JdbcEverySessionCatalogue', 'RERUN005A..H', 'RERUN004A..I', 'RERUN003A..G', 'RERUN002', 'RERUN001-F'],
    'expected': 'Independent literal256/280, direct SQL and DataOutputStream/JCA: confirmed no queue/old local deletion; unknown/0102 durable NULL-expiry queue and local atomic deletion; failures try independent deletion/never success; borrowed/new Login preserved; fatal identity and JDBC resource postconditions',
    'actual': 'Eight Local tests and one new JDBC public-boundary matrix passed; 100 local rows destroyed and 100 durable unique retries/Message IDs retained; nested close/cycle/rollback/same-fatal identity preserved; all fixed nonfatal catalog checks passed',
    'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'before': {'id': 'PG450-local-before-v1', 'exitCode': 1, 'finishedAt': '2026-10-04T10:15:35+09:00', 'sourceHead': 'adf261fb782f0902b8634639273e22da65728d75', 'dirty': 'Local atomic/coordinator initial Test, before fatal guards', 'executedTests': 197, 'failures': 1, 'errors': 0, 'skipped': 0, 'notRun': ['Batch', 'Web static/coverage report'], 'failedTest': 'rerun006eFatalWireAndFatalSuppressedDbClosePreserveIdentityAfterLocalCleanup', 'expected': 'original AssertionError', 'actual': 'SessionStoreException', 'logSha256': 'f97a7a34389e370b313faffcc4afe820537f81069be6ed80520f0c3a36f91ace', 'bytePreservation': str(work / 'pg450-local-before-v1-frozen')},
    'redaction': 'JUnit properties/stdout/stderr/provider text omitted; no real credential/context/cookie/token/key/dump/raw log',
    'limitations': ['Transport fixture and host PostgreSQL only; HTTP Cookie/CSRF/context/drain/worker join/key lifetime/full native/CHR not accepted', 'Same-source ownership/security full regression pending', 'Formal PT-WEB-20260925-24/1964PT/53scope unchanged'],
}
manifest['files'] = [{'path': str(path.relative_to(root)), 'sha256': sha(path)} for path in sorted(out.rglob('*')) if path.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 253, 'coverageClasses': 16, 'manifestSha256': sha(out / 'manifest.json')}))
