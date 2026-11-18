"""Freeze the standalone Characterization CLI's exact sources and verify a small compile recipe."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tarfile

OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
SRC = 'program/characterization/src/main/java/'
RUN = 'PG40162-p020-filestore-artifact-prep-v1'
JAVA = Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java')
SDK = {
    'jackson-annotations-2.19.2.jar', 'jackson-core-2.19.2.jar', 'jackson-databind-2.19.2.jar',
    'jspecify-1.0.1.jar', 'playwright-1.55.0.jar',
}
COVERAGE_TOOLS = {'org.jacoco.agent-0.8.15-runtime.jar', 'org.jacoco.cli-0.8.15-nodeps.jar'}


def git(*args):
    return subprocess.check_output(['git', *args], timeout=25)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(Path(path).read_bytes()))


def main():
    start = json.loads(next(D.glob('636_P020*')).read_bytes())['values']
    pin, = start['oracleReferences']
    assert ref(pin['path']) == pin
    archive_begin = json.loads(Path(pin['path']).read_bytes())
    archive_unit_path = Path(pin['path']).with_name('manifest.json')
    archive_unit = json.loads(archive_unit_path.read_bytes())
    assert archive_begin['source'] == archive_unit['source']
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head == start['source']
    assert not git('diff', '--name-only', archive_begin['source'], head, '--', SRC)
    forks = {n: h for n, h in archive_begin['inputHashes'].items() if n.startswith(SRC)}
    assert len(forks) == 6
    tools = {n: p for n, p in archive_begin['tools'].items() if n in SDK | COVERAGE_TOOLS}
    assert set(tools) == SDK | COVERAGE_TOOLS
    assert all(ref(pin['path']) == pin for pin in tools.values())
    assert ref(JAVA) == archive_begin['jdk']
    assert ref(JAVA.with_name('javac')) == archive_begin['javaC']
    assert len(archive_unit['mainPhysical']) == 17

    t = Path('../pgpt-runs/PG379') / RUN.lower()
    t.mkdir(mode=0o700)
    out = OPS / RUN
    out.mkdir()
    files = []
    for name, expected in sorted(forks.items()):
        value = git('show', f'{head}:{name}')
        assert sha(value) == expected
        p = t / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(value)
        files.append(p)
    artifact = t / 'frozen-main-six.tar'
    with tarfile.open(artifact, 'x', format=tarfile.PAX_FORMAT) as tar:
        for p in files:
            entry = tar.gettarinfo(str(p), arcname=str(p.relative_to(t)))
            entry.mtime, entry.uid, entry.gid, entry.uname, entry.gname = 0, 0, 0, '', ''
            with p.open('rb') as stream:
                tar.addfile(entry, stream)
    with tarfile.open(artifact, 'r') as tar:
        assert set(tar.getnames()) == set(forks)
        for name, digest in forks.items():
            assert tar.getmember(name).isfile() and sha(tar.extractfile(name).read()) == digest
    output = t / 'physical'
    output.mkdir()
    compile_command = [str(JAVA.with_name('javac')), '--release', '25', '-g', '-Xlint:all', '-Werror',
                       '-proc:none', '-cp', os.pathsep.join(tools[n]['path'] for n in sorted(SDK)),
                       '-d', str(output), *map(str, files)]
    build = subprocess.run(compile_command, capture_output=True, timeout=40, check=False)
    assert build.returncode == 0 and not build.stdout and not build.stderr
    physical = {str(f.relative_to(output)): sha(f.read_bytes()) for f in output.rglob('*.class')}
    assert physical.keys() == archive_unit['mainPhysical'].keys()
    differences = sorted(n for n in physical if physical[n] != archive_unit['mainPhysical'][n])
    manifest = dict(actualExit=0, source=head, previousUnit=ref(archive_unit_path),
                    priorToolSource=archive_unit['source'], productionCore=start['productionCoreMain'],
                    archive=ref(artifact.resolve()), archiveBytes=artifact.stat().st_size,
                    sourceHashes=forks, exactLocalTools=tools, java=ref(JAVA), javac=ref(JAVA.with_name('javac')),
                    localCompileCommand=compile_command, localCompileExit=0, mainPhysical=physical,
                    byteDifferencesVs206=differences, priorCoverageJoinEligibleByClassBytes=not differences,
                    runStagedOnHaruka=False, backendActions=0, gateCliExecuted=False,
                    externalTransfer=False, productTests=0, formalIntake=0,
                    terminalAtUTC=datetime.now(timezone.utc).isoformat())
    f = out / 'manifest.json'
    f.write_text(json.dumps(manifest, indent=2) + '\n')
    print(ref(f), artifact.stat().st_size, len(physical), len(differences))


if __name__ == '__main__':
    main()
