"""Independent new candidate14PT and literal core four-counter closure; not native."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from pg707_selected import classes, HOST, MODULES

W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
D = W / 'pg711-expiry-core-v1'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    run = json.loads((D / 'run.safe.json').read_bytes())
    assert run['actualExit'] == 0 and run['candidateSource'] == 'cc24647741f55266ea763e1b8dbc97f7a3c55c2e'
    assert (D / 'exit').read_bytes() == b'0\n'
    for name, digest in run['files'].items(): assert sha(D / name) == digest
    expected = {'ExpiryResultContractTest': 11, 'CleanupExpiryExecutionTest': 1, 'ExpiryOwnerTest': 2}
    paths = list((D / 'batch').glob('TEST-*.xml'))
    assert {p.name.rsplit('.', 1)[0].rsplit('.', 1)[-1] for p in paths} == set(expected)
    names = []
    for p in paths:
        root = ET.parse(p).getroot(); name = root.get('name').rsplit('.', 1)[-1]
        assert root.get('tests') == str(expected[name])
        assert all(root.get(k) == '0' for k in ('failures', 'errors', 'skipped'))
        cases = root.findall('testcase'); assert len(cases) == expected[name]
        assert len({c.get('name') for c in cases}) == len(cases)
        for case in cases:
            assert not any(case.findall(k) for k in ('failure', 'error', 'skipped', 'flakyFailure', 'rerunFailure', 'rerunError'))
            names.append(case.get('name'))
    assert len(names) == 14 and len([n for n in names if n.startswith('exp711')]) == 11
    bugs = ET.parse(D / 'batch/spotbugsXml.xml').getroot()
    assert not bugs.findall('BugInstance') and not bugs.findall('.//Error')
    jar = D / 'batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    old = classes(HOST / 'batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar'); new = classes(jar)
    changed = sorted(k for k in old if old[k] != new[k]); added = sorted(new.keys() - old.keys())
    assert changed == ['dev/codex/schubert/nk/batch/file/CleanupExpiryExecution.class']
    assert added == ['dev/codex/schubert/nk/batch/file/CleanupExpiryExecution$1.class', 'dev/codex/schubert/nk/batch/file/CleanupExpiryExecution$ExpiryWork.class']
    assert not old.keys() - new.keys()
    target = W / 'pg712-expiry-core-qualification-v1'; target.mkdir(mode=0o700)
    repo = Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp = [str(W / 'pg562-current-native-gap-v1/classes'), str(W / 'pg571-current-ten-native-v2/classes')]
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar', 'org/jacoco/org.jacoco.report/0.8.15/*.jar',
                    'org/ow2/asm/asm/9.10.1/*.jar', 'org/ow2/asm/asm-tree/9.10.1/*.jar', 'org/ow2/asm/asm-commons/9.10.1/*.jar'):
        found = list(repo.glob(pattern)); assert len(found) == 1; cp.append(str(found[0]))
    java = '/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java'
    xml = target / 'batch.xml'; data = D / 'batch/jacoco.exec'
    result = subprocess.run([java, '-cp', ':'.join(cp), 'NativeCoverageXml471', str(jar), str(xml), str(data)], capture_output=True, timeout=45)
    assert result.returncode == 0 and not result.stderr
    root = ET.parse(xml).getroot()
    node = next(c for c in root.findall('.//class') if c.get('name') == 'dev/codex/schubert/nk/batch/file/CleanupExpiryExecution')
    method = next(m for m in node.findall('method') if m.get('name') == 'executeAuthenticated')
    counters = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in method.findall('counter')}
    assert all(counters[k]['missed'] == 0 and counters[k]['covered'] > 0 for k in ('LINE', 'METHOD', 'BRANCH'))
    measured = subprocess.run([java, '-cp', ':'.join(cp), 'NativeCoverage', str(jar), str(data)], capture_output=True, timeout=45)
    assert measured.returncode == 0 and not measured.stderr
    overall = json.loads(measured.stdout); assert overall['classByteMismatch'] == 0
    source_path = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/CleanupExpiryExecution.java'
    source_bytes = subprocess.check_output(['git', 'show', run['candidateSource'] + ':' + source_path])
    main_count = sum(len(classes(HOST / m / ('schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar'))) for m in MODULES) + 2
    assert main_count == 1614
    safe = {'actualExit': 0, 'source': run['candidateSource'], 'run': D.name, 'selectedTests': 14, 'suites': 3,
            'newCases': 11, 'FESFlakyNotRun': 0, 'staticBatchIssues': 0, 'coreCounters': counters,
            'changedMainClasses': changed, 'addedInnerClasses': added, 'candidateMainClasses': main_count,
            'xmlSha256': sha(xml), 'jarSha256': sha(jar), 'execSha256': sha(data), 'moduleCounters': overall,
            'productionSourcePath': source_path, 'sourceSha256': hashlib.sha256(source_bytes).hexdigest(),
            'runReceiptSha256': sha(D / 'run.safe.json'), 'nativeAccepted': False,
            'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'formalAccepted': False, 'rawExported': False}
    with (target / 'manifest.safe.json').open('x') as output: json.dump(safe, output, sort_keys=True)
    print(json.dumps({'actualExit': 0, 'PT': 14, 'coreCounters': counters, 'candidateMainClasses': main_count,
                      'manifestSha256': sha(target / 'manifest.safe.json'), 'formalAccepted': False}))


if __name__ == '__main__': main()
