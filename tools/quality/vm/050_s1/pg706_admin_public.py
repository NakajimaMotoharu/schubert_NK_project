"""Explicit ADMIN/post/native whitelist; never exports input bytes or JaCoCo sessions."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent; T = R.parents[3]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
D = T / 'evidence/01_PT/018_NK-OPS-001/evidence/PG702-current-admin-public-v1'


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=T) == b''
    D.mkdir(); files = {}
    allowed = ('run', 'actualExit', 'operatorSource', 'productionSource', 'startedAt', 'endedAt',
               'elapsedSeconds', 'privateLogSha256', 'oldCloseNotInferred', 'productionPT0',
               'formalAccepted', 'full21Fields', 'batchRows', 'bootstrapElapsedSeconds',
               'whole187SignedArtifactBytesVerified', 'unchangedSnapshots', 'tables', 'units',
               'allClientAdvisoryFlock0', 'allUnitKernel0', 'newMetadataScopesNormal',
               'retiredTwoSourceAbsent', 'runtimeCredentialsAbsent', 'verifyBeforeAfterEqual',
               'originalsBackupNativeCredentialsUnchanged', 'startsStopsReloadsSqlWrites', 'rawExported')
    for name in ('pg702-bootstrap-verify-v1', 'pg702-bootstrap-execute-v1', 'pg703-bootstrap-final-v4'):
        raw = (W / (name + '.safe.json')).read_bytes(); value = json.loads(raw)
        assert value['actualExit'] == 0
        safe = {k: value[k] for k in allowed if k in value}
        safe['privateReceiptSha256'] = hashlib.sha256(raw).hexdigest()
        data = (json.dumps(safe, indent=2) + '\n').encode()
        with (D / (name + '.json')).open('xb') as output: output.write(data)
        files[name + '.json'] = hashlib.sha256(data).hexdigest()
    raw = (W / 'pg704-current-nine-native-v1/manifest.safe.json').read_bytes(); value = json.loads(raw)
    assert value['actualExit'] == 0 and value['qualifiedSingleSessions'] == 9
    safe = {k: value[k] for k in ('run', 'actualExit', 'source', 'operatorSource', 'atUTC',
                                'qualifiedSingleSessions', 'frozenHostManifestSha256', 'remaining',
                                'gainVsPG698', 'otherSourceStreamsImported', 'coverage100', 'formalAccepted')}
    safe['moduleCounters'] = {}
    for module, counts in value['moduleCounters'].items():
        assert counts['classByteMismatch'] == 0
        safe['moduleCounters'][module] = {k: counts[k] for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
    safe['privateReceiptSha256'] = hashlib.sha256(raw).hexdigest()
    data = (json.dumps(safe, indent=2) + '\n').encode()
    with (D / 'pg704-native9.json').open('xb') as output: output.write(data)
    files['pg704-native9.json'] = hashlib.sha256(data).hexdigest()
    manifest = {'source': value['source'], 'run': D.name, 'files': files, 'specs': ['568', '569', '570'],
                'testIds': ['BOOT702001..002', 'BOOT703001..002', 'BOOT704001..002'],
                'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip(),
                'tools': {'jdk': '25.0.4', 'jacoco': '0.8.15', 'postgresql': '18.6'},
                'bugs': ['BUG-922'], 'ykt': ['YKT-691'], 'formalAccepted': False, 'coverage100': False,
                'rawInputsPasswordsSessionDBExported': False, 'pgptComplete': False}
    with (D / 'manifest.json').open('x') as output: json.dump(manifest, output, indent=2); output.write('\n')
    print(json.dumps({'safeReceipts': 4, 'manifestSha256': hashlib.sha256((D / 'manifest.json').read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
