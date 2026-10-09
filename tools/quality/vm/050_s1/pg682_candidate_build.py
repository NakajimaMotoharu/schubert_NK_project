"""New-only signed candidate from PG680 owner fixed host; no guest mutation/acceptance."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pg682_candidate_contract import MODULES, verify_delta

T = Path('/home/mini/codex/project1/work/pgpt-foundation')
R = T / 'tools/quality/vm/050_s1'
sys.path.insert(0, str(R))
from pg548_candidate_contract import artifacts, class_inventory

W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE = '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'
OLD_SOURCE = '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'
OLD = W / 'pg631-release-v1'
FROZEN = W / 'pg680-owner-six-host-v1'
NEXT = W / 'pg682-release-v1'
SIG = P / 'pg682-manifest-v1.sig'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    assert not NEXT.exists() and not SIG.exists()
    assert subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml'], cwd=T) == b''
    assert subprocess.check_output(['git', 'diff', 'HEAD', '--', 'src', 'tools', 'pom.xml'], cwd=T) == b''
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip()
    gate_raw = (FROZEN / 'manifest.safe.json').read_bytes(); gate = json.loads(gate_raw)
    assert hashlib.sha256(gate_raw).hexdigest() == 'b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6'
    assert gate['candidateSource'] == SOURCE and gate['actualExit'] == 0
    assert gate['tests'] == 3489 and gate['suites'] == 516 and gate['FESFlakyNotRunIndicators'] == 0
    assert gate['staticModules'] == 6 and gate['staticIssues'] == 0
    assert gate['knownOracleHold'] is None and gate['mainClasses'] == 1612
    assert gate['oldNativeStreamsNotImported'] and gate['candidateNotDeployed']
    raw = (OLD / 'RELEASE-MANIFEST.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'
    data = json.loads(raw)
    # Separate authenticated old rows; mutable new rows never overwrite the baseline oracle.
    baseline = artifacts(json.loads(raw)['artifacts'])
    assert data['source']['commit'] == OLD_SOURCE and data['versions']['schema'] == '028'
    for path, row in baseline.items():
        p = OLD / path
        assert not p.is_symlink() and p.stat().st_size == row['size'] and sha(p) == row['sha256']
    assert not OLD.is_symlink()
    assert all(not p.is_symlink() and (p.is_dir() or p.is_file()) for p in OLD.rglob('*'))
    assert {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()} \
        == set(baseline) | {'RELEASE-MANIFEST.json', 'SHA256SUMS'}
    old_classes = {}; new_classes = {}; jar_hashes = {}
    for module in MODULES:
        name = 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'
        frozen = FROZEN / module; row = gate['moduleResults'][module]
        jar = frozen / name
        assert sha(jar) == row['jarSha256'] and row['FESFlakyNotRun'] == row['staticIssues'] == 0
        assert sha(frozen / 'jacoco.xml') == row['coverageSha256']
        assert sha(frozen / 'spotbugsXml.xml') == row['staticSha256']
        assert not ET.parse(frozen / 'spotbugsXml.xml').getroot().findall('.//BugInstance')
        assert set(row['xmlHashes']) == {p.name for p in (frozen / 'surefire-reports').glob('TEST-*.xml')}
        for name_xml, digest in row['xmlHashes'].items():
            assert sha(frozen / 'surefire-reports' / name_xml) == digest
        old_path = {'api': 'api/api.jar', 'web': 'web/web.jar',
                    'batch': 'operations/batch.jar'}.get(module)
        if old_path is None:
            old_path = next(path for path in baseline if Path(path).name == name)
        # Prior class bytes come from authenticated signed payload, not a mutable host target.
        old_classes[module] = class_inventory(OLD / old_path)
        new_classes[module] = class_inventory(jar); jar_hashes[module] = row['jarSha256']
    assert verify_delta(old_classes, new_classes) == 1612
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    shutil.copytree(OLD, NEXT)
    version = NEXT / 'VERSION'
    assert version.read_bytes() == b'0.1.0-PG631\n'
    version.write_bytes(b'0.1.0-PG682\n')
    main_paths = {'api/api.jar': 'api', 'web/web.jar': 'web', 'operations/batch.jar': 'batch'}
    allowed = {'VERSION'}; bootstrap_paths = []
    for row in data['artifacts']:
        path = row['path']; p = NEXT / path; module = main_paths.get(path)
        if module is None:
            module = next((m for m in ('protocol', 'storage', 'bootstrap', 'api')
                           if p.name == 'schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar'), None)
        if module is not None:
            name = 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'
            shutil.copyfile(FROZEN / module / name, p); allowed.add(path)
            assert sha(p) == jar_hashes[module]
            if module == 'bootstrap': bootstrap_paths.append(path)
        row['size'] = p.stat().st_size; row['sha256'] = sha(p)
    assert len(bootstrap_paths) == 3
    changed = {r['path'] for r in data['artifacts'] if r['sha256'] != baseline[r['path']]['sha256']}
    assert changed <= allowed and {'VERSION', 'api/api.jar'} <= changed
    assert len(list((NEXT / 'db/migration').glob('*.sql'))) == 28 and len(data['migrations']) == 29
    for path in set(baseline) - allowed: assert (NEXT / path).read_bytes() == (OLD / path).read_bytes()
    data['release'] = '0.1.0-PG682'; data['source']['commit'] = SOURCE
    manifest = json.dumps(data, ensure_ascii=False, indent=2).encode() + b'\n'
    (NEXT / 'RELEASE-MANIFEST.json').write_bytes(manifest); digest = hashlib.sha256(manifest).hexdigest()
    sums = {r['path']: r['sha256'] for r in data['artifacts']}; sums['RELEASE-MANIFEST.json'] = digest
    (NEXT / 'SHA256SUMS').write_bytes(''.join(sums[n] + '  ' + n + '\n' for n in sorted(sums)).encode())
    assert set(artifacts(data['artifacts'])) == set(baseline)
    assert {p.relative_to(NEXT).as_posix() for p in NEXT.rglob('*') if p.is_file()} == set(baseline) | {'RELEASE-MANIFEST.json', 'SHA256SUMS'}
    for row in data['artifacts']:
        p = NEXT / row['path']; assert not p.is_symlink() and p.stat().st_size == row['size'] and sha(p) == row['sha256']
    log = W / 'pg682-sign-v1.private.log'
    with log.open('xb') as f:
        subprocess.run(['openssl', 'pkeyutl', '-sign', '-rawin', '-inkey', str(P / 'pg381-release-signing.pem'),
                        '-in', str(NEXT / 'RELEASE-MANIFEST.json'), '-out', str(SIG)], stdout=f, stderr=f, check=True)
        subprocess.run(['openssl', 'pkeyutl', '-verify', '-rawin', '-pubin', '-keyform', 'DER',
                        '-inkey', str(P / 'pg381-release-pin.der'), '-in', str(NEXT / 'RELEASE-MANIFEST.json'),
                        '-sigfile', str(SIG)], stdout=f, stderr=f, check=True)
    assert SIG.stat().st_size == 64
    safe = {'run': 'PG682-candidate-build-v1', 'candidateSource': SOURCE, 'operatorSource': operator,
            'priorSource': OLD_SOURCE, 'startedUTC': started,
            'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'hostGateSha256': hashlib.sha256(gate_raw).hexdigest(), 'tests': 3489, 'suites': 516,
            'staticModules': 6, 'staticIssues': 0, 'mainClasses': 1612, 'changedClasses': 6,
            'addedAbstractInterfaces': 7, 'addedInternalClasses': 0, 'release': '0.1.0-PG682', 'manifestSha256': digest,
            'artifacts': 187, 'schema': '028', 'sql': 28, 'history': 29,
            'changedArtifactPaths': sorted(changed), 'signatureVerified': True,
            'signatureSha256': sha(SIG), 'privateLogSha256': sha(log), 'helperSha256': sha(Path(__file__)),
            'guestMutations0': True, 'candidateNotDeployed': True, 'formalAccepted': False}
    with (W / 'pg682-candidate-build-v1.safe.json').open('x') as f:
        json.dump(safe, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps({'run': safe['run'], 'candidateSource': SOURCE, 'artifacts': 187,
                      'signatureVerified': True, 'guestMutations0': True, 'manifestSha256': digest}))


if __name__ == '__main__': main()
