"""Fresh strict API/reactor test-compile only; no Surefire/PT/service/VM operation."""
import json
import os
import subprocess
import tarfile
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg5540_snapshot_scratch_selected import utc

OLD = 'c51ea85db941ed76d73c4ec839b9e5c9d37165c0'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/config/ApiBrokerFactoryRemainderTest.java'


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed fixed source before static preflight')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()) != {TEST}:
        raise ValueError('only documented Test fixture warning corrected; all Main/poms unchanged')
    os.umask(0o077); out = W/'pg6153-api-test-compile-preflight-v1'; out.mkdir()
    archive = out/'source.tar'
    with archive.open('xb') as f:
        subprocess.run(['git', 'archive', source, 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization', 'tools/quality/static'], cwd=ROOT, stdout=f, check=True)
        f.flush(); os.fsync(f.fileno())
    snapshot = out/'source'; snapshot.mkdir()
    with tarfile.open(archive) as a: a.extractall(snapshot, filter='data')
    inputs = {p.relative_to(snapshot).as_posix(): sha(p) for p in snapshot.rglob('*') if p.is_file()}
    previous = W/'pg6150-api-factory-close-selected-v1/source'
    main_paths = list(snapshot.glob('src/*/src/main/java/**/*.java'))
    if len(main_paths) != 851 or any(sha(p) != sha(previous/p.relative_to(snapshot)) for p in main_paths):
        raise ValueError('all851 Main identical to original compiled Main; no alternate source success')
    env = {k:v for k,v in os.environ.items() if k not in ('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    env.update(JAVA_HOME=str(TC/'jdk-25.0.4'), PATH=str(TC/'jdk-25.0.4/bin')+os.pathsep+os.environ['PATH'], MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir='+str(out))
    command = [str(TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'), '-B', '-o', '-ntp',
        '-Dmaven.repo.local='+str(TC/'m2/repository'), '-pl', 'src/schubert-nk-api', '-am', 'test-compile']
    started = utc()
    with (out/'begin.safe.json').open('x') as f:
        json.dump(dict(source=source, archiveSha256=sha(archive), command=command, startedUTC=started, testsPlanned=0), f, sort_keys=True)
    with (out/'compile.private.log').open('xb') as log:
        child = subprocess.Popen(command, cwd=snapshot, env=env, stdout=log, stderr=log)
        from pathlib import Path
        proc = Path('/proc')/str(child.pid)
        with (out/'owner.safe.json').open('x') as f:
            json.dump(dict(pid=child.pid,ticks=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])),f)
        actual = child.wait(); log.flush(); os.fsync(log.fileno())
    fixed = all(sha(snapshot/p)==h for p,h in inputs.items())
    reports = list(snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'))
    jacoco = list(snapshot.glob('src/*/target/jacoco.exec'))
    code = actual if actual else 0 if fixed and not reports and not jacoco else 1
    value = dict(actualExit=code, mavenActualExit=actual, source=source, archiveSha256=sha(archive),
        startedUTC=started, completedUTC=utc(), command=command, sourceFixed=fixed,
        compiledModules=['protocol','storage','bootstrap','api'] if actual==0 else [],
        all851MainUnchanged=True, testsExecuted=0, surefireXmlCount=len(reports), jacocoExecCount=len(jacoco),
        coverageMeasured=False, formalAccepted=False, nativeQualified=False, ptAlternativeCompleted=0,
        originalCompilerArgumentCaptureAvailable=False,
        compileConfiguration='existing unchanged module -Xlint:all/-Werror and inherited Main type/null compiler; lifecycle ends at test-compile')
    for target in (out, BASE/'PG6153-api-test-compile-preflight-v1'):
        if target != out: target.mkdir()
        with (target/'manifest.json').open('x') as f:
            json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(value, ensure_ascii=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
