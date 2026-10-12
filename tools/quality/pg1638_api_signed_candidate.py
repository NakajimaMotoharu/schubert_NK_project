"""New-only signed API candidate. Host signing material never leaves host.

Requires completed independent PG1636; immutable old187 artifacts and SQL,
exact three-changed/six-added Main classes, fixed full-source inputs and six
qualified JARs. Does not deploy, activate, reload, boot or start anything.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import pg1535_filesystem_signed_candidate as transfer
from pg548_candidate_contract import artifacts, class_inventory
from pg1630_api_terminal_selected import PRODUCTION
from pg1637_api_candidate_contract import MODULES, validate_gate, verify_delta

W, P, T = transfer.W, transfer.P, transfer.T
OLD = W / 'pg1544-release-v1'
NEXT = W / 'pg1638-release-v1'
FROZEN = W / 'pg1638-frozen-six-v1'
SIG = P / 'pg1638-manifest-v1.sig'
OLD_SOURCE = '4d6bcbddb417b76d27e52d5d9640752c300edccf'
OLD_BOM = 'e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def require(value):
    if not value:
        raise ValueError('sameSource signed candidate boundary refused')


def receive(module):
    import inspect
    raw = inspect.getsource(transfer.receive).replace('PG1532', 'PG1633').replace('pg1535', 'pg1638')
    ns = {**transfer.__dict__, 'FROZEN': FROZEN}
    exec(compile(raw, '<fixed qualified PG1633 JAR transport>', 'exec'), ns)
    return ns['receive'](module)


def main():
    os.umask(0o077)
    require(not subprocess.check_output(['git', 'diff', '--name-only', '1683dd9f6de00e71d2317d9af3cd50400a37bf4e', 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=T))
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=T))
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip()
    report = W / 'pg1638-candidate-build-v1.safe.json'
    require(not any(os.path.lexists(p) for p in [NEXT, FROZEN, SIG, report]))
    raw_gate = (W / 'pg1636-api-boundary-full-qualified-v1/manifest.safe.json').read_bytes()
    outer = json.loads(raw_gate)
    gate = validate_gate(outer, PRODUCTION)
    from pg1636_api_boundary_full_qualification import server
    require(outer['qualificationSourceSha256'] == hashlib.sha256(server().encode()).hexdigest())
    old_raw = (OLD / 'RELEASE-MANIFEST.json').read_bytes()
    require(hashlib.sha256(old_raw).hexdigest() == OLD_BOM)
    data = json.loads(old_raw)
    baseline = artifacts(json.loads(old_raw)['artifacts'])
    require(data['source']['commit'] == OLD_SOURCE and data['release'] == '0.1.0-PG1544' and data['versions']['schema'] == '028')
    require(not OLD.is_symlink() and all(not p.is_symlink() and (p.is_dir() or p.is_file()) for p in OLD.rglob('*')))
    require({str(p.relative_to(OLD)) for p in OLD.rglob('*') if p.is_file()} == set(baseline) | {'RELEASE-MANIFEST.json', 'SHA256SUMS'})
    for path, row in baseline.items():
        require((OLD / path).stat().st_size == row['size'] and sha(OLD / path) == row['sha256'])
    require(os.statvfs(W).f_bavail * os.statvfs(W).f_frsize >= 10 * 1024**3 + sum(r['size'] for r in baseline.values()) * 3)
    FROZEN.mkdir(mode=0o700)
    before, after, jars = {}, {}, {}
    for module in MODULES:
        p = receive(module)
        require(sha(p) == gate['jarHashes'][module])
        jars[module] = p
        old_path = {'api': 'api/api.jar', 'web': 'web/web.jar', 'batch': 'operations/batch.jar'}.get(module)
        if old_path is None:
            old_path = next(path for path in baseline if Path(path).name == p.name)
        before[module], after[module] = class_inventory(OLD / old_path), class_inventory(p)
    require(verify_delta(before, after) == 1643)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    shutil.copytree(OLD, NEXT)
    require((NEXT / 'VERSION').read_bytes() == b'0.1.0-PG1544\n')
    (NEXT / 'VERSION').write_bytes(b'0.1.0-PG1638\n')
    main_paths = {'api/api.jar': 'api', 'web/web.jar': 'web', 'operations/batch.jar': 'batch'}
    allowed = {'VERSION'}
    for row in data['artifacts']:
        path = row['path']
        p = NEXT / path
        module = main_paths.get(path)
        if module is None:
            module = next((m for m in MODULES if p.name == jars[m].name), None)
        if module is not None:
            shutil.copyfile(jars[module], p)
            allowed.add(path)
            require(sha(p) == gate['jarHashes'][module])
        row['size'], row['sha256'] = p.stat().st_size, sha(p)
    changed = {r['path'] for r in data['artifacts'] if r['sha256'] != baseline[r['path']]['sha256']}
    require(changed <= allowed and {'VERSION', 'api/api.jar'} <= changed)
    require(len(list((NEXT / 'db/migration').glob('*.sql'))) == 28 and len(data['migrations']) == 29)
    for path in set(baseline) - allowed:
        require((NEXT / path).read_bytes() == (OLD / path).read_bytes())
    data['release'], data['source']['commit'] = '0.1.0-PG1638', PRODUCTION
    encoded = json.dumps(data, ensure_ascii=False, indent=2).encode() + b'\n'
    (NEXT / 'RELEASE-MANIFEST.json').write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest()
    sums = {r['path']: r['sha256'] for r in data['artifacts']}
    sums['RELEASE-MANIFEST.json'] = digest
    (NEXT / 'SHA256SUMS').write_bytes(''.join(sums[n] + '  ' + n + '\n' for n in sorted(sums)).encode())
    require(set(artifacts(data['artifacts'])) == set(baseline))
    for row in data['artifacts']:
        require((NEXT / row['path']).stat().st_size == row['size'] and sha(NEXT / row['path']) == row['sha256'])
    with (W / 'pg1638-sign-v1.private.log').open('xb') as log:
        subprocess.run(['openssl', 'pkeyutl', '-sign', '-rawin', '-inkey', str(P / 'pg381-release-signing.pem'), '-in', str(NEXT / 'RELEASE-MANIFEST.json'), '-out', str(SIG)], stdout=log, stderr=log, check=True)
        subprocess.run(['openssl', 'pkeyutl', '-verify', '-rawin', '-pubin', '-keyform', 'DER', '-inkey', str(P / 'pg381-release-pin.der'), '-in', str(NEXT / 'RELEASE-MANIFEST.json'), '-sigfile', str(SIG)], stdout=log, stderr=log, check=True)
    require(SIG.stat().st_size == 64)
    for p in [SIG] + [p for p in NEXT.rglob('*') if p.is_file()]:
        with p.open('rb') as f:
            os.fsync(f.fileno())
    for p in sorted([p for p in NEXT.rglob('*') if p.is_dir()] + [NEXT], key=lambda p: len(p.parts), reverse=True):
        fd = os.open(p, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    value = {'run': 'PG1638-candidate-build-v1', 'actualExit': 0, 'candidateSource': PRODUCTION, 'operatorSource': operator, 'priorSource': OLD_SOURCE, 'release': '0.1.0-PG1638', 'startedUTC': started, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'hostGateSha256': hashlib.sha256(raw_gate).hexdigest(), 'tests': 3596, 'suites': 532, 'mainClasses': 1643, 'changedClasses': 3, 'addedClasses': 6, 'manifestSha256': digest, 'artifacts': 187, 'schema': '028', 'sql': 28, 'history': 29, 'changedArtifactPaths': sorted(changed), 'signatureVerified': True, 'signatureSha256': sha(SIG), 'helperSha256': sha(Path(__file__)), 'guestMutations0': True, 'candidateNotDeployed': True, 'formalAccepted': False}
    with report.open('x') as f:
        json.dump(value, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(value))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
