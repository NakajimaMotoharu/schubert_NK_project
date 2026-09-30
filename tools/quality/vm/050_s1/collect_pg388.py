"""Frozen PG388 full-six capture; no native or formal acceptance is inferred."""
import hashlib
import json
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
source = subprocess.check_output(['git', 'rev-parse', sys.argv[1]], cwd=root, text=True).strip()
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip() == source
subprocess.run(['git', 'diff', '--exit-code', source, '--', 'src', 'tools', 'pom.xml'], cwd=root, check=True)
log = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg388-six.log').read_text()
assert 'BUILD SUCCESS' in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
out = root / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG388-cleanup-dependencies'
assert not out.exists()
modules, coverage = {}, {}
for name, expected in [('protocol', 80), ('storage', 150), ('bootstrap', 182), ('api', 756), ('web', 565), ('batch', 827)]:
    target = root / f'src/schubert-nk-{name}/target'
    count = 0
    reports = sorted((target / 'surefire-reports').glob('TEST-*.xml'))
    for report in reports:
        suite = ET.parse(report).getroot()
        assert all(int(suite.get(k)) == 0 for k in ('failures', 'errors', 'skipped'))
        assert len(suite.findall('testcase')) == int(suite.get('tests'))
        safe = ET.Element('testsuite', {k: suite.get(k) for k in ('name', 'tests', 'failures', 'errors', 'skipped', 'time')})
        for case in suite.findall('testcase'):
            assert all(child.tag in ('system-out', 'system-err') for child in case)
            ET.SubElement(safe, 'testcase', {k: case.get(k) for k in ('name', 'classname', 'time')})
        path = out / 'junit' / name / report.name
        path.parent.mkdir(parents=True, exist_ok=True)
        ET.indent(safe)
        ET.ElementTree(safe).write(path, encoding='utf-8', xml_declaration=True)
        count += int(suite.get('tests'))
    assert count == expected, (name, count, expected)
    modules[name] = {'tests': count, 'suites': len(reports), 'failures': 0, 'errors': 0, 'skipped': 0}
    coverage[name] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in ET.parse(target / 'site/jacoco/jacoco.xml').getroot().findall('counter')}
    bugs = ET.parse(target / 'spotbugsXml.xml').getroot()
    assert not bugs.findall('BugInstance') and int(bugs.find('Errors').get('errors')) == 0
manifest = {
    'id': 'PG388-cleanup-dependencies', 'formal': False, 'sourceCommit': source, 'branch': 'dev-foundation',
    'environment': 'Linux/JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'explicit six modules: clean test spotbugs:check jacoco:report jar:jar dependency:copy-dependencies dependency:list -o',
    'exitCode': 0, 'modules': modules, 'tests': sum(m['tests'] for m in modules.values()), 'coverage': coverage,
    'testIds': ['PT-OPS-EREQ005', 'PT-OPS-ESKIP001', 'PT-OPS-TRANSFER001..003', 'PT-OPS-CCYCLE001..002', 'MDB010..012'],
    'bugs': ['BUG-351', 'BUG-352', 'BUG-353', 'BUG-354', 'BUG-355'], 'ssc': ['SSC-117', 'SSC-118'],
    'limitations': ['host dependency regression only', 'Cleanup Main/Inspector/native/Expiry/issuer not connected', 'CCYCLE003..006 and 100% coverage not accepted', 'formal PT-WEB-20260925-24 unchanged'],
    'priorFailures': ['selected Batch119 F1 (duplicate recheck event)', 'selected148 PT pass/static1 useless suppression (BUG355)', 'ESKIP initial exception oracle failure (BUG352)', 'selected58 pass/static4 null unbox warnings (BUG353)'],
    'redaction': 'JUnit properties/stdout/stderr/provider diagnostics omitted; no credentials/session/token/password/key/dump',
}
manifest['finishedAt'] = next(line.split('Finished at: ', 1)[1] for line in log.splitlines() if 'Finished at: ' in line)
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'source': source, 'tests': manifest['tests'], 'coverage': coverage, 'manifestSha256': hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest()}, ensure_ascii=False))
