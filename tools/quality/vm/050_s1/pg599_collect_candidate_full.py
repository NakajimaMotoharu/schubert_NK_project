"""Fresh six-module candidate only; old byte-mismatched native not imported."""
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


def main(source):
    os.umask(0o077)
    assert re.fullmatch('[0-9a-f]{40}', source)
    run = W / 'pg599-candidate-bootstrap-six-host-v1'
    assert (run / 'source').read_text().strip() == source and (run / 'exit').read_bytes() == b'0\n'
    entries = [l.split('  ', 1) for l in (run / 'source-files.sha256').read_text().splitlines()]
    raw = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=T,
                                  input=''.join(source + ':' + p + '\n' for _, p in entries).encode())
    offset = 0
    for expected, path in entries:
        end = raw.index(b'\n', offset)
        header = raw[offset:end].split()
        assert len(header) == 3 and header[1] == b'blob'
        size = int(header[2]); offset = end + 1
        assert hashlib.sha256(raw[offset:offset + size]).hexdigest() == expected
        assert raw[offset + size:offset + size + 1] == b'\n'
        offset += size + 1
    assert offset == len(raw)
    log = (run / 'build.private.log').read_text()
    assert log.count('BUILD SUCCESS') == 1 and 'BUILD FAILURE' not in log
    start = datetime.datetime.fromisoformat((run / 'started').read_text().strip()).timestamp()
    end = datetime.datetime.fromisoformat((run / 'completed').read_text().strip()).timestamp()
    selected = W / 'pg598-ordinary-process-policy-v2'
    assert sha(selected / 'manifest.safe.json') == '0cf145a124ab72159144eaeae5d9042d77980ab49953c62ddb3ccb9cf2c81257'
    old = W / 'pg596-fixture-retained-six-host-v1'
    assert sha(old / 'manifest.safe.json') == 'a91fd3f455aa79b64f32a971b9a4757ca62b58d31e93c3627c394f5a703570f1'
    results = {}; total_classes = 0; tests = 0; suites = 0
    for module in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'):
        base = run / module; current = T / 'src' / ('schubert-nk-' + module) / 'target'
        name = 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'
        actual = classes(base / name)
        admitted = classes(selected / name if module == 'bootstrap' else old / module / name)
        assert actual == admitted == classes(current / name) and actual
        total_classes += len(actual)
        sums = {k: 0 for k in ('tests', 'failures', 'errors', 'skipped')}; hashes = {}
        reports = sorted((base / 'surefire-reports').glob('TEST-*.xml')); assert reports
        for p in reports:
            original = current / 'surefire-reports' / p.name
            assert sha(p) == sha(original) and start <= original.stat().st_mtime <= end + 1
            root = ET.parse(p).getroot(); cases = root.findall('testcase')
            assert len(cases) == int(root.get('tests')) > 0
            assert all(not any(c.find(k) is not None for k in ('failure', 'error', 'skipped',
                            'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError')) for c in cases)
            for k in sums: sums[k] += int(root.get(k, '0'))
            hashes[p.name] = sha(p)
        assert sum(sums[k] for k in ('failures', 'errors', 'skipped')) == 0
        assert not ET.parse(base / 'spotbugsXml.xml').getroot().findall('.//BugInstance')
        assert sha(base / 'jacoco.xml') == sha(current / 'site/jacoco/jacoco.xml')
        root = ET.parse(base / 'jacoco.xml').getroot()
        counts = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))}
                  for c in root.findall('counter')}
        results[module] = {'tests': sums['tests'], 'suites': len(reports), 'FESFlakyNotRun': 0,
                           'staticIssues': 0, 'hostCounters': counts, 'xmlHashes': hashes,
                           'jarSha256': sha(base / name), 'execSha256': sha(base / 'jacoco.exec'),
                           'coverageSha256': sha(base / 'jacoco.xml'), 'staticSha256': sha(base / 'spotbugsXml.xml')}
        tests += sums['tests']; suites += len(reports)
    assert tests == 3457 and suites == 511 and total_classes == 1603
    assert results['bootstrap']['tests'] == 267
    remaining = {k: sum(m['hostCounters'][k]['missed'] for m in results.values())
                 for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
    result = {'actualExit': 0, 'run': 'PG599-candidate-bootstrap-six-host-v1', 'candidateSource': source,
              'installedVmSource': '969d8ded10c0bf5841d9e3a5c531e922caf4a24a', 'candidateNotDeployed': True,
              'sourceQualification': 'UNACCEPTED_CANDIDATE_FRESH_SIX_HOST_ONLY', 'tests': tests,
              'suites': suites, 'mainClasses': total_classes, 'allMainBytesEqualSelectedCandidate': True,
              'FESFlakyNotRunIndicators': 0, 'staticModules': 6, 'staticIssues': 0,
              'moduleResults': results, 'remainingHostOnly': remaining,
              'oldNativeStreamsNotImported': True, 'nativeNotRunCredit0': True,
              'historicalV1Hold': 'BUG-878', 'global100': all(v == 0 for v in remaining.values()),
              'formalAccepted': False, 'wholeWbsAccepted': False, 'rawExported': False,
              'started': (run / 'started').read_text().strip(), 'completed': (run / 'completed').read_text().strip(),
              'elapsedSeconds': end - start, 'logSha256': sha(run / 'build.private.log'),
              'sourceFilesSha256': sha(run / 'source-files.sha256'), 'collectorSha256': sha(pathlib.Path(__file__))}
    with (run / 'manifest.safe.json').open('x') as f:
        json.dump(result, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps({'actualExit': 0, 'tests': tests, 'suites': suites, 'staticIssues': 0,
                      'candidateMainClasses': 1603, 'remainingHostOnly': remaining,
                      'manifestSha256': sha(run / 'manifest.safe.json'), 'formalAccepted': False}))


if __name__ == '__main__':
    assert len(sys.argv) == 2
    main(sys.argv[1])
