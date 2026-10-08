"""Independent fixed PG676v3 XML/source/class-byte qualification; no VM operation."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

T = Path('/home/mini/codex/project1/work/pgpt-foundation')
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
RUN = W/'pg676-inspector-owner-component-v3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classes(path):
    with zipfile.ZipFile(path) as archive:
        return {n: archive.read(n) for n in archive.namelist() if n.endswith('.class')}


def main():
    os.umask(0o077)
    source = (RUN/'source').read_text().strip()
    assert source.startswith('f76c7ec09') and (RUN/'exit').read_bytes() == b'0\n'
    for line in (RUN/'source-files.sha256').read_text().splitlines():
        digest, path = line.split('  ', 1)
        assert hashlib.sha256(subprocess.check_output(['git', 'show', source+':'+path], cwd=T)).hexdigest() == digest
    begin = datetime.datetime.fromisoformat((RUN/'started').read_text().strip()).timestamp()
    end = datetime.datetime.fromisoformat((RUN/'completed').read_text().strip()).timestamp()
    counts = {'bootstrap.BootstrapEntryBoundaryTest': 5, 'bootstrap.BootstrapAdminMainTest': 4,
              'maintenance.InspectorEntryBoundaryTest': 4, 'maintenance.InspectorLauncherTest': 8,
              'file.InspectorApplicationTest': 9, 'maintenance.InspectorProcessTest': 14,
              'file.InspectorOwnerContractTest': 6, 'maintenance.InspectionRunExecutorTest': 9}
    paths = sorted((RUN/'surefire-reports').glob('TEST-*.xml'))
    assert {p.name for p in paths} == {'TEST-dev.codex.schubert.nk.api.'+name+'.xml' for name in counts}
    for p in paths:
        root = ET.parse(p).getroot()
        name = root.get('name').removeprefix('dev.codex.schubert.nk.api.')
        assert root.get('tests') == str(counts[name])
        assert all(root.get(k) == '0' for k in ('failures', 'errors', 'skipped'))
        cases = root.findall('testcase')
        assert len(cases) == counts[name] and len({c.get('name') for c in cases}) == len(cases)
        assert not any(c.findall(k) for c in cases for k in ('failure', 'error', 'skipped', 'flakyFailure', 'rerunFailure', 'rerunError'))
        assert begin-1 <= p.stat().st_mtime <= end+2
    root = ET.parse(RUN/'jacoco.xml').getroot()
    sessions = root.findall('sessioninfo')
    assert len(sessions) == 1
    assert all(begin*1000-1000 <= int(s.get('start')) <= int(s.get('dump')) <= end*1000+1000 for s in sessions)
    bugs = ET.parse(RUN/'spotbugsXml.xml').getroot()
    assert not bugs.findall('BugInstance') and not bugs.findall('.//Error')
    nodes = [c for c in root.findall('.//class') if c.get('name') == 'dev/codex/schubert/nk/api/file/InspectorApplication']
    assert len(nodes) == 1
    counters = {}
    for name in ('validateOwner', 'executeGuarded', 'lambda$executeGuarded$0'):
        methods = [m for m in nodes[0].findall('method') if m.get('name') == name]
        assert len(methods) == 1
        counters[name] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in methods[0].findall('counter')}
        assert all(counters[name][k]['missed'] == 0 and counters[name][k]['covered'] > 0 for k in ('LINE', 'METHOD', 'BRANCH'))
    a = classes(W/'pg672-entry-six-host-v2/api/schubert-nk-api-0.1.0-SNAPSHOT.jar')
    b = classes(RUN/'schubert-nk-api-0.1.0-SNAPSHOT.jar')
    added = sorted(b.keys()-a.keys())
    changed = sorted(n for n in a.keys() & b.keys() if a[n] != b[n])
    assert not a.keys()-b.keys()
    assert added == ['dev/codex/schubert/nk/api/file/InspectorApplication$InspectorProbe.class', 'dev/codex/schubert/nk/api/file/InspectorApplication$OwnedOperation.class']
    assert changed == ['dev/codex/schubert/nk/api/file/InspectorApplication.class']
    log = (RUN/'build.private.log').read_text()
    assert log.count('BUILD SUCCESS') == 1 and 'BUILD FAILURE' not in log and 'qualifiedNullableFixtures' in log
    safe = {'actualExit': 0, 'run': 'PG676-inspector-owner-component-v3', 'source': source,
            'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip(),
            'selectedTests': 59, 'suites': 8, 'newCases': 6, 'FESFlakyNotRun': 0, 'staticApiIssues': 0,
            'helperCounters': counters, 'elapsedSeconds': end-begin,
            'hashes': {p.name: sha(p) for p in [RUN/'source-files.sha256', RUN/'api.exec', RUN/'jacoco.xml', RUN/'spotbugsXml.xml', RUN/'schubert-nk-api-0.1.0-SNAPSHOT.jar', *paths]},
            'sessionIdSha256': hashlib.sha256(sessions[0].get('id').encode()).hexdigest(),
            'changedMainClasses': changed, 'addedAbstractInterfaces': added,
            'actualUnitAdmission': False, 'candidateDeployed': False, 'coverage100': False, 'formalAccepted': False}
    with (RUN/'manifest.safe.json').open('x') as stream:
        json.dump(safe, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'actualExit': 0, 'selectedTests': 59, 'suites': 8, 'staticIssues': 0,
                      'threeHelpers100': True, 'manifestSha256': sha(RUN/'manifest.safe.json'), 'formalAccepted': False}))


if __name__ == '__main__':
    main()
