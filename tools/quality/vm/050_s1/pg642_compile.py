"""Build a new-only private stop tool after genuine PG640; no VM operations."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg642_stop_binding import generate

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R.parents[3]) == b''
    assert (W/'pg640-completed-readonly-v1.exit').read_bytes() == b'0\n'
    proof = json.loads((W/'pg640-completed-readonly-v1.safe.json').read_bytes())
    files = generate(proof)
    target = W/'pg642-native-tools-v1'
    target.mkdir(mode=0o700)
    for name, raw in files.items():
        with (target/name).open('x') as f:
            os.fchmod(f.fileno(), 0o600); f.write(raw); f.flush(); os.fsync(f.fileno())
    repo = Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    paths = [W/'pg498-pending-tools-v3', W/'pg464-code-tools-v2', W/'pg490-migration-tools-v4',
             W/'pg481-pending-tools-v2', W/'pg456-tools-v7']
    candidate = W/'pg630-retention-factory-six-host-v1'
    for module in ('api', 'batch', 'bootstrap', 'storage', 'protocol'):
        paths.append(candidate/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'))
    paths.extend((W/'pg631-release-v1/api/lib/*', W/'pg631-release-v1/operations/lib/*',
                  repo/'com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar',
                  repo/'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar',
                  repo/'com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    cp = ':'.join(str(p) for p in paths)
    java = Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
    with (W/'pg642-native-compile-v1.private.log').open('xb') as f:
        result = subprocess.run([str(java/'javac'), '-Xlint:all', '-Werror', '-cp', cp, '-d', str(target),
                                 str(target/'Pg642NativeStop.java'), str(target/'Pg642NativeArgumentTest.java')], stdout=f, stderr=f)
    assert result.returncode == 0
    with (W/'pg642-argument-oracle-v1.private.log').open('xb') as f:
        result = subprocess.run([str(java/'java'), '-cp', str(target)+':'+cp, 'Pg642NativeArgumentTest'], stdout=f, stderr=f)
    assert result.returncode == 0
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}
    with (W/'pg642-native-build-v1.safe.json').open('x') as f:
        json.dump({'files': manifest, 'actualCompileExit': 0, 'argumentExit': 0,
                   'productionSource': proof['productionSource'], 'genuineParentBeforeSha256': proof['beforeSha256'],
                   'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                   'vmActions0': True, 'productionPT0': True}, f, sort_keys=True)
    print(json.dumps({'compileExit': 0, 'argumentExit': 0, 'files': len(manifest), 'vmActions0': True}))


if __name__ == '__main__': main()
