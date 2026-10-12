"""Freeze current-DONE placement operator and signed new input; host only."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
from pg1446_current_cold_stage import W
from pg1640_completed_unused_candidate_sources import sources, TOOLS, BEFORE, CURRENT
from pg1630_api_terminal_selected import PRODUCTION
from pg601_stage_contract import check_members

P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
J = Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
TARGET = W / TOOLS
ARCHIVE = P / 'pg1643-release-v1.tar'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(path, raw):
    with path.open('xb') as f:
        os.fchmod(f.fileno(), 0o400)
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed operator required')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    candidate = json.loads((W / 'pg1638-candidate-build-v1.safe.json').read_bytes())
    current = json.loads((W / 'pg1641-completed-current-before-v2/manifest.safe.json').read_bytes())
    if candidate['actualExit'] != 0 or candidate['candidateSource'] != PRODUCTION or not candidate['signatureVerified'] or not candidate['candidateNotDeployed']:
        raise ValueError('independently signed new-source input required')
    if current['actualExit'] != 0 or current['productionSource'] != CURRENT or current['privateBeforeSha256'] != BEFORE:
        raise ValueError('actual full current genuine-DONE before required')
    prior = json.loads((W / 'pg1610-frozen-v1.safe.json').read_bytes())
    if prior['actualExit'] != 0 or prior['productionSource'] != CURRENT:
        raise ValueError('qualified same current shared ABI required')
    release = W / 'pg1638-release-v1'
    signature = P / 'pg1638-manifest-v1.sig'
    if sha(release / 'RELEASE-MANIFEST.json') != candidate['manifestSha256'] or sha(signature) != candidate['signatureSha256']:
        raise ValueError('immutable signed input changed')
    if os.path.lexists(TARGET) or os.path.lexists(ARCHIVE):
        raise ValueError('new-only tool and input namespace required')
    if os.statvfs(P).f_bavail * os.statvfs(P).f_frsize < 10 * 1024**3 + sum(p.stat().st_size for p in release.rglob('*') if p.is_file()) * 2:
        raise ValueError('preservation capacity required')
    TARGET.mkdir(mode=0o700)
    with tarfile.open(ARCHIVE, 'x:') as t:
        for p in sorted(release.rglob('*')):
            if p.is_symlink():
                raise ValueError('candidate link refused')
            t.add(p, arcname=str(p.relative_to(release)), recursive=False)
    data = json.loads((release / 'RELEASE-MANIFEST.json').read_bytes())
    with tarfile.open(ARCHIVE, 'r:') as t:
        check_members(t.getmembers(), {r['path'] for r in data['artifacts']} | {'RELEASE-MANIFEST.json', 'SHA256SUMS'})
    bundle = json.dumps({'archiveSha256': sha(ARCHIVE), 'signatureSha256': sha(signature)}, sort_keys=True).encode()
    generated = sources(candidate['manifestSha256'])
    generated['pg1640_native_refs.py'] = 'BUNDLE_HASH=' + repr(hashlib.sha256(bundle).hexdigest()) + '\n' + generated['pg1640_native_refs.py']
    generated['bundle.safe.json'] = bundle.decode()
    for name, digest in prior['fileHashes'].items():
        if not name.endswith('.class') or name.startswith('Pg1609'):
            continue
        p = W / 'pg1609-current-ordinary-owned-stop-tools-v1' / name
        if sha(p) != digest:
            raise ValueError('qualified shared class changed')
        write(TARGET / name, p.read_bytes())
    for name, raw in generated.items():
        write(TARGET / name, raw.encode())
    old = W / 'pg1544-release-v1'
    cp = ':'.join(str(p) for p in [TARGET, old / 'api/api.jar', old / 'operations/batch.jar', old / 'api/lib/*', old / 'operations/lib/*'])
    repo = Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp += ':' + ':'.join(str(repo / p) for p in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar', 'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar', 'com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    names = ['Pg1640UnusedStage.java', 'Pg1640NativeArgumentTest.java', 'Pg1640StopLabelTest.java', 'Pg1640OriginalTupleTest.java']
    commands = [('compile', [str(J / 'javac'), '-Xlint:all', '-Werror', '-sourcepath', '', '-cp', cp, '-d', str(TARGET), *[str(TARGET / n) for n in names]])]
    commands += [(label, [str(J / 'java'), '--enable-native-access=ALL-UNNAMED', '-cp', cp, clazz]) for label, clazz in [('argument', 'Pg1640NativeArgumentTest'), ('label', 'Pg1640StopLabelTest'), ('original', 'Pg1640OriginalTupleTest')]]
    phases = {}
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for label, argv in commands:
        log = W / ('pg1642-' + label + '-v1.private.log')
        with log.open('xb') as f:
            r = subprocess.run(argv, stdout=f, stderr=f)
            f.flush()
            os.fsync(f.fileno())
        phases[label] = {'actualExit': r.returncode, 'logSha256': sha(log)}
        if r.returncode:
            break
    hashes = {p.name: sha(p) for p in TARGET.iterdir() if p.is_file()}
    for p in TARGET.iterdir():
        p.chmod(0o400)
    write(TARGET / 'payload-sha256.json', json.dumps(hashes, sort_keys=True).encode())
    value = {'actualExit': r.returncode, 'operatorSource': head, 'productionSource': CURRENT, 'candidateSource': PRODUCTION, 'candidateManifestSha256': candidate['manifestSha256'], 'genuineParentBeforeSha256': BEFORE, 'bundleSha256': sha(ARCHIVE), 'fileHashes': hashes, 'phases': phases, 'startedUTC': started, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'guestMutations0': True, 'formalAccepted': False}
    write(W / 'pg1642-frozen-v1.safe.json', json.dumps(value, sort_keys=True).encode())
    print(json.dumps({k: v for k, v in value.items() if k not in ['fileHashes', 'phases']}))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
