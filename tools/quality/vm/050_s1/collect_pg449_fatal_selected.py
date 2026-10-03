"""Frozen fatal-close public-boundary regression capture; not full or native acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E
root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg449-fatal-selected-v1'
frozen = work / 'pg449-fatal-selected-v1-frozen'
out = root / 'evidence/01_PT/007_NK-AUT-001/evidence/provisional/PG449-fatal-selected-v1'
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log and log.count('BugInstance size is 0') == 6
names = {'AuthSessionRevocationService', 'AuthSessionService', 'AuthenticationContextVerifier',
         'AdminCommandAuthenticator', 'AuthenticationInfrastructureException', 'LogoutInboxService'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
modules, coverage = {}, {}
for name, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'),
                          (5, 7, 10, 44, 10, 8), strict=True):
    reports = sorted((frozen / name / 'surefire-reports').glob('TEST-*.xml'))
    count = 0
    for report in reports:
        suite = E.parse(report).getroot()
        assert all(int(suite.get(k)) == 0 for k in ('failures', 'errors', 'skipped'))
        assert int(suite.get('tests')) == len(suite.findall('testcase'))
        safe = E.Element('testsuite', {k: suite.get(k) for k in ('name', 'tests', 'failures', 'errors', 'skipped', 'time')})
        for case in suite.findall('testcase'):
            assert all(c.tag in ('system-out', 'system-err') for c in case)
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
    for c in E.parse(frozen / name / 'site/jacoco/jacoco.xml').findall('.//class'):
        simple = c.get('name').rsplit('/', 1)[-1]
        if simple in names:
            coverage[simple] = {k.get('type'): {'missed': int(k.get('missed')), 'covered': int(k.get('covered'))} for k in c.findall('counter')}
assert set(coverage) == names and all(k['missed'] == 0 for v in coverage.values() for k in v.values())
manifest = {
    'id': 'PG449-fatal-selected-v1', 'formal': False, 'fullRun': False, 'native': False,
    'sourceHead': 'd35bbcd29f559343483cdc93b94cf24bc0112d08', 'sourceDirty': 'Five API security classes and independent AuthSessionRevocationServiceTest',
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')), 'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')),
    'finishedAt': prefix.with_suffix('.completed').read_text().strip(), 'branch': 'dev-foundation',
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg449_selected.sh fatal-selected-v1 d35bbcd29f559343483cdc93b94cf24bc0112d08 FieldCodecTest,StorageAttributeGuardTest,FixedServiceIdentityTest,AuthSessionRevocationServiceTest,AuthSessionServiceTest,AuthenticationContextVerifierTest,AdminCommandAuthenticatorTest,LogoutInboxServiceTest,WebRequestTraceTest,CleanupStepValuesTest; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'exitCode': 0, 'tests': 84, 'suites': 10, 'modules': modules, 'coverage': coverage,
    'staticAnalysis': {'modules': 6, 'findings': 0}, 'bugs': ['BUG-622'], 'ykt': ['YKT-440'], 'qa': ['QA-050'], 'ssc': ['SSC-171'],
    'testIds': ['RERUN001-F', 'RERUN001-A..E', 'PT-AUT-008-R01..05', 'PT-AUT-007', 'PT-ADM-034/036/039'],
    'before': {'id': 'PG449-fatal-before-v1', 'tests': 1, 'failures': 1, 'exitCode': 1, 'logSha256': '6568f8b554624c250f331cf67ce568511fbb7e323f7e0b46e227e8f235606f72'},
    'expected': 'Original fatal Error identity across six denial public boundaries, nested SQL-primary fatal close and bounded cyclic suppressed graph; rollback SQL0. Ordinary SQLException redacted fixed infrastructure, wire/session authority unchanged.',
    'actual': 'All real isolated JDBC/proxy fault, identity, rollback and existing authority/Inbox/100-replay assertions passed',
    'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'redaction': 'JUnit properties/stdout/stderr/provider text omitted; no runtime credential/context/token/session/cookie/key/dump/raw log',
    'limitations': ['Same-source QA050 ownership group full regression required', 'V027/revoke retry/key/local destruction/full Web native/CHR/formal run24 pending'],
}
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 84, 'coverageClasses': 6, 'manifestSha256': sha(out / 'manifest.json')}))
