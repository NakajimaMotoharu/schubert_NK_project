"""PG446 selected regression: sanitized counts and fixed-source artifact hashes only."""
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess
import xml.etree.ElementTree as ET

root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
work = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
target = root / 'evidence/01_PT/016_NK-WEB-002/evidence/provisional/PG446-token-selected-v3'
frozen = work / 'pg446-token-selected-v3-frozen-v2'
assert not target.exists() and not frozen.exists()
assert (work / 'pg446-token-selected-v3.exit').read_text().strip() == '0'
log = (work / 'pg446-token-selected-v3.log').read_bytes()
assert b'BUILD SUCCESS' in log
modules = ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']
results = []
for module in modules:
    source = root / f'src/schubert-nk-{module}/target'
    tests = []
    for xml in sorted((source / 'surefire-reports').glob('TEST-*.xml')):
        suite = ET.parse(xml).getroot()
        assert all(int(suite.get(k, '0')) == 0 for k in ['failures', 'errors', 'skipped'])
        assert int(suite.get('tests')) > 0
        for case in suite.findall('testcase'):
            assert all(child.tag in ['system-out', 'system-err'] for child in case), 'Reject failed, skipped or unknown result elements'
            tests.append({'class': case.get('classname'), 'method': case.get('name')})
        assert len(suite.findall('testcase')) == int(suite.get('tests'))
    assert tests
    static = ET.parse(source / 'spotbugsXml.xml').getroot()
    assert not static.findall('.//BugInstance')
    results.append({'module': module, 'tests': tests, 'count': len(tests), 'staticBugs': 0})
    dest = frozen / module
    dest.mkdir(parents=True)
    for name in ['classes', 'test-classes', 'surefire-reports']:
        shutil.copytree(source / name, dest / name)
    for name in ['jacoco.exec', 'site/jacoco/jacoco.xml', 'spotbugsXml.xml']:
        path = dest / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, path)

coverage = []
report = ET.parse(root / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml').getroot()
for cls in report.findall('.//class'):
    if cls.get('name').rsplit('/', 1)[-1] in ['SessionOperationToken', 'SessionAttributeCodec']:
        counters = {c.get('type'): {'covered': int(c.get('covered')), 'missed': int(c.get('missed'))}
                    for c in cls.findall('counter')}
        coverage.append({'class': cls.get('name'), 'counters': counters})
assert len(coverage) == 2
files = []
for base in ['src', 'tools/quality/060_collect_pg446_token_selected.py']:
    directory = root / base
    candidates = directory.rglob('*') if directory.is_dir() else [directory]
    for path in candidates:
        if path.is_file() and 'target' not in path.parts and '.git' not in path.parts:
            files.append({'path': str(path.relative_to(root)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
record = {'id': target.name, 'formal': False, 'fullRegression': False,
          'timeUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
          'sourceDirty': True, 'branch': 'dev-foundation', 'command': 'WorkPG379/pg446_token_selected_v3.sh',
          'actualExit': 0, 'environment': 'Linux/JDK25.0.4/Maven3.9.12/Node24.19.0/offline M2',
          'tests': sum(r['count'] for r in results), 'modules': results, 'coverage': coverage,
          'sourceFiles': sorted(files, key=lambda f: f['path']), 'logSha256': hashlib.sha256(log).hexdigest(),
          'failedRuns': [{'run': f'v{i}', 'actualExit': 1, 'acceptedTests': 0,
                          'logSha256': hashlib.sha256((work / f'pg446-token-selected-v{i}.log').read_bytes()).hexdigest()}
                         for i in [1, 2]],
          'qa': ['QA-049'], 'bugs': ['BUG-600', 'BUG-601'], 'specification': '016/073',
          'limits': ['lifecycle issue/require/complete not implemented or tested in this source',
                     'native/Web full assembly and formal 451 recognition not accepted',
                     'strict failIfNoTests=true retained; selected success is not full-module suite coverage'],
          'redaction': 'No raw XML properties, logs, session/cookie/token/key/DB/private archive copied to Git'}
target.mkdir(parents=True)
manifest = target / 'manifest.json'
manifest.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'actualExit': 0, 'tests': record['tests'], 'coverage': coverage,
                  'manifestSha256': hashlib.sha256(manifest.read_bytes()).hexdigest(), 'formal': False}))
