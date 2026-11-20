"""Test the exact current Maven floor with the preceding upstream distribution."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path.cwd()
OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
JAVA = ROOT.parent / 'toolchain/jdk-25.0.4'
CACHE = ROOT.parent / 'toolchain/m2/repository'
ARCHIVE_URL = ('https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/'
               '3.9.11/apache-maven-3.9.11-bin.tar.gz')
CHECKSUM_URL = ('https://archive.apache.org/dist/maven/maven-3/3.9.11/binaries/'
                'apache-maven-3.9.11-bin.tar.gz.sha512')
SHA512 = ('bcfe4fe305c962ace56ac7b5fc7a08b87d5abd8b7e89027ab251069faebee516b0d'
          'ed8961445d6d91ec1985dfe30f8153268843c89aa392733d1a3ec956c9978')


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def git(*args):
    return subprocess.check_output(['git', *args])


def write(path, document):
    with path.open('x') as output:
        json.dump(document, output, indent=2, ensure_ascii=False)
        output.write('\n')


def main():
    start = json.loads(next(PLAN.glob('1015_F02*')).read_text())['values']
    assert all(pin(Path(ref['path'])) == ref for ref in start['oracleReferences'])
    source = start['source']
    core = start['productionCoreMain']
    assert git('show', f'{source}:pom.xml') == git('show', f'{core}:pom.xml')
    assert git('show', f'{source}:.mvn/wrapper/maven-wrapper.properties') == git(
        'show', f'{core}:.mvn/wrapper/maven-wrapper.properties')
    assert shutil.disk_usage('/dev/shm').free >= 64 * 1024**2
    out = OPS / start['run']
    out.mkdir()
    with tempfile.TemporaryDirectory(dir='/dev/shm', prefix='pgpt-maven-lower-bound-') as tmp:
        local = Path(tmp)
        pom = local / 'pom.xml'
        pom.write_bytes(git('show', f'{source}:pom.xml'))
        archive = local / 'distribution.tar.gz'
        subprocess.run(['curl', '--fail', '--silent', '--show-error', '--proto', '=https',
                        '--max-time', '30', '--max-filesize', '12582912', '--output',
                        str(archive), ARCHIVE_URL], check=True)
        assert hashlib.sha512(archive.read_bytes()).hexdigest() == SHA512
        subprocess.run(['tar', '-xzf', str(archive), '-C', str(local)], check=True)
        maven = local / 'apache-maven-3.9.11/bin/mvn'
        home = local / 'isolated-home'
        home.mkdir()
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': str(home),
               'JAVA_HOME': str(JAVA), 'MAVEN_SKIP_RC': 'true',
               'MAVEN_OPTS': f'-Duser.home={home} -Djava.io.tmpdir={local}'}
        args = [str(maven), '-N', '-B', '-o', '-ntp', '-Dstyle.color=never',
                '-Dmaven.repo.local=' + str(CACHE), '-f', str(pom), 'validate']
        version = subprocess.run([str(maven), '--version'], env=env, cwd=local,
                                 capture_output=True, text=True, timeout=15, check=True)
        observed_version = [line.split(' (', 1)[0] for line in version.stdout.splitlines()
                            if line.startswith(('Apache Maven ', 'Java version: '))]
        begin = out / 'begin.json'
        write(begin, dict(source=source, productionCore=core, rootPomSha256=pin(pom)['sha256'],
                          javaSha256=pin(JAVA / 'bin/java')['sha256'],
                          downloadUrl=ARCHIVE_URL, checksumUrl=CHECKSUM_URL, archiveSha512=SHA512,
                          mavenScriptSha256=pin(maven)['sha256'], toolVersions=observed_version,
                          command=[part.replace(tmp, '<PRIVATE_TMPFS>') for part in args],
                          startedAtUTC=datetime.now(timezone.utc).isoformat()))
        result = subprocess.run(args, env=env, cwd=local, capture_output=True, timeout=45)
        log = result.stdout + result.stderr
        allow = ('[INFO] --- ', '[INFO] Rule ', '[INFO] BUILD ',
                 '[ERROR] Rule ', '[ERROR] Detected Maven Version:')
        lines = [line for line in log.decode('utf-8', 'replace').splitlines()
                 if line.startswith(allow)]
        observed = out / 'enforcer.txt'
        observed.write_text('\n'.join(lines) + '\n')
        stages = [line for line in lines if line.startswith('[INFO] --- ')]
        terminal = out / 'terminal.json'
        write(terminal, dict(source=source, productionCore=core, actualExit=result.returncode,
                             terminalAtUTC=datetime.now(timezone.utc).isoformat(), begin=pin(begin),
                             rawProcessSha256=hashlib.sha256(log).hexdigest(), output=pin(observed),
                             observedStages=stages, targetCreated=(local / 'target').exists(),
                             productCompiles=0, productTests=0, remoteOperations=0))
        print(pin(terminal))


if __name__ == '__main__':
    main()
