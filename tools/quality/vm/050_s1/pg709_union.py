"""Offline all-six unchanged byte union: frozen host + new selected2 + current native9."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    host = W / 'pg680-owner-six-host-v1'; selected = W / 'pg707-owner-negatives-v1'
    native = W / 'pg698-current-eight-native-v1'; ninth = W / 'pg704-current-nine-native-v1'
    h = json.loads((host / 'manifest.safe.json').read_bytes())
    s = json.loads((selected / 'manifest.safe.json').read_bytes())
    n = json.loads((native / 'manifest.safe.json').read_bytes())
    b = json.loads((ninth / 'manifest.safe.json').read_bytes())
    assert sha(host / 'manifest.safe.json') == 'b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6'
    assert sha(selected / 'manifest.safe.json') == 'd6124de12211ce3b3784daf4cab2b2041270fa1ccd63db180eb22fd1d5c80d62'
    assert sha(native / 'manifest.safe.json') == 'e55c6095a06be0e1aa5a316ee8e43663714728ed5527624e3223c30c1b2a4045'
    assert sha(ninth / 'manifest.safe.json') == 'f5c612e6a3445c4ead6c103da1a8d77e4d323aca9ad02a525c1f426c6da9ae11'
    assert s['actualExit'] == 0 and s['selectedTests'] == 40 and s['FESFlakyNotRun'] == 0
    assert s['allMainClassBytesEqualPG680'] == 1612 and s['staticIssues'] == 0
    assert s['productionSource'] == n['productionSource'] == b['source'] == '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'
    data = []
    for m in MODULES:
        path = host / m / 'jacoco.exec'
        assert sha(path) == h['moduleResults'][m]['execSha256'] == n['hostExecHashes'][m]
        data.append(path)
    for m in ('api', 'batch'):
        path = selected / m / 'jacoco.exec'; assert sha(path) == s['selectedExecHashes'][m]; data.append(path)
    for i, value in enumerate(n['selected']):
        path = native / (str(i) + '.exec'); assert sha(path) == value['sha256']; data.append(path)
    path = ninth / 'bootstrap.exec'; assert sha(path) == b['bootstrap']['sha256']; data.append(path)
    assert len(data) == 17
    helper = W / 'pg571-current-ten-native-v2/classes'
    assert sha(helper / 'NativeCoverage.class') == '37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a'
    repo = Path('/home/mini/codex/project1/work/toolchain/m2/repository'); cp = [str(helper)]
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar', 'org/ow2/asm/asm/9.10.1/*.jar',
                    'org/ow2/asm/asm-tree/9.10.1/*.jar', 'org/ow2/asm/asm-commons/9.10.1/*.jar'):
        paths = list(repo.glob(pattern)); assert len(paths) == 1; cp.append(str(paths[0]))
    target = W / 'pg709-owner-negatives-union-v1'; target.mkdir(mode=0o700)
    counts = {}; gain = {}
    for m in MODULES:
        jar = host / m / ('schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar')
        assert sha(jar) == h['moduleResults'][m]['jarSha256']
        result = subprocess.run(['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java',
                                 '-cp', ':'.join(cp), 'NativeCoverage', str(jar), *map(str, data)],
                                capture_output=True, timeout=45)
        with (target / (m + '.private.log')).open('xb') as output: output.write(result.stdout + result.stderr)
        assert result.returncode == 0 and not result.stderr
        value = json.loads(result.stdout); assert value['classByteMismatch'] == 0
        counts[m] = value
        gain[m] = {k: b['moduleCounters'][m][k]['missed'] - value[k]['missed'] for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
        assert all(v >= 0 for v in gain[m].values())
    record = {'actualExit': 0, 'productionSource': s['productionSource'], 'operatorSource': s['operatorSource'],
              'run': target.name, 'qualifiedNativeStreams': 9, 'selectedHostTests': 40,
              'allMainClassBytesEqualPG680': 1612, 'moduleCounters': counts, 'gainVsPG704': gain,
              'remaining': {k: sum(v[k]['missed'] for v in counts.values()) for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')},
              'qualificationManifests': {p.name: sha(p / 'manifest.safe.json') for p in (host, selected, native, ninth)},
              'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'otherSourceMainBytesImported': False,
              'coverage100': all(v[k]['missed'] == 0 for v in counts.values() for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')),
              'formalAccepted': False, 'rawExported': False}
    with (target / 'manifest.safe.json').open('x') as output: json.dump(record, output, sort_keys=True)
    print(json.dumps({'actualExit': 0, 'gain': {k: sum(v[k] for v in gain.values()) for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')},
                      'remaining': record['remaining'], 'manifestSha256': sha(target / 'manifest.safe.json')}))


if __name__ == '__main__': main()
