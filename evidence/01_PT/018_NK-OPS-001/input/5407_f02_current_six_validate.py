"""Run just original Maven validate with the current six Main source sets."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
JAVA = Path.cwd().parent / 'toolchain/jdk-25.0.4'
CACHE = Path.cwd().parent / 'toolchain/m2/repository'
MAVEN = Path('/home/mini/.m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn')


def sha(content):
    return hashlib.sha256(content).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def write(path, value):
    with path.open('x') as file:
        json.dump(value, file, indent=2, ensure_ascii=False)
        file.write('\n')


def git(*args):
    return subprocess.check_output(['git', *args])


def main():
    context = json.loads(next(PLAN.glob('1036_F02*')).read_bytes())
    start = context['values']
    assert all(pin(Path(ref['path'])) == ref for ref in start['oracleReferences'])
    core, source = start['productionCoreMain'], start['source']
    scope = {'protocol': 169, 'storage': 25, 'bootstrap': 88, 'api': 283, 'web': 262, 'batch': 200}
    roots = {module: f'src/schubert-nk-{module}' for module in scope}
    deps = ['pom.xml', 'program/characterization/pom.xml', *(root+'/pom.xml' for root in roots.values())]
    assert not git('diff', '--name-only', core, source, '--', *deps, *(r+'/src/main' for r in roots.values()))
    assert shutil.disk_usage('/dev/shm').free > 512 * 1024**2
    out = OPS/start['run']
    out.mkdir()
    with tempfile.TemporaryDirectory(dir='/dev/shm', prefix='pgpt-current-six-validate-') as tmp:
        sandbox = Path(tmp)
        files = list(deps)
        for module, root in roots.items():
            sources = [name for name in git('ls-tree', '-r', '--name-only', core, '--', root+'/src/main/java')
                       .decode().splitlines() if name.endswith('.java')]
            assert len(sources) == scope[module]
            files.extend(sources)
        inputs = {}
        for name in files:
            value = git('show', f'{core}:{name}')
            destination = sandbox/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(value)
            inputs[name] = sha(value)
        inventory = out/'main-inventory.json'
        write(inventory, inputs)
        home = sandbox/'isolated-home'
        home.mkdir()
        tmp_work = sandbox/'tmp'
        tmp_work.mkdir()
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': str(home), 'JAVA_HOME': str(JAVA),
               'MAVEN_SKIP_RC': 'true', 'MAVEN_OPTS': f'-Duser.home={home} -Djava.io.tmpdir={tmp_work}'}
        args = [str(MAVEN), '-o', '-B', '-ntp', '-Dstyle.color=never', f'-Dmaven.repo.local={CACHE}',
                '-pl', ','.join(roots.values()), '-am', 'validate']
        assert not list(sandbox.rglob('*.class')) and not list(sandbox.rglob('*/src/test'))
        begin = out/'begin.json'
        write(begin, dict(productionCore=core, source=source, startedAtUTC=datetime.now(timezone.utc).isoformat(),
                          groupStart=context['eventId'], command=args, mainCounts=scope, pomCount=len(deps),
                          java=pin(JAVA/'bin/java'), maven=pin(MAVEN), inventory=pin(inventory),
                          productTestSourcesCopied=0, artifactFilesBefore=0))
        child = subprocess.run(args, env=env, cwd=sandbox, capture_output=True, timeout=120)
        lines = (child.stdout + child.stderr).decode('utf-8', 'replace').splitlines()
        allowed = ('[INFO] --- ', '[INFO] Rule ', '[INFO] BUILD ', '[INFO] Reactor Summary',
                   '[INFO] Schubert NK', '[INFO] schubert-nk')
        steps = out/'maven-steps.txt'
        steps.write_text('\n'.join(line.replace(tmp, '<MAIN_ONLY>') for line in lines if line.startswith(allowed))+'\n')
        assert all(pin(sandbox/name)['sha256'] == digest for name, digest in inputs.items())
        terminal = out/'terminal.json'
        write(terminal, dict(source=source, productionCore=core, actualExit=child.returncode, begin=pin(begin),
                             terminalAtUTC=datetime.now(timezone.utc).isoformat(), steps=pin(steps),
                             rawStdoutSha256=sha(child.stdout), rawStderrSha256=sha(child.stderr),
                             productClassfilesAfter=len(list(sandbox.rglob('*.class'))),
                             testResultDirectories=len(list(sandbox.rglob('surefire-reports'))),
                             productJarsAfter=len(list(sandbox.rglob('*.jar'))), inputUnchanged=True,
                             actualExternalSystemActions=0, f02Accepted=False, f03Accepted=False))
        print(pin(terminal), child.returncode)
        return child.returncode


if __name__ == '__main__':
    raise SystemExit(main())
