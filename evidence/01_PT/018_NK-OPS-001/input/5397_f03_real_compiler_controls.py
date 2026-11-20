"""Exercise the actual inherited Maven compiler controls on three synthetic sources."""

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
MAVEN = Path('/home/mini/.m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn')
CHILD = Path('src/schubert-nk-protocol')
SOURCE = CHILD / 'src/main/java/dev/codex/schubert/nk/protocol/CompilerContractCanary.java'
TEMPLATES = {
    'valid': '''package dev.codex.schubert.nk.protocol;

import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

@NullMarked
final class CompilerContractCanary {
  static int length(@Nullable String value) {
    return value == null ? 0 : value.length();
  }
}
''',
    'nullable': '''package dev.codex.schubert.nk.protocol;

import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

@NullMarked
final class CompilerContractCanary {
  static int length(@Nullable String value) {
    return value.length();
  }
}
''',
    'unchecked': '''package dev.codex.schubert.nk.protocol;

import java.util.List;
import org.jspecify.annotations.NullMarked;

@NullMarked
final class CompilerContractCanary {
  static List<String> list(Object value) {
    return (List<String>) value;
  }
}
''',
}


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(['git', *args])


def main():
    start = json.loads(next(PLAN.glob('1018_F03*')).read_bytes())['values']
    assert all(pin(Path(ref['path'])) == ref for ref in start['oracleReferences'])
    poms = {path: git('show', f'{start["source"]}:{path}')
            for path in (Path('pom.xml'), CHILD / 'pom.xml')}
    assert all(data == git('show', f'{start["productionCoreMain"]}:{path}')
               for path, data in poms.items())
    assert shutil.disk_usage('/dev/shm').free > 128 * 1024**2
    assert JAVA.is_dir() and MAVEN.is_file() and CACHE.is_dir()
    out = OPS / start['run']
    out.mkdir()
    run_identity = dict(source=start['source'], productionCore=start['productionCoreMain'])
    begin = out / 'begin.json'
    write(begin, dict(**run_identity, maven=pin(MAVEN), java=pin(JAVA / 'bin/java'),
                      compiler=pin(JAVA / 'bin/javac'), pomInputs=[pin(path) for path in poms],
                      startedAtUTC=datetime.now(timezone.utc).isoformat(), expectedCases=3))
    outcomes = {}
    for case, template in TEMPLATES.items():
        with tempfile.TemporaryDirectory(dir='/dev/shm', prefix='pgpt-compiler-canary-') as temp:
            scope = Path(temp)
            main_file = scope / SOURCE
            main_file.parent.mkdir(parents=True)
            main_file.write_text(template, encoding='utf-8')
            saved = out / (case + '.java.txt')
            saved.write_bytes(main_file.read_bytes())
            for path, data in poms.items():
                (scope / path).write_bytes(data)
            home = scope / 'isolated-home'
            home.mkdir()
            environment = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': str(home),
                           'JAVA_HOME': str(JAVA), 'MAVEN_SKIP_RC': 'true',
                           'MAVEN_OPTS': f'-Duser.home={home} -Djava.io.tmpdir={scope}'}
            command = [str(MAVEN), '-N', '-B', '-o', '-ntp', '-Dstyle.color=never',
                       '-Dmaven.repo.local=' + str(CACHE), '-f', str(scope / CHILD / 'pom.xml'), 'compile']
            measured = subprocess.run(command, env=environment, cwd=scope, capture_output=True, timeout=60)
            raw = measured.stdout + measured.stderr
            prefixes = ('[INFO] --- ', '[INFO] Compiling ', '[INFO] BUILD ', '[WARNING] ', '[ERROR] ')
            warnings = [line.replace(temp, '<SCOPE>')
                        for line in raw.decode('utf-8', 'replace').splitlines()
                        if line.startswith(prefixes) and 'http' not in line]
            log = out / (case + '.txt')
            log.write_text('\n'.join(warnings) + '\n')
            physical = sorted(path.name for path in (scope / CHILD / 'target/classes').rglob('*.class'))
            outcomes[case] = dict(actualExit=measured.returncode,
                                  finishedAtUTC=datetime.now(timezone.utc).isoformat(),
                                  command=[str(part).replace(temp, '<SCOPE>') for part in command],
                                  rawSha256=hashlib.sha256(raw).hexdigest(), source=pin(saved),
                                  log=pin(log), resultingClassNames=physical)
    terminal = out / 'terminal.json'
    write(terminal, dict(**run_identity, begin=pin(begin), terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                         observedOutcomes=outcomes, actualProductionFilesCompiled=0,
                         productTests=0, vmsOrServicesStarted=0))
    print(pin(terminal))


if __name__ == '__main__':
    main()
