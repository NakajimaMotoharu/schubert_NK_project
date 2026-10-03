"""Frozen QA050 V027 and fatal-close selection; never formal/native/full acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg449-null-expiry-selected-v3'
frozen = work / 'pg449-null-expiry-selected-v3-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG449-null-expiry-selected-v3'
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log
assert 'do not match with execution data' not in log and log.count('BugInstance size is 0') == 6
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
names = {'AuthSessionRevocationService', 'AuthSessionService', 'AuthenticationContextVerifier',
         'AdminCommandAuthenticator', 'AuthenticationInfrastructureException', 'LogoutInboxService'}
modules, coverage = {}, {}
for name, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'),
                          (5, 7, 10, 111, 10, 43), strict=True):
    reports = sorted((frozen / name / 'surefire-reports').glob('TEST-*.xml'))
    count = 0
    for report in reports:
        suite = E.parse(report).getroot()
        assert all(int(suite.get(k)) == 0 for k in ('failures', 'errors', 'skipped'))
        assert int(suite.get('tests')) == len(suite.findall('testcase'))
        safe = E.Element('testsuite', {k: suite.get(k) for k in ('name', 'tests', 'failures', 'errors', 'skipped', 'time')})
        for case in suite.findall('testcase'):
            assert all(child.tag in ('system-out', 'system-err') for child in case)
            E.SubElement(safe, 'testcase', {k: case.get(k) for k in ('name', 'classname', 'time')})
        destination = out / 'junit' / name / report.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        E.indent(safe)
        E.ElementTree(safe).write(destination, encoding='utf-8', xml_declaration=True)
        count += int(suite.get('tests'))
    assert count == expected
    modules[name] = {'tests': count, 'suites': len(reports), 'failures': 0, 'errors': 0, 'skipped': 0}
    static = E.parse(frozen / name / 'spotbugsXml.xml').getroot()
    assert not static.findall('BugInstance') and int(static.find('Errors').get('errors')) == 0
    for cls in E.parse(frozen / name / 'site/jacoco/jacoco.xml').findall('.//class'):
        simple = cls.get('name').rsplit('/', 1)[-1]
        if simple in names:
            coverage[simple] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in cls.findall('counter')}
assert set(coverage) == names and all(c['missed'] == 0 for value in coverage.values() for c in value.values())
assert sum(value['tests'] for value in modules.values()) == 186
assert sum(value['suites'] for value in modules.values()) == 20
manifest = {
    'id': 'PG449-null-expiry-selected-v3', 'formal': False, 'fullRun': False, 'native': False,
    'sourceHead': 'd35bbcd29f559343483cdc93b94cf24bc0112d08',
    'sourceDirty': 'Five API security classes, independent auth/migration/inventory API and Batch tests, append-only V027',
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')),
    'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')),
    'branch': 'dev-foundation', 'startedAt': prefix.with_suffix('.started').read_text().strip(),
    'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg449_selected.sh null-expiry-selected-v3 d35bbcd29f559343483cdc93b94cf24bc0112d08 FieldCodecTest,StorageAttributeGuardTest,FixedServiceIdentityTest,DatabaseMigrationTest,StartupSchemaProjectionTest,InboxInspectionProgressBoundaryTest,LogCleanupProgressBoundaryTest,InspectionParentBoundaryTest,OutboxCleanupBoundaryTest,StepCleanupBoundaryTest,AuthSessionRevocationServiceTest,AuthSessionServiceTest,AuthenticationContextVerifierTest,AdminCommandAuthenticatorTest,LogoutInboxServiceTest,WebRequestTraceTest,BackupStepRepositoryTest,BatchRunRepositoryTest,CleanupDatabaseSessionTest,CleanupStepValuesTest; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'exitCode': 0, 'tests': 186, 'suites': 20, 'modules': modules, 'coverage': coverage,
    'staticAnalysis': {'modules': 6, 'findings': 0}, 'bugs': ['BUG-622', 'BUG-623', 'BUG-624'],
    'ykt': ['YKT-440', 'YKT-441'], 'qa': ['QA-050'], 'ssc': ['SSC-171'],
    'testIds': ['RERUN002', 'RERUN001-F', 'PT-DB-SCHEMA001..008', 'BCATALOG001', 'PT-AUT-007/008'],
    'expected': 'NULL expiry retained under exact WEB role; constraints, grants and old migrations unchanged; independent 27-version/28-history inventories; fatal identity and rollback across six denial boundaries',
    'actual': 'All independent SQL/catalog/NULL/constraint/auth-fault and API/Batch inventory assertions passed',
    'before': [
        {'id': 'PG449-null-expiry-before-v1', 'exitCode': 1, 'error': 'Wrong fixture role; BUG623'},
        {'id': 'PG449-null-expiry-before-v2', 'exitCode': 1, 'error': 'Unimplemented NULL TDD; not BUG'},
        {'id': 'PG449-null-expiry-selected-v1', 'exitCode': 1, 'failures': 1, 'error': 'CSV inventory; BUG624'},
        {'id': 'PG449-null-expiry-selected-v2', 'exitCode': 1, 'failures': 5, 'error': 'Total history inventory; BUG624'},
    ],
    'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'redaction': 'JUnit properties/stdout/stderr/provider text omitted; no credential/raw session/context/cookie/token/key/dump/raw log',
    'limitations': ['Same-source security/DDL/Logout ownership full regression pending', 'Dedicated revoke codec/claim/retry/key retention/local Logout/native full Web/CHR/formal run24 pending'],
}
manifest['files'] = [{'path': str(path.relative_to(root)), 'sha256': sha(path)} for path in sorted(out.rglob('*')) if path.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 186, 'suites': 20, 'coverageClasses': 6, 'manifestSha256': sha(out / 'manifest.json')}))
