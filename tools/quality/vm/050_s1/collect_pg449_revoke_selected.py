"""Frozen dedicated-revoke codec capture; no native/full/formal acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg449-revoke-codec-selected-v1'
frozen = work / 'pg449-revoke-codec-selected-v1-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG449-revoke-codec-selected-v1'
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
names = {'RevocationPayloadCodec', 'RevocationPayloadIdentity', 'EncryptedRevocationPayload',
         'RevocationPayloadException', 'RevocationPayloadException$Reason'}
modules, coverage = {}, {}
for name, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'), (5, 7, 10, 111, 17, 43), strict=True):
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
        path = out / 'junit' / name / report.name
        path.parent.mkdir(parents=True, exist_ok=True)
        E.indent(safe)
        E.ElementTree(safe).write(path, encoding='utf-8', xml_declaration=True)
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
assert sum(m['suites'] for m in modules.values()) == 21
manifest = {
    'id': 'PG449-revoke-codec-selected-v1', 'formal': False, 'fullRun': False, 'native': False,
    'sourceHead': 'c230694c0f4ec4a7cf2f3e26cb1cd65678293c52', 'sourceDirty': 'Dedicated web.revocation four classes/package and independent RevocationPayloadCodecTest',
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')), 'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')),
    'branch': 'dev-foundation', 'startedAt': prefix.with_suffix('.started').read_text().strip(), 'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg449_selected.sh revoke-codec-selected-v1 c230694c0f4ec4a7cf2f3e26cb1cd65678293c52 FieldCodecTest,StorageAttributeGuardTest,FixedServiceIdentityTest,DatabaseMigrationTest,StartupSchemaProjectionTest,InboxInspectionProgressBoundaryTest,LogCleanupProgressBoundaryTest,InspectionParentBoundaryTest,OutboxCleanupBoundaryTest,StepCleanupBoundaryTest,AuthSessionRevocationServiceTest,AuthSessionServiceTest,AuthenticationContextVerifierTest,AdminCommandAuthenticatorTest,LogoutInboxServiceTest,WebRequestTraceTest,RevocationPayloadCodecTest,BackupStepRepositoryTest,BatchRunRepositoryTest,CleanupDatabaseSessionTest,CleanupStepValuesTest; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'exitCode': 0, 'tests': 193, 'suites': 21, 'modules': modules, 'coverage': coverage, 'staticAnalysis': {'modules': 6, 'findings': 0},
    'qa': ['QA-050'], 'ssc': ['SSC-171'], 'implementationDecision': 'PG-D359', 'testIds': ['RERUN003A..G', 'RERUN002', 'RERUN001-F'],
    'expected': 'Independent JCA envelope/6-field DataOutputStream AAD, 64 lowercase-hex context, current/previous key isolation, all mutations fail closed, owned nonce/copy/close and 100 fresh parallel nonces; no authorization/expiry/delete proof',
    'actual': 'All seven dedicated codec tests and inherited 186-test selection passed',
    'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'redaction': 'JUnit properties/stdout/stderr/provider text omitted; only synthetic public crypto fixtures in source; no runtime secret/session/context/token/key/dump/raw log',
    'limitations': ['Same-source QA050 security/DDL/ownership full regression pending', 'Pending claim/retry/key retirement/local Logout/full Web native/CHR/formal run24 pending'],
}
manifest['files'] = [{'path': str(path.relative_to(root)), 'sha256': sha(path)} for path in sorted(out.rglob('*')) if path.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 193, 'coverageClasses': 5, 'manifestSha256': sha(out / 'manifest.json')}))
