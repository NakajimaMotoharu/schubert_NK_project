"""WBS-F03/2-2 and F02/SYS-002: build the four admitted Main source sets."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path.cwd()
EVIDENCE = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PMO = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
MODULES = ('protocol', 'storage', 'bootstrap', 'batch')
ALL_MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
POMS = ['pom.xml', 'program/characterization/pom.xml'] + [
    f'src/schubert-nk-{module}/pom.xml' for module in ALL_MODULES
]
PRIOR = EVIDENCE / 'PG39434-service-jdbc-four-module-build-v1/compile/manifest.json'
DENIED = {
    'TemporaryInfrastructureException', 'FingerprintKeyRing', 'ResponseSnapshotCodec',
    'WebStartupException', 'RootFailedStartRecoveryTest', 'RootFailedStartPairRecoveryTest',
    'SnapshotKeyCloseWitness', 'pg9892_snapshot_key_close_witness',
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_git(ref, path):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'])


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def main():
    start = json.loads((PMO / '451_P00405接続確認の生分岐是正開始.json').read_text())
    core = subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
    assert subprocess.run(['git','merge-base','--is-ancestor',start['baseCore'], core]).returncode == 0
    previous = json.loads(PRIOR.read_text())
    baseline = previous['sourceCore']
    source_lists = {
        module: sorted(Path(f'src/schubert-nk-{module}/src/main/java').rglob('*.java'))
        for module in MODULES
    }
    assert {k: len(v) for k, v in source_lists.items()} == {
        'protocol': 169, 'storage': 25, 'bootstrap': 88, 'batch': 200
    }
    main_paths = [p for paths in source_lists.values() for p in paths]
    assert all(p.stem not in DENIED for p in main_paths)
    paths = [Path(p) for p in POMS] + main_paths
    inputs = {p: p.read_bytes() for p in paths}
    assert all(data == read_git(core, path) for path, data in inputs.items())
    previous_pins = previous['sourceInputs']
    pins = {str(p): hashlib.sha256(data).hexdigest() for p, data in inputs.items()}
    new = {name for name in pins if name not in previous_pins}
    assert not new
    assert previous_pins.keys() <= pins.keys()
    changed = sorted(k for k, h in pins.items() if previous_pins.get(k) != h)
    assert {Path(p).name for p in changed} == {
        'ServiceDatabaseAdmission.java', 'ServiceDatabaseSource.java',
    }
    work = ROOT.parent / 'pgpt-runs/PG379/pg39458-admission-single-cleanup-four-build-v1'
    output = EVIDENCE / 'PG39458-admission-single-cleanup-four-build-v1/compile'
    assert not work.exists() and not output.exists()
    free = shutil.disk_usage(ROOT).free
    assert free >= 1024**3
    work.mkdir()
    output.mkdir(parents=True)
    for path, raw in inputs.items():
        target = work / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    toolchain = ROOT.parent / 'toolchain'
    jdk = toolchain / 'jdk-25.0.4'
    maven = toolchain / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
    args = [
        str(maven), '-o', '-B', '-ntp', f'-Dmaven.repo.local={toolchain}/m2/repository',
        '-pl', ','.join(f'src/schubert-nk-{module}' for module in MODULES), '-am', 'compile',
    ]
    env = {
        'JAVA_HOME': str(jdk), 'PATH': f'{jdk}/bin:/usr/bin:/bin',
        'HOME': os.environ['HOME'], 'LANG': 'C.UTF-8',
    }
    begin = {
        'run': 'PG39458-WBS66-ADMISSION-SINGLE-CLEANUP-FOUR-MAIN',
        'startEvent': start['eventId'], 'sourceCore': core, 'baselineSource': baseline,
        'baselineManifestSha256': digest(PRIOR), 'sourceInputs': pins, 'changedSources': changed,
        'mainCounts': {m: len(v) for m, v in source_lists.items()}, 'freeBytes': free,
        'startedAtUTC': utc(), 'command': args, 'cwd': str(work),
        'tools': {'javaSha256': digest(jdk / 'bin/java'), 'mavenLauncherSha256': digest(maven)},
    }
    (output / 'begin.safe.json').write_text(json.dumps(begin, indent=2) + '\n')
    print(f"Started {begin['run']} at {core}", flush=True)
    with (output / 'maven.stdout.log').open('xb') as stdout, (output / 'maven.stderr.log').open('xb') as stderr:
        try:
            code = subprocess.run(args, cwd=work, env=env, stdout=stdout, stderr=stderr, timeout=180).returncode
        except subprocess.TimeoutExpired:
            code = 124
    (output / 'maven-process-exit.safe.json').write_text(
        json.dumps({'actualExit': code, 'observedAtUTC': utc()}, indent=2) + '\n'
    )
    classes = {}
    for module in MODULES:
        directory = work / f'src/schubert-nk-{module}/target/classes'
        classes[module] = {
            str(p.relative_to(directory)): digest(p) for p in sorted(directory.rglob('*.class'))
        }
    deltas = {}
    for module, new in classes.items():
        old = previous['physicalClassHashes'][module]
        deltas[module] = {
            'added': sorted(new.keys() - old.keys()), 'removed': sorted(old.keys() - new.keys()),
            'changed': sorted(k for k in new.keys() & old.keys() if new[k] != old[k]),
        }
    verified = all(digest(p) == digest(work / p) == h for p, h in pins.items())
    assert not list(work.rglob('surefire-reports'))
    result = dict(begin, terminalAtUTC=utc(), actualExit=code, inputHashesReverified=verified,
                  physicalClassHashes=classes, deltas=deltas, productTestsExecuted=0,
                  logs={n: digest(output / n) for n in ('maven.stdout.log', 'maven.stderr.log')})
    (output / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'exit': code, 'counts': {m: len(v) for m, v in classes.items()},
                      'deltas': deltas, 'inputHashesReverified': verified}))
    return code or (0 if verified else 1)


if __name__ == '__main__':
    sys.exit(main())
