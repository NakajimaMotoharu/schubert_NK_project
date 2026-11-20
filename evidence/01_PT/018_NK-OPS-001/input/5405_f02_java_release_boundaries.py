"""Exercise both ends of the exact Java release contract with real runtimes."""

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
MAVEN = Path('/home/mini/.m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn')
CACHE = ROOT.parent / 'toolchain/m2/repository'
RELEASES = {
    '24': ('jdk-24.0.2%2B12', '24.0.2_12',
           'bee902852ae8b6698e04eb1599dc94af844ae45b72b3b8ec854350b9aba41335'),
    '26': ('jdk-26%2B35', '26_35',
           '3a65331f4c4b671a5e5bb3ae4e4a65fd0eb5bf8672c0c2fba6ba36972c4042a4'),
}


def sha(path):
    with path.open('rb') as data:
        return hashlib.file_digest(data, 'sha256').hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path))


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def check(major, tag, build, digest, frozen, out):
    url = (f'https://github.com/adoptium/temurin{major}-binaries/releases/download/{tag}/'
           f'OpenJDK{major}U-jre_x64_linux_hotspot_{build}.tar.gz')
    with tempfile.TemporaryDirectory(dir='/dev/shm', prefix='pgpt-java-enforcer-') as name:
        scratch = Path(name)
        package = scratch/'runtime.tar.gz'
        subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location', '--proto', '=https',
                        '--proto-redir', '=https', '--max-time', '60', '--max-filesize', '83886080',
                        '--output', str(package), url], check=True)
        assert sha(package) == digest
        subprocess.run(['tar','-xzf',str(package),'-C',str(scratch)], check=True)
        versions = list(scratch.glob('*/bin/java'))
        assert len(versions) == 1
        java = versions[0]
        home = scratch/'isolated-home'
        home.mkdir()
        pom = scratch/'pom.xml'
        pom.write_bytes(frozen)
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': str(home),
               'MAVEN_SKIP_RC': 'true', 'JAVA_HOME': str(java.parent.parent),
               'MAVEN_OPTS': f'-Duser.home={home} -Djava.io.tmpdir={scratch}'}
        version = subprocess.run([str(MAVEN), '--version'], env=env, cwd=scratch, capture_output=True,
                                 check=True, timeout=15).stdout.decode('utf-8')
        versions = [line.split(', runtime: ', 1)[0].split(' (', 1)[0]
                    for line in version.splitlines() if line.startswith(('Apache Maven ', 'Java version: '))]
        command = [str(MAVEN), '-N', '-B', '-o', '-ntp', '-Dstyle.color=never',
                   '-Dmaven.repo.local='+str(CACHE), '-f', str(pom), 'validate']
        result = subprocess.run(command, env=env, cwd=scratch, capture_output=True, timeout=30)
        diagnostics = result.stdout + result.stderr
        prefixes = ('[INFO] --- ', '[INFO] Rule ', '[INFO] BUILD ',
                    '[ERROR] Rule ', '[ERROR] Detected JDK version')
        lines = [line.replace(name, '<TMPFS>') for line in diagnostics.decode('utf-8', 'replace').splitlines()
                 if line.startswith(prefixes)]
        recorded = out / f'java-{major}.txt'
        recorded.write_text('\n'.join(lines) + '\n')
        return dict(actualExit=result.returncode, destinationCreated=(scratch/'target').exists(),
                    runtimeBinarySha256=sha(java), distributionSha256=digest, sourceUrl=url,
                    tools=versions, observed=pin(recorded), pomSha256=sha(pom),
                    rawSha256=hashlib.sha256(diagnostics).hexdigest(),
                    command=[part.replace(name, '<TMPFS>') for part in command],
                    terminalAtUTC=datetime.now(timezone.utc).isoformat())


def main():
    start = json.loads(next(PLAN.glob('1033_F02*')).read_bytes())['values']
    assert all(pin(Path(ref['path'])) == ref for ref in start['oracleReferences'])
    release = subprocess.check_output(['git', 'show', f'{start["productionCoreMain"]}:pom.xml'])
    assert release == subprocess.check_output(['git', 'show', f'{start["source"]}:pom.xml'])
    assert MAVEN.is_file() and CACHE.is_dir() and shutil.disk_usage('/dev/shm').free > 512 * 1024**2
    out = OPS/start['run']
    out.mkdir()
    begin = dict(source=start['source'], productionCore=start['productionCoreMain'],
                 maven=pin(MAVEN), mavenCore=pin(MAVEN.parent.parent/'lib/maven-core-3.9.12.jar'),
                 startedAtUTC=datetime.now(timezone.utc).isoformat())
    write(out/'begin.json', begin)
    cases = {}
    for major, inputs in RELEASES.items():
        try:
            cases[major] = check(major, *inputs, release, out)
        except (subprocess.SubprocessError, AssertionError) as failure:
            cases[major] = dict(notRun=True, phase='tool preparation or invocation',
                                cause=type(failure).__name__, actualExit=getattr(failure, 'returncode', None))
    terminal = out/'terminal.json'
    write(terminal, dict(**begin, cases=cases, productBuilds=0, productTests=0,
                         terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(terminal), {case: result['actualExit'] for case, result in cases.items()})


if __name__ == '__main__':
    main()
