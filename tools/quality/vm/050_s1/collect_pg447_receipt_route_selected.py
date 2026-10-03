"""RCPT006 selected-run sanitized capture; never formal/full/native acceptance."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg447-http-selected-v5'
frozen = work / 'pg447-http-selected-v5-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG447-http-selected-v5'
assert not out.exists()
assert prefix.with_suffix('.exit').read_text().strip() == '0'
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log
assert log.count('BugInstance size is 0') == 6
modules, coverage, cases = {}, {}, []
names = {'QuestionController', 'QuestionSubmitViewModel', 'QuestionAcceptedViewModel',
         'QuestionAcceptanceMvcConfiguration', 'QuestionDetailViewModel', 'QuestionSubmitForm',
         'ReceiptReference', 'ReceiptReferenceRepository', 'ReceiptReferenceException',
         'WebRequestTrace', 'WebRequestTrace$Scope', 'WebRequestLogProducer',
         'HttpRequestLoggingValve', 'WebRequestRouteInterceptor', 'RequestLogMvcConfiguration'}
for name, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'),
                          (5, 7, 10, 5, 68, 43), strict=True):
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
            assert all(c.tag in ('system-out', 'system-err') for c in case)
            E.SubElement(safe, 'testcase', {k: case.get(k) for k in ('name', 'classname', 'time')})
            if case.get('name').startswith('rcpt006'):
                cases.append({'testId': 'RCPT006' + case.get('name')[7],
                              'method': case.get('name'), 'junit': 'junit/' + name + '/' + report.name})
        destination = out / 'junit' / name / report.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        E.indent(safe)
        E.ElementTree(safe).write(destination, encoding='utf-8', xml_declaration=True)
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
assert len(cases) == 11 and {c['testId'] for c in cases} == {'RCPT006' + c for c in 'ABCDEFGH'}
js = frozen / 'web/pt-question-script'
tap = (js / 'node.tap').read_text()
assert all(x in tap.splitlines() for x in
           ('# tests 8', '# pass 8', '# fail 0', '# cancelled 0', '# skipped 0', '# todo 0'))
assert re.search(r'question-input-validation\.js\s*\|\s*100\.00\s*\|\s*100\.00\s*\|\s*100\.00', tap)
proof = json.loads((js / 'PT-QST-JS001-node.json').read_text())
assert proof['testExit'] == proof['syntaxExit'] == proof['failed'] == proof['skipped'] == proof['todo'] == 0
(out / 'logs').mkdir()
(out / 'logs/byte-counter.txt').write_text(tap)
(out / 'logs/byte-counter.json').write_text(json.dumps(proof, indent=2) + '\n')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = {
    'id': 'PG447-http-selected-v5', 'formal': False, 'fullRun': False, 'native': False,
    'sourceHead': '4be6d85a9adc953ac07df474766f9633088ad660',
    'sourceDirty': 'Approved receipt HTTP plus exact registered REQUEST patterns and independent inventory/unknown/raw-locator rejection; full file hashes captured before execution',
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')),
    'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')), 'branch': 'dev-foundation',
    'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg447_http_selected_v5.sh; six explicit modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report; selected 16 named suites, failIfNoTests=true',
    'exitCode': 0, 'modules': modules, 'tests': 138, 'suites': 16,
    'coverage': coverage, 'staticAnalysis': {'modules': 6, 'findings': 0}, 'javascript': proof,
    'testCases': cases, 'qa': ['QA-048', 'QA-049'], 'ssc': ['SSC-175'],
    'bugs': ['BUG-' + str(n) for n in range(611, 618)] + ['BUG-619', 'BUG-620'],
    'ykt': ['YKT-' + str(n) for n in range(431, 437)] + ['YKT-438'],
    'requestTraceTests': ['REQ004 actual27methods/25unique+CSSJS2', 'req004ReceiptProjectionUsesRegisteredPatternAndNeverRawLocator', 'REQ001..016 existing native terminal/producer/trace'],
    'before': {'id': 'PG447-route-before-v1', 'webTests': 10, 'failures': 2, 'exitCode': 1,
               'logSha256': 'ceab5625a429d72411db1d03c931d8e2e0bf564faac1edfc46fac796521ac02d'},
    'expected': 'UI236 independent QSB4400/320 and QSD268/8608; SS331 SQL postconditions; explicit HTTP302 fixed Location, CSRF403/API0, current owner/tuple and escaped200-codepoint DOM; no DB held during wire',
    'actual': 'All independent SQL/wire/DOM/security/negative/lost-response/100-concurrent assertions passed',
    'logSha256': sha(prefix.with_suffix('.log')),
    'bytePreservation': str(frozen) + ': all six actual classes/test-classes/XML/exec/site/static copied and diff/cmp verified',
    'redaction': 'No JUnit properties/stdout/stderr, cookie/session/context/token/password/key/runtime body/dump/raw log included',
    'limitations': ['Fresh same-source full-six receipt ownership regression required; prior failed full runs remain failed',
                    'V026 signed native migration/Backup/full ordinary Web/Caddy/DONE/CHR/native100/formal pending',
                    'Formal PT-WEB-20260925-24/1964PT/53scope unchanged'],
}
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'id': manifest['id'], 'tests': 138, 'coverageClasses': len(coverage),
                  'manifestSha256': sha(out / 'manifest.json')}))
