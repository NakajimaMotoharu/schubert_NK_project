"""Source-frozen PG389 full-six sanitized capture; not formal/native acceptance."""
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
assert not subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--', 'src', 'tools'], cwd=root, text=True).strip()
log = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg389-six.log').read_text()
assert 'BUILD SUCCESS' in log and log.count('BugInstance size is 0') == 6
assert 'do not match with execution data' not in log
out = root / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG389-inspector-owner'
assert not out.exists()
modules, coverage = {}, {}
for name, expected in [('protocol', 80), ('storage', 153), ('bootstrap', 191), ('api', 760), ('web', 565), ('batch', 832)]:
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
    'id': 'PG389-inspector-owner', 'formal': False, 'sourceCommit': source, 'branch': 'dev-foundation',
    'environment': 'Linux/JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
    'command': 'explicit six modules: clean test spotbugs:check jacoco:report jar:jar org.apache.maven.plugins:maven-dependency-plugin:3.9.0:copy-dependencies org.apache.maven.plugins:maven-dependency-plugin:3.9.0:list -DincludeScope=runtime -o',
    'exitCode': 0, 'modules': modules, 'tests': sum(m['tests'] for m in modules.values()), 'coverage': coverage,
    'testIds': ['PT-DB-INBOX-269..271', 'PT-OPS-COWNER001..004', 'PT-OPS-CINSPECT001..004', 'ROOTCTX010', 'MBUDGET003'],
    'bugs': ['BUG-356', 'BUG-357', 'BUG-358', 'BUG-359', 'BUG-360'], 'ssc': ['SSC-119'], 'ykt': ['YKT-282'],
    'limitations': ['native Cleanup assembler/root owner issuance not connected', 'VM still PG387', 'native common deadline/Inspector/100% coverage not accepted', 'formal PT-WEB-20260925-24 unchanged'],
    'priorFailures': ['initial API F1/E1 timeout representation BUG357', 'API12 pass/static1 resource expression BUG358', 'native non-manager fixture old credential-stage oracle F1 BUG359', 'Batch compile nullable leaf BUG360', 'new constructor TDD ambiguity before factory selection', 'first six command unqualified dependency prefix selected uncached3.7.0; stopped at protocol, nonaccepted'],
    'redaction': 'JUnit properties/stdout/stderr/provider diagnostics omitted; no credentials/session/token/password/key/dump',
}
manifest['finishedAt'] = next(line.split('Finished at: ', 1)[1] for line in log.splitlines() if 'Finished at: ' in line)
manifest['files'] = [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()]
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'source': source, 'tests': manifest['tests'], 'coverage': coverage, 'manifestSha256': hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest()}, ensure_ascii=False))
