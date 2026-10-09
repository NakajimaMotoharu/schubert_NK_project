"""SSC234 fixed candidate selected host regression; no VM operations or formal acceptance."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

T = Path(__file__).resolve().parents[4]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
D = W / 'pg743-closing-selected-v1'
TESTS = {
    'bootstrap': ['FixedNativeCoverageTerminalTest', 'FixedNativeCoverageCheckpointTest',
                  'FixedNativeCoverageProfileTest', 'NativeCoverageExportTest', 'NativeCoveragePrivateFileTest'],
    'api': ['BootstrapClosingBoundaryTest', 'BootstrapEntryBoundaryTest', 'BootstrapAdminMainTest',
            'InspectorEntryBoundaryTest', 'InspectorLauncherTest', 'InspectorApplicationTest', 'InspectorProcessTest'],
}


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=T) == b''
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip()
    paths = subprocess.check_output(['git', 'ls-files', 'src', 'tools', 'pom.xml'], cwd=T, text=True).splitlines()
    hashes = {p: hashlib.sha256((T / p).read_bytes()).hexdigest() for p in paths}
    D.mkdir(mode=0o700)
    prior = D / 'preexisting'; prior.mkdir(mode=0o700)
    for module, tests in TESTS.items():
        target = T / 'src' / ('schubert-nk-' + module) / 'target'
        for name in ('jacoco.exec', 'spotbugsXml.xml'):
            p = target / name
            if p.exists(): p.rename(prior / (module + '-' + name))
        for p in (target / 'surefire-reports').glob('TEST-*.xml'):
            if p.name.removesuffix('.xml').split('.')[-1] in tests:
                p.rename(prior / (module + '-' + p.name))
    env = dict(os.environ)
    env['JAVA_HOME'] = '/home/mini/codex/project1/work/toolchain/jdk-25.0.4'
    env['PATH'] = env['JAVA_HOME'] + '/bin:' + env['PATH']
    command = ['./mvnw', '-o', '--no-transfer-progress', '-Dstyle.color=never', '-Djansi.force=false',
               '-Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository',
               '-pl', 'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',
               'spotless:check', 'test-compile', 'test', 'spotbugs:check', 'jacoco:report', 'jar:jar',
               '-Dtest=' + ','.join(n for names in TESTS.values() for n in names),
               '-Dsurefire.failIfNoSpecifiedTests=false']
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (D / 'build.private.log').open('xb') as out:
        result = subprocess.run(command, cwd=T, env=env, stdout=out, stderr=out)
        out.flush(); os.fsync(out.fileno())
    with (D / 'exit').open('x') as out: out.write(str(result.returncode) + '\n')
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip() == source
    assert hashes == {p: hashlib.sha256((T / p).read_bytes()).hexdigest() for p in paths}
    files = {}
    for module in TESTS:
        target = T / 'src' / ('schubert-nk-' + module) / 'target'
        root = D / module; root.mkdir(mode=0o700)
        for name in ('jacoco.exec', 'spotbugsXml.xml', 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'):
            p = target / name
            if p.exists(): shutil.copyfile(p, root / name)
        xml = target / 'site/jacoco/jacoco.xml'
        if xml.exists(): shutil.copyfile(xml, root / 'jacoco.xml')
        for p in (target / 'surefire-reports').glob('TEST-*.xml'):
            if p.name.removesuffix('.xml').split('.')[-1] in TESTS[module]: shutil.copyfile(p, root / p.name)
        for p in root.iterdir(): files[str(p.relative_to(D))] = hashlib.sha256(p.read_bytes()).hexdigest()
    record = {'actualExit':result.returncode, 'source':source, 'run':'PG743-closing-selected-v1',
              'startedUTC':start, 'endedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'command':command, 'files':files, 'selectedTests':TESTS,
              'sourceHashes':hashes, 'installedVmSource':'1ec19782a1afe22d1de75b05f4cd12b8a8a8a172',
              'candidateDeployed':False, 'formalAccepted':False, 'wholeRegressionPending':True}
    with (D / 'run.safe.json').open('x') as out: json.dump(record, out, sort_keys=True)
    print(json.dumps({'actualExit':result.returncode, 'source':source, 'formalAccepted':False}))
    raise SystemExit(result.returncode)


if __name__ == '__main__': main()
