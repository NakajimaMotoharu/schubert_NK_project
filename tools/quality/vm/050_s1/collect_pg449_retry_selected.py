"""Frozen genuine Logout-facade/API selection; no native/full/formal acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg449-retry-selected-v1'
frozen = work / 'pg449-retry-selected-v1-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG449-retry-selected-v1'
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
assert prefix.with_suffix('.source').read_text().strip() == 'bc03db444106aa6b87fd8b0e9135e19bab25e3d1'
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
modules, coverage, no_executable = {}, {}, []
for module, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'), (5, 7, 10, 111, 34, 43), strict=True):
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
            counters = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in cls.findall('counter')}
            if counters:
                coverage[cls.get('name').rsplit('/', 1)[-1]] = counters
            else:
                no_executable.append(cls.get('name'))
assert no_executable == ['dev/codex/schubert/nk/web/revocation/RevocationRetryCoordinator$SqlWork']
assert len(coverage) == 11 and all(c['missed'] == 0 for value in coverage.values() for c in value.values())
assert sum(m['tests'] for m in modules.values()) == 210 and sum(m['suites'] for m in modules.values()) == 23
manifest = {
    'id': 'PG449-retry-selected-v1', 'formal': False, 'fullRun': False, 'native': False,
    'sourceHead': 'bc03db444106aa6b87fd8b0e9135e19bab25e3d1',
    'sourceDirty': 'RevocationRetryCoordinator/RevocationRetryException/independent RevocationRetryCoordinatorTest',
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')), 'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')),
    'branch': 'dev-foundation', 'startedAt': prefix.with_suffix('.started').read_text().strip(), 'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg449_selected.sh retry-selected-v1 bc03db444106aa6b87fd8b0e9135e19bab25e3d1 FieldCodecTest,StorageAttributeGuardTest,FixedServiceIdentityTest,DatabaseMigrationTest,StartupSchemaProjectionTest,InboxInspectionProgressBoundaryTest,LogCleanupProgressBoundaryTest,InspectionParentBoundaryTest,OutboxCleanupBoundaryTest,StepCleanupBoundaryTest,AuthSessionRevocationServiceTest,AuthSessionServiceTest,AuthenticationContextVerifierTest,AdminCommandAuthenticatorTest,LogoutInboxServiceTest,WebRequestTraceTest,RevocationPayloadCodecTest,PendingRevocationRepositoryTest,RevocationRetryCoordinatorTest,BackupStepRepositoryTest,BatchRunRepositoryTest,CleanupDatabaseSessionTest,CleanupStepValuesTest; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'preflight': 'Exact same selector passed six-module source-class validation before execution; no failIfNoTests bypass',
    'exitCode': 0, 'tests': 210, 'suites': 23, 'modules': modules, 'coverage': coverage,
    'noExecutableInterface': no_executable, 'coverageExclusions': [], 'staticAnalysis': {'modules': 6, 'findings': 0},
    'qa': ['QA-050'], 'ssc': ['SSC-171'], 'testIds': ['RERUN005A..H', 'RERUN004A..I', 'RERUN003A..G', 'RERUN002', 'RERUN001-F'],
    'expected': 'Independent UI literal256/280 and SQL: API commit then lost reply retained/fresh0200 closes; expired0102 retained/fresh0200 only proves revoke; current lease CAS, 100 claims, per-worker DB0 before remote; fatal identity/resource postconditions',
    'actual': 'Eight new independent real API/PostgreSQL and transport-fixture tests passed; 100 rows produced 100 unique Message IDs/Inbox/audit without retained rows; all JDBC fault postconditions passed',
    'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'redaction': 'JUnit properties/stdout/stderr/provider text omitted; no runtime secret/context/cookie/token/key/dump/raw log',
    'limitations': ['JMS transport is an independent fixture, not actual Artemis/native/IT/ST', 'Local Logout/worker join/key retention/full Web native/CHR and same-source whole-group full regression pending', 'Formal PT-WEB-20260925-24/1964PT/53scope unchanged'],
}
manifest['files'] = [{'path': str(path.relative_to(root)), 'sha256': sha(path)} for path in sorted(out.rglob('*')) if path.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 210, 'coverageClasses': 11, 'manifestSha256': sha(out / 'manifest.json')}))
