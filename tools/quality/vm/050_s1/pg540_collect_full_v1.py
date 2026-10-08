"""Post-run read-only sealing helper; independent hashes, no VM/native/formal acceptance."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as E
import zipfile

os.umask(0o077)
T = Path('/home/mini/codex/project1/work/pgpt-foundation')
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
RUN = 'PG540-completion-admission-six-v1'
stem = W / RUN.lower()
def value(s):
    return Path(str(stem) + s).read_text().strip()
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
source = value('.source')
assert source == '969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
assert value('.exit') == '0'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip() == source
assert subprocess.run(['sha256sum', '--check', '--status', str(stem) + '.source-files.sha256'], cwd=T).returncode == 0
log = value('.log')
assert 'BUILD SUCCESS' in log and log.count('BugInstance size is 0') == 6
assert log.count('No errors/warnings found') == 6
start = datetime.datetime.fromisoformat(value('.started')).timestamp()
end = datetime.datetime.fromisoformat(value('.completed')).timestamp()
root = W / 'pg540-six-host-v1'
assert not root.exists()
root.mkdir(mode=0o700)
modules = []
changed = []
classes = 0
for name in ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']:
    origin = T / ('src/schubert-nk-' + name + '/target')
    frozen = root / name
    shutil.copytree(origin, frozen)
    frozen.chmod(0o700)
    for p in frozen.rglob('*'):
        p.chmod(0o700 if p.is_dir() else 0o600)
        if p.is_file():
            assert digest(p) == digest(origin / p.relative_to(frozen))
    suites = list((frozen / 'surefire-reports').glob('TEST-*.xml'))
    assert suites
    rows = []
    for p in suites:
        assert start <= p.stat().st_mtime <= end + 1
        suite = E.parse(p).getroot()
        tests = int(suite.attrib['tests'])
        assert tests > 0
        assert all(int(suite.get(k, '0')) == 0 for k in ['failures', 'errors', 'skipped'])
        cases = suite.findall('testcase')
        assert len(cases) == tests
        assert all(not any(c.find(k) is not None for k in ['failure', 'error', 'skipped']) for c in cases)
        rows.append({'class': suite.attrib['name'], 'tests': tests, 'xmlSha256': digest(p)})
    xml = frozen / 'site/jacoco/jacoco.xml'
    assert start <= xml.stat().st_mtime <= end + 1
    doc = E.parse(xml).getroot()
    assert not E.parse(frozen / 'spotbugsXml.xml').getroot().findall('.//BugInstance')
    jar = frozen / ('schubert-nk-' + name + '-0.1.0-SNAPSHOT.jar')
    prior = W / 'pg495-host' / name / jar.name
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(prior) as b:
        aa = [n for n in a.namelist() if n.endswith('.class')]
        bb = [n for n in b.namelist() if n.endswith('.class')]
        assert len(aa) == len(set(aa)) and len(bb) == len(set(bb)) and set(aa) == set(bb)
        classes += len(aa)
        changed.extend(name + ':' + n for n in aa if a.read(n) != b.read(n))
    modules.append({'module': name, 'tests': sum(r['tests'] for r in rows), 'suiteCount': len(rows),
                    'FES': 0, 'XML': rows, 'coverageXmlSha256': digest(xml), 'projectJarSha256': digest(jar),
                    'spotbugsXmlSha256': digest(frozen / 'spotbugsXml.xml'),
                    'counters': {c.attrib['type']: {'missed': int(c.attrib['missed']), 'covered': int(c.attrib['covered'])}
                                 for c in doc.findall('counter')}})
assert changed == ['batch:dev/codex/schubert/nk/batch/file/MorningCompletionEvidence.class']
batch = E.parse(root / 'batch/site/jacoco/jacoco.xml').getroot()
completion = next(c for c in batch.findall('./package/class')
                  if c.attrib['name'] == 'dev/codex/schubert/nk/batch/file/MorningCompletionEvidence')
counters = {c.attrib['type']: {'missed': int(c.attrib['missed']), 'covered': int(c.attrib['covered'])}
            for c in completion.findall('counter')}
assert all(counters[k]['missed'] == 0 and counters[k]['covered'] > 0 for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH'])
summary = {'run': RUN, 'productionSource': source, 'source': source, 'branch': 'dev-foundation',
           'deployedVmSource': 'a2e98ce9e96c42425921e3686e8ae7a94bff9e6c', 'runRecordStem': str(stem),
           'actualExit': 0, 'FES': 0, 'staticModules': 6, 'staticIssues': 0,
           'sourceUnchanged': True, 'sourceBeforeAfterUnchanged': True, 'formatNullAwayWerrorPassed': True,
           'startedJST': value('.started'), 'completedJST': value('.completed'),
           'elapsedSeconds': end - start, 'command': 'bash tools/quality/vm/050_s1/pg540_full_v1.sh ' + source,
           'tests': sum(m['tests'] for m in modules), 'suiteCount': sum(m['suiteCount'] for m in modules),
           'modules': modules, 'coverageRoot': str(root), 'comparedClasses': classes,
           'changedProductionClassesFromPG495': changed, 'morningCompletionEvidenceCounters': counters,
           'ssc': ['SSC-218'], 'testIds': ['PT-PARENT540001', 'PT-PARENT540002', 'PT-PARENT540003', 'PT-PARENT540004'],
           'logSha256': digest(Path(str(stem) + '.log')), 'sourceFilesSha256': digest(Path(str(stem) + '.source-files.sha256')),
           'collectorSourceSha256': digest(Path(__file__)), 'collectorMode': 'Post-run independent helper SHA, not part of frozen Maven source',
           'globalCoverage100': False, 'nativeSameSourceAccepted': False, 'allChrPassed': False,
           'formalPass': False, 'ITSTAccepted': False, 'rawLogsInGit': False,
           'environment': {'os': 'Linux 7.0.0-38-generic', 'jdk': '25.0.4', 'maven': '3.9.12',
                           'node': '24.19.0', 'jacoco': '0.8.15', 'spotbugsPlugin': '4.10.4.0'}}
assert summary['tests'] > 3411 and summary['suiteCount'] >= 510
out = W / 'pg540-six-host-v1.safe.json'
with out.open('x') as f:
    json.dump(summary, f, sort_keys=True, indent=2)
    f.write('\n')
print(json.dumps({'run': RUN, 'source': source, 'tests': summary['tests'], 'suites': summary['suiteCount'],
                  'staticModules': 6, 'changedClasses': changed, 'completionCounters': counters, 'safeSha256': digest(out)}))
