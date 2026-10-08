"""Seal changed bootstrap candidate, never merge old mismatched native classes or claim deployed."""
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

T = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def classes(p):
    with zipfile.ZipFile(p) as z:
        return {n: z.read(n) for n in z.namelist() if n.endswith('.class')}


def main(source, version='v2'):
    os.umask(0o077)
    assert re.fullmatch('[0-9a-f]{40}', source)
    assert version in ('v2', 'v3', 'PG598', 'PG598V2')
    run_name = 'pg598-ordinary-process-policy-v2' if version == 'PG598V2' else 'pg598-ordinary-process-policy-v1' if version == 'PG598' else 'pg597-public-agent-driver-' + version
    run = W / run_name
    expected_tests = 26 if version == 'v2' else 29 if version in ('PG598', 'PG598V2') else 27
    assert (run / 'source').read_text().strip() == source and (run / 'exit').read_bytes() == b'0\n'
    entries = [line.split('  ', 1) for line in (run / 'source-files.sha256').read_text().splitlines()]
    objects = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=T,
                                     input=''.join(source + ':' + n + '\n' for _, n in entries).encode())
    offset = 0
    for expected, name in entries:
        end = objects.index(b'\n', offset)
        header = objects[offset:end].split()
        assert len(header) == 3 and header[1] == b'blob'
        size = int(header[2])
        offset = end + 1
        assert hashlib.sha256(objects[offset:offset + size]).hexdigest() == expected
        assert objects[offset + size:offset + size + 1] == b'\n'
        offset += size + 1
    assert offset == len(objects)
    log = (run / 'build.private.log').read_text()
    assert log.count('BUILD SUCCESS') == 1 and 'BUILD FAILURE' not in log
    start = datetime.datetime.fromisoformat((run / 'started').read_text().strip()).timestamp()
    end = datetime.datetime.fromisoformat((run / 'completed').read_text().strip()).timestamp()
    tests = {}
    hashes = {}
    for cls, count in (('FixedNativeCoverageCheckpointTest', 10 if version == 'v2' else 11), ('FixedNativeCoverageProfileTest', 5),
                       ('NativeCoveragePrivateFileTest', 7 if version in ('PG598', 'PG598V2') else 5), ('FixedNativeCoverageStopHoldTest', 6)):
        name = 'TEST-dev.codex.schubert.nk.bootstrap.' + cls + '.xml'
        p = run / name
        current = T / 'src/schubert-nk-bootstrap/target/surefire-reports' / name
        assert sha(p) == sha(current) and start <= current.stat().st_mtime <= end + 1
        root = ET.parse(p).getroot()
        assert int(root.get('tests')) == count and len(root.findall('testcase')) == count
        assert all(int(root.get(k, '0')) == 0 for k in ('failures', 'errors', 'skipped'))
        assert all(not any(c.find(k) is not None for k in ('failure', 'error', 'skipped', 'flakyFailure',
                                                         'flakyError', 'rerunFailure', 'rerunError'))
                   for c in root.findall('testcase'))
        tests[cls] = count
        hashes[name] = sha(p)
    assert sum(tests.values()) == expected_tests
    old = W / 'pg596-fixture-retained-six-host-v1'
    assert sha(old / 'manifest.safe.json') == 'a91fd3f455aa79b64f32a971b9a4757ca62b58d31e93c3627c394f5a703570f1'
    before = classes(old / 'bootstrap/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar')
    jar = run / 'schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar'
    after = classes(jar)
    assert after == classes(T / 'src/schubert-nk-bootstrap/target' / jar.name)
    prefix = 'dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint'
    added = sorted(set(after) - set(before))
    changed = sorted(n for n in set(before) & set(after) if before[n] != after[n])
    assert not set(before) - set(after)
    assert added == sorted(prefix + '$PublicAgent$' + n + '.class' for n in ('Classes', 'Sources', 'Invocation'))
    expected_changes = [prefix + '.class', prefix + '$PublicAgent.class']
    if version in ('PG598', 'PG598V2'):
        expected_changes.append('dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class')
    assert changed == sorted(expected_changes)
    unchanged = 0
    for m in ('protocol', 'storage', 'api', 'web', 'batch'):
        name = 'schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar'
        a = classes(old / m / name)
        assert a == classes(T / 'src' / ('schubert-nk-' + m) / 'target' / name)
        unchanged += len(a)
    assert unchanged + len(before) == 1600 and unchanged + len(after) == 1603
    assert not ET.parse(run / 'spotbugsXml.xml').getroot().findall('.//BugInstance')
    root = ET.parse(run / 'jacoco.xml').getroot()
    selected = {}
    for c in root.findall('./package/class'):
        if c.get('name') in (prefix, prefix + '$PublicAgent', 'dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile'):
            selected[c.get('name')] = {x.get('type'): {'missed': int(x.get('missed')), 'covered': int(x.get('covered'))}
                                      for x in c.findall('counter')}
    assert selected[prefix + '$PublicAgent']['BRANCH'] == {'missed': 0, 'covered': 22}
    result = {'actualExit': 0, 'run': run_name, 'operatorSource': source,
              'candidateProductionSource': source, 'installedVmProductionSource': '969d8ded10c0bf5841d9e3a5c531e922caf4a24a',
              'sourceQualification': 'UNACCEPTED_PRODUCTION_CANDIDATE_NOT_DEPLOYED',
              'tests': tests, 'selectedTests': expected_tests, 'newTestCases': 4 if version == 'v2' else 7 if version in ('PG598', 'PG598V2') else 5, 'FESFlakyNotRun': 0,
              'outsideSelectedNotRunCredit0': True, 'staticModules': 1, 'staticIssues': 0,
              'beforeMainClasses': 1600, 'candidateMainClasses': 1603, 'changedClasses': changed,
              'addedAbstractInterfaces': added, 'removedClasses': [], 'interfaceExclusionConfigured': False,
              'selectedCounters': selected, 'allFourCounters100': False,
              'oldNativeStreamsNotJoinedToChangedClass': True, 'vmDeploymentActions': 0,
              'started': (run / 'started').read_text().strip(), 'completed': (run / 'completed').read_text().strip(),
              'elapsedSeconds': end - start, 'xmlHashes': hashes, 'execSha256': sha(run / 'bootstrap.exec'),
              'jarSha256': sha(jar), 'staticSha256': sha(run / 'spotbugsXml.xml'),
              'coverageSha256': sha(run / 'jacoco.xml'), 'sourceFilesSha256': sha(run / 'source-files.sha256'),
              'logSha256': sha(run / 'build.private.log'), 'collectorSha256': sha(pathlib.Path(__file__)),
              'formalAccepted': False, 'wholeWbsAccepted': False, 'rawExported': False}
    with (run / 'manifest.safe.json').open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps({'actualExit': 0, 'selectedTests': expected_tests, 'publicAgentBranch': '22/22',
                      'candidateMain': 1603, 'changedClasses': len(changed), 'staticIssues': 0,
                      'manifestSha256': sha(run / 'manifest.safe.json'), 'formalAccepted': False}))


if __name__ == '__main__':
    assert len(sys.argv) in (2, 3)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else 'v2')
