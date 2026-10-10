"""New-only operator compile and independent inherited fault tests against PG1068."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1134_failed_recovery_sources import files, SOURCE

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J = Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
OUT = W / 'pg1134-issued-api-tools-v1'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    with path.open('xb') as f:
        os.fchmod(f.fileno(), 0o400); f.write(data); f.flush(); os.fsync(f.fileno())


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT): raise ValueError('clean fixed source required')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    start = datetime.datetime.now(datetime.timezone.utc).isoformat(); OUT.mkdir(mode=0o700)
    write(OUT / 'begin.safe.json', json.dumps({'operatorSource': head, 'startedUTC': start, 'formalAccepted': False}).encode())
    previous = json.loads((W / 'pg983-frozen-v3.safe.json').read_bytes())
    if previous['actualExit'] != 0: raise ValueError('qualified immutable helper input refused')
    for name, digest in previous['fileHashes'].items():
        p = W / 'pg983-bootstrap-tools-v3' / name
        if sha(p) != digest: raise ValueError('immutable helper hash refused')
        if name.endswith('.class'): write(OUT / name, p.read_bytes())
    for name, text in files().items():
        if name.endswith('.py'): ast.parse(text)
        write(OUT / name, text.encode())
    release = W / 'pg1068-release-v1'
    cp = ':'.join(map(str, [OUT, release / 'api/api.jar', release / 'operations/batch.jar',
                          release / 'api/lib/*', release / 'operations/lib/*']))
    repo = Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp += ':' + ':'.join(str(repo / x) for x in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar',
        'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar', 'com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    java = [str(p) for p in OUT.glob('Pg1134*.java')]
    commands = [('python-oracle', ['python3', '-B', '-m', 'unittest', 'discover', '-s', str(HERE), '-p', 'pg113[34]*test.py', '-v']),
                ('compile', [str(J / 'javac'), '-Xlint:all', '-Werror', '-cp', cp, '-d', str(OUT), *sorted(java)]),
                ('single-intent-oracle', [str(J / 'java'), '--enable-native-access=ALL-UNNAMED', '-cp', cp, 'dev.codex.schubert.nk.batch.file.Pg1134SingleApiIntentTest']),
                ('issued-oracle', [str(J / 'java'), '--enable-native-access=ALL-UNNAMED', '-cp', cp, 'dev.codex.schubert.nk.batch.file.Pg1134IssuedApiRecoveryTest'])]
    phases = []
    for phase, command in commands:
        log = OUT / (phase + '.private.log')
        with log.open('xb') as f:
            p = subprocess.run(command, cwd=ROOT, stdout=f, stderr=f); f.flush(); os.fsync(f.fileno())
        write(OUT / (phase + '.exit'), (str(p.returncode) + '\n').encode())
        phases.append(dict(phase=phase, command=command, actualExit=p.returncode, logSha256=sha(log)))
        if p.returncode: break
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT) or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() != head:
        raise ValueError('source moved during fixed build')
    result = dict(run='PG1135-failed-recovery-compile-v1', actualExit=phases[-1]['actualExit'], operatorSource=head,
                  productionSource=SOURCE, phases=phases, startedUTC=start,
                  completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), formalAccepted=False,
                  fileHashes={str(p.relative_to(OUT)): sha(p) for p in OUT.rglob('*') if p.is_file()})
    write(W / 'pg1135-failed-recovery-frozen-v1.safe.json', json.dumps(result, sort_keys=True).encode())
    print(json.dumps({k: v for k, v in result.items() if k != 'fileHashes'})); return result['actualExit']


if __name__ == '__main__': raise SystemExit(main())
