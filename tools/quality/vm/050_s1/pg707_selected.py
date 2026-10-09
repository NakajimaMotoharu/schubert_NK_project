"""Test-only two-module owner negatives; frozen six main byte equality is mandatory."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile

T = Path('/home/mini/codex/project1/work/pgpt-foundation')
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
D = W / 'pg707-owner-negatives-v1'
HOST = W / 'pg680-owner-six-host-v1'
MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')


def classes(path):
    with zipfile.ZipFile(path) as archive:
        return {n: archive.read(n) for n in archive.namelist() if n.endswith('.class')}


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=T) == b''
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip()
    assert not subprocess.check_output(['git', 'diff', '--name-only', '9bd50536f692610036a0ed8b83e0a8b35fe2a66f', '--',
                                        'src/**/src/main', 'pom.xml', 'src/**/pom.xml'], cwd=T)
    assert hashlib.sha256((HOST / 'manifest.safe.json').read_bytes()).hexdigest() == 'b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6'
    for module in MODULES:
        name = 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'
        assert classes(HOST / module / name) == classes(T / 'src' / ('schubert-nk-' + module) / 'target' / name)
    D.mkdir(mode=0o700)
    prior_reports = D / 'preexisting-reports'; prior_reports.mkdir(mode=0o700)
    for module in ('api', 'batch'):
        target = T / 'src' / ('schubert-nk-' + module) / 'target'
        path = target / 'jacoco.exec'
        if path.exists(): path.rename(D / ('preexisting-' + module + '.exec'))
        for p in (target / 'surefire-reports').glob('TEST-*.xml'):
            if p.name.endswith(('BootstrapAdminMainTest.xml', 'ApiProcessMainTest.xml', 'MorningDatabaseSessionTest.xml')):
                p.rename(prior_reports / (module + '-' + p.name))
        if (target / 'spotbugsXml.xml').exists():
            (target / 'spotbugsXml.xml').rename(D / ('preexisting-' + module + '-spotbugs.xml'))
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    env = dict(os.environ); env['JAVA_HOME'] = '/home/mini/codex/project1/work/toolchain/jdk-25.0.4'
    env['PATH'] = env['JAVA_HOME'] + '/bin:' + env['PATH']
    command = ['./mvnw', '-o', '--no-transfer-progress', '-Dstyle.color=never', '-Djansi.force=false',
               '-Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository',
               '-pl', 'src/schubert-nk-api,src/schubert-nk-batch', 'spotless:check', 'test-compile',
               'test', 'spotbugs:check', 'jacoco:report', 'jar:jar',
               '-Dtest=BootstrapAdminMainTest,ApiProcessMainTest,MorningDatabaseSessionTest']
    # Existing toolchain fixture credentials stay private; whole stdout/stderr is not exported.
    with (D / 'build.private.log').open('xb') as output:
        outcome = subprocess.run(command, cwd=T, env=env, stdout=output, stderr=output)
        output.flush(); os.fsync(output.fileno())
    with (D / 'exit').open('x') as output: output.write(str(outcome.returncode) + '\n')
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip() == source
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=T) == b''
    if outcome.returncode == 0:
        for module in MODULES:
            name = 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'
            assert classes(HOST / module / name) == classes(T / 'src' / ('schubert-nk-' + module) / 'target' / name)
    files = {}
    for module in ('api', 'batch'):
        root = D / module; root.mkdir(mode=0o700)
        target = T / 'src' / ('schubert-nk-' + module) / 'target'
        for p in (target / 'surefire-reports').glob('TEST-*.xml'):
            if p.name.endswith(('BootstrapAdminMainTest.xml', 'ApiProcessMainTest.xml', 'MorningDatabaseSessionTest.xml')):
                with (root / p.name).open('xb') as output: output.write(p.read_bytes())
        for name in ('jacoco.exec', 'spotbugsXml.xml', 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'):
            p = target / name
            if p.exists():
                with (root / name).open('xb') as output: output.write(p.read_bytes())
        for p in root.iterdir(): files[str(p.relative_to(D))] = hashlib.sha256(p.read_bytes()).hexdigest()
    record = {'actualExit': outcome.returncode, 'operatorSource': source, 'productionSource': '9bd50536f692610036a0ed8b83e0a8b35fe2a66f',
              'command': command, 'startedUTC': start, 'endedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'files': files, 'allSixMainBytesUnchanged': outcome.returncode == 0,
              'formalAccepted': False, 'rawExported': False}
    with (D / 'run.safe.json').open('x') as output: json.dump(record, output, sort_keys=True)
    print(json.dumps({'actualExit': outcome.returncode, 'source': source, 'formalAccepted': False}))
    raise SystemExit(outcome.returncode)


if __name__ == '__main__': main()
