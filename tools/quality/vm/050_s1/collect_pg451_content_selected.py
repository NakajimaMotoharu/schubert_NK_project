"""Actual frozen content read selection; no full/native/formal acceptance."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/home/mini/codex/project1/work/pgpt-foundation')
work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
prefix = work / 'pg451-content-selected-v2'
frozen = work / 'pg451-content-selected-v2-frozen'
out = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG451-content-selected-v2'
source = '5c933eacc394bec8ac85e69294824a52944bdf4f'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not out.exists() and prefix.with_suffix('.exit').read_text().strip() == '0'
assert prefix.with_suffix('.source').read_text().strip() == source
log = prefix.with_suffix('.log').read_text()
assert 'BUILD SUCCESS' in log and 'BUILD FAILURE' not in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
modules, coverage = {}, {}
for module, expected in zip(('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'), (5, 7, 10, 71, 187, 43), strict=True):
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
        if cls.findall('counter') and (name in ('ContentDetailController', 'ContentDetailMvcConfiguration', 'AnimationWatchViewModel', 'MusicTrackViewModel', 'WebMvcConfiguration', 'LargeResultReader', 'FileIntegrityException', 'ScenarioDetailViewModel', 'MediaResponseDecoder') or name.startswith('WebRequestTrace')):
            coverage[name] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in cls.findall('counter')}
assert len(coverage) == 11 and all(c['missed'] == 0 for value in coverage.values() for c in value.values())
assert sum(m['tests'] for m in modules.values()) == 323 and sum(m['suites'] for m in modules.values()) == 36
before = []
for tag, stage, tests, failures, errors in (
    ('content-before-v1', 'Web testCompile; Web PT/Batch/Web static not run', 93, 0, 0),
    ('content-selected-v1', 'Web PT; Batch/Web static not run', 280, 3, 0),
):
    p = work / ('pg451-' + tag)
    assert p.with_suffix('.exit').read_text().strip() == '1'
    before.append({'id': 'PG451-' + tag, 'accepted': False, 'exitCode': 1,
        'stage': stage, 'executedTests': tests, 'failures': failures, 'errors': errors,
        'logSha256': sha(p.with_suffix('.log')),
        'sourceFilesSha256': sha(p.with_suffix('.source-files.sha256')),
        'bytePreservation': str(work / ('pg451-' + tag + '-frozen'))})
manifest = {
    'id': 'PG451-content-selected-v2', 'sourceHead': source, 'sourceDirty': 'PG-D365 fixed content read mappings, borrowed file reader, display maps/templates, literal wire/DOM/security tests before PT-CONTENT010 and collector addition',
    'formal': False, 'fullRun': False, 'native': False, 'branch': 'dev-foundation',
    'startedAt': prefix.with_suffix('.started').read_text().strip(), 'finishedAt': prefix.with_suffix('.completed').read_text().strip(),
    'environment': 'Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'bash WorkPG379/pg451_selected.sh content-selected-v2 ' + source + ' exact36Testclasses; six modules clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report',
    'testClasses': sorted({c.get('classname') for m in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch') for p in (frozen / m / 'surefire-reports').glob('TEST-*.xml') for c in E.parse(p).getroot().findall('testcase')}),
    'exitCode': 0, 'tests': 323, 'suites': 36, 'modules': modules, 'coverage': coverage, 'coverageExclusions': [], 'staticAnalysis': {'modules': 6, 'findings': 0},
    'sourceFilesSha256': sha(prefix.with_suffix('.source-files.sha256')), 'sourceDiffSha256': sha(prefix.with_suffix('.source-diff')), 'logSha256': sha(prefix.with_suffix('.log')), 'bytePreservation': str(frozen),
    'testIds': ['PT-CONTENT%03d' % n for n in range(1, 10)],
    'qa': [], 'ssc': ['SSC-176'], 'bugs': ['BUG-635', 'BUG-636', 'BUG-637'], 'ykt': ['YKT-450'],
    'expected': 'SCN INLINE0/1/200 and held FILE1/201/10000; valid VIDEO prefix and invalid prefix503; literal back links and escaped title; music stored4pairs/5players/3missing sides; zero music404; fixed error codes/null/immutable maps; anonymous302, authenticated GETHEAD200/POST405, genuine0102terminal, 100 independent reads',
    'actual': '323 PT/36 suites/FES0, static6zero; eleven affected classes all four coverage counters missed0; closed MVC/DOM/file/security and independent wire assertions passed',
    'before': before, 'redaction': 'No JUnit properties/stdout/stderr, provider messages, raw logs, real credentials/cookie/context/token/key/dump',
    'limitations': ['Selected host MVC/security/held file/PostgreSQL with independent JMS fixture only; no actual Artemis or native owner proof', 'PT-CONTENT010 and this collector added after frozen selection; fresh same-source full regression required and not yet accepted', 'Formal PT-WEB-20260925-24/1964PT/53scope unchanged'],
}
assert manifest['ssc'] == ['SSC-176'] and manifest['qa'] == [] and manifest['ykt'] == ['YKT-450']
assert manifest['testIds'] == ['PT-CONTENT%03d' % n for n in range(1, 10)]
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': 323, 'coverageClasses': 11, 'manifestSha256': sha(out / 'manifest.json')}))
