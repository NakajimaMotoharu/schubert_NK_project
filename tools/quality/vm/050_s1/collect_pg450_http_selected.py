"""Actual frozen HTTP Logout selection; no full/native/formal acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg450-http-selected-v2'
frozen = work / 'pg450-http-selected-v2-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG450-http-selected-v2'
source = '7be8ff8edca8dd2bf293d88efe821e71477d0b31'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
assert prefix.with_suffix('.source').read_text().strip() == source
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
modules, coverage = {}, {}
for module, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'), (5, 7, 10, 111, 106, 43), strict=True):
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
        if cls.findall('counter') and ('/revocation/' in cls.get('name') or name in ('JdbcWebSessionStore', 'SessionStoreException', 'EncryptedWebSessionRepository', 'LocalLogoutHandler', 'LogoutController', 'LogoutMvcConfiguration') or name.startswith(('WebSecurityAudit', 'WebRequestTrace'))):
            coverage[name] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in cls.findall('counter')}
assert len(coverage) == 24 and all(c['missed'] == 0 for value in coverage.values() for c in value.values())
assert sum(m['tests'] for m in modules.values()) == 282 and sum(m['suites'] for m in modules.values()) == 32
before = []
for tag, errors in (('http-before-v1', 8), ('http-selected-v1', 1)):
    b = work / ('pg450-' + tag)
    assert b.with_suffix('.exit').read_text().strip() == '1'
    failed = E.parse(work / ('pg450-' + tag + '-frozen/web/surefire-reports/TEST-dev.codex.schubert.nk.web.session.LogoutControllerTest.xml')).getroot()
    assert int(failed.get('errors')) == errors and int(failed.get('failures')) == 0
    before.append({'id': 'PG450-' + tag, 'exitCode': 1, 'errors': errors, 'failures': 0, 'skipped': 0, 'executedTests': 239, 'notRun': ['Batch', 'Web static/coverage'], 'logSha256': sha(b.with_suffix('.log')), 'sourceFilesSha256': sha(b.with_suffix('.source-files.sha256')), 'bytePreservation': str(work / ('pg450-' + tag + '-frozen')), 'failedTests': [c.get('name') for c in failed.findall('testcase') if c.find('error') is not None]})
manifest = {
    'id': 'PG450-http-selected-v2', 'sourceHead': source, 'sourceDirty': 'Logout HTTP/security/audit/route and independent fixture tests',
    'formal': False, 'fullRun': False, 'native': False, 'branch': 'dev-foundation',
    'startedAt': prefix.with_suffix('.started').read_text().strip(), 'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg450_selected.sh http-selected-v2 ' + source + ' exact32Testclasses; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'testClasses': sorted({c.get('classname') for m in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch') for p in (frozen / m / 'surefire-reports').glob('TEST-*.xml') for c in E.parse(p).getroot().findall('testcase')}),
    'exitCode': 0, 'tests': 282, 'suites': 32, 'modules': modules, 'coverage': coverage, 'coverageExclusions': [], 'staticAnalysis': {'modules': 6, 'findings': 0},
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')), 'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')), 'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'testIds': ['RERUN007A..H', 'RERUN006A..H', 'RERUN005A..H', 'RERUN004A..I', 'RERUN003A..G', 'RERUN002', 'RERUN001-F', 'REQ004', 'PT-WEB095..100', 'PT-WEB158..165'],
    'qa': ['QA-050'], 'ssc': ['SSC-171'], 'bugs': ['BUG-628', 'BUG-630', 'BUG-631'], 'ykt': ['YKT-445', 'YKT-447', 'YKT-448'],
    'expected': 'Literal HTTP302 /login?logout; expired secure HttpOnly SameSite=Lax cookie; old local absent/new row preserved; 0000/0200 no queue; failure NULL-expiry encrypted row, 0 attempts/5 seconds; GET/HEAD405, CSRF/anonymous403 and MQ0; fixed failure/fatal identity/cleared identity; 100 independent HTTP/rows/audits',
    'actual': 'Eight HTTP tests passed; 100 valid distinct session inputs and 100 HTTP302/durable retained rows/audit IDs, local0; handler/controller/MVC/audit/trace/revocation/session24 executable classes all counters missed0',
    'before': before, 'redaction': 'No JUnit properties/stdout/stderr, provider messages, raw logs, real credentials/cookie/context/token/key/dump',
    'limitations': ['Host HTTP/security/MVC/PostgreSQL and independent JMS fixture only; no actual Artemis or native owner proof', 'Retry worker/current revoke key owner/UNKNOWN stop guard and same-source whole regression pending', 'Formal PT-WEB-20260925-24/1964PT/53scope unchanged'],
}
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 282, 'coverageClasses': 24, 'manifestSha256': sha(out / 'manifest.json')}))
