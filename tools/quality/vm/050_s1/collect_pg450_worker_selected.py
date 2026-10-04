"""Actual frozen owned retry/stop/key selection; no full/native/formal acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg450-worker-selected-v4'
frozen = work / 'pg450-worker-selected-v4-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG450-worker-selected-v4'
source = '6d36e0d098765b2f03bd441bad26d70929d5a500'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
assert prefix.with_suffix('.source').read_text().strip() == source
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
modules, coverage = {}, {}
for module, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'), (5, 7, 10, 111, 151, 43), strict=True):
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
        if cls.findall('counter') and ('/revocation/' in cls.get('name') or name in ('JdbcWebSessionStore', 'SessionStoreException', 'EncryptedWebSessionRepository', 'LocalLogoutHandler', 'LogoutController', 'LogoutMvcConfiguration', 'WebLogApplicationRuntime', 'WebHttpServer', 'WebNativeCodecs', 'WebNativeCodecs$1', 'WebLogReplayWorker', 'WebLogReplayWorker$Snapshot') or name.startswith(('WebSecurityAudit', 'WebRequestTrace'))):
            coverage[name] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in cls.findall('counter')}
assert len(coverage) == 32 and all(c['missed'] == 0 for value in coverage.values() for c in value.values())
assert sum(m['tests'] for m in modules.values()) == 327 and sum(m['suites'] for m in modules.values()) == 39
before = []
for tag, stage, tests, failures, errors in (
    ('worker-before-v3', 'Web PT; Batch/Web static not run', 57, 2, 0),
    ('worker-selected-v1', 'Web testCompile; Web PT/Batch/Web static not run', 133, 0, 0),
    ('worker-selected-v2', 'Web PT; Batch/Web static not run', 275, 0, 1),
):
    p = work / ('pg450-' + tag)
    assert p.with_suffix('.exit').read_text().strip() == '1'
    before.append({'id': 'PG450-' + tag, 'accepted': False, 'exitCode': 1,
        'stage': stage, 'executedTests': tests, 'failures': failures, 'errors': errors,
        'logSha256': sha(p.with_suffix('.log')),
        'sourceFilesSha256': sha(p.with_suffix('.source-files.sha256')),
        'bytePreservation': str(work / ('pg450-' + tag + '-frozen'))})
manifest = {
    'id': 'PG450-worker-selected-v4', 'sourceHead': source, 'sourceDirty': 'PG-D364 owned retry worker/current third key/fatal propagation/confirmed stop phases and independent tests',
    'formal': False, 'fullRun': False, 'native': False, 'branch': 'dev-foundation',
    'startedAt': prefix.with_suffix('.started').read_text().strip(), 'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg450_selected.sh worker-selected-v4 ' + source + ' exact39Testclasses; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'testClasses': sorted({c.get('classname') for m in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch') for p in (frozen / m / 'surefire-reports').glob('TEST-*.xml') for c in E.parse(p).getroot().findall('testcase')}),
    'exitCode': 0, 'tests': 327, 'suites': 39, 'modules': modules, 'coverage': coverage, 'coverageExclusions': [], 'staticAnalysis': {'modules': 6, 'findings': 0},
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')), 'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')), 'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'testIds': ['RERUN008A..E', 'NKEY005', 'Log unknown join/hidden fatal', 'Runtime confirmed phase/HTTP stop-destroy phase', 'REQUEST actual valve', 'RERUN007A..H', 'RERUN006A..H', 'RERUN005A..H', 'RERUN004A..I', 'RERUN003A..G', 'RERUN002', 'RERUN001-F', 'REQ004', 'PT-WEB095..100', 'PT-WEB158..165'],
    'qa': ['QA-050'], 'ssc': ['SSC-171'], 'bugs': ['BUG-629', 'BUG-632', 'BUG-633', 'BUG-634'], 'ykt': ['YKT-446', 'YKT-449'],
    'expected': 'Actual retry scheduling; borrowed coordinator retained; repeated UNKNOWN join rejected; confirmed phase retained/retried; fatal identity terminal, current third codec cleared keys and independent JCA vector; literal HTTP302 /login?logout; expired secure HttpOnly SameSite=Lax cookie; old local absent/new row preserved; 0000/0200 no queue; failure NULL-expiry encrypted row, 0 attempts/5 seconds; GET/HEAD405, CSRF/anonymous403 and MQ0; fixed failure/fatal identity/cleared identity; 100 independent HTTP/rows/audits',
    'actual': '327 PT/39 suites passed; selected32 executable classes B447/L1282/M188/C32 all missed0; native key public vector matches independent JCA; worker actual join and confirmed stop phase postconditions',
    'before': before, 'redaction': 'No JUnit properties/stdout/stderr, provider messages, raw logs, real credentials/cookie/context/token/key/dump',
    'limitations': ['Host HTTP/security/MVC/PostgreSQL and independent JMS fixture only; no actual Artemis or native owner proof', 'Legacy startPath/closeAfterFailure and native outer callback UNKNOWN retention remain open BUG629/YKT446; same-source full regression pending', 'Formal PT-WEB-20260925-24/1964PT/53scope unchanged'],
}
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 327, 'coverageClasses': 32, 'manifestSha256': sha(out / 'manifest.json')}))
