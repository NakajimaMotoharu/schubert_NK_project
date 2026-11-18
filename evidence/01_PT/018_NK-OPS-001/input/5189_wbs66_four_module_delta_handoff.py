"""Reconcile the current four-module bytecode edges and November 25 handoff."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

B = Path('evidence/01_PT/018_NK-OPS-001')
E = B / 'evidence'
D = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
OUT = E / 'PG39616-wbs66-four-module-edge-and-handoff-v1'
MODULES = ('protocol', 'storage', 'bootstrap', 'batch')
ALLOWED = {'bootstrap->storage', 'batch->storage', 'batch->bootstrap'}
SOURCE_ROOT = 'dev.codex.schubert.nk.'
PROTECTED = ('TemporaryInfrastructureException', 'FingerprintKeyRing', 'ResponseSnapshotCodec',
             'WebStartupException', 'RootFailedStartRecovery', 'RootFailedStartPairRecovery',
             'SnapshotKeyCloseWitness')
JDEPS_LINE = re.compile(r'^\s+(\S+)\s+->\s+(\S+)\s+(.+?)\s*$')
EXACT_CHANGED_PARENTS = {
    'ServiceCredentialId', 'ServiceCredentialLocation', 'StorageIoException',
    'JdbcFailureGraph', 'ApiNonSecretConfig', 'JdbcAdmissionFailures', 'SchemaHistoryAdmission',
    'ServiceDatabaseAdmission', 'ServiceDatabaseSource', 'WebNonSecretConfig',
    'BackupCommitService', 'LogCleanupService', 'StepCleanupService', 'BackupManifestCodec',
    'BackupStepRepository', 'CleanupRepository', 'CleanupStepRepository',
    'JdbcResourceFailures', 'MorningSqlFailures', 'RunReferenceRepository',
}


def git(*args):
    return subprocess.check_output(['git', *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(p):
    return {'path': str(p), 'sha256': sha(p.read_bytes())}


def matching_path(pattern):
    [result] = E.glob(pattern)
    return result


def load(path):
    return json.loads(path.read_bytes())


def write(path, value):
    with path.open('x', encoding='utf-8') as out:
        out.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def revalidate_reference(receipt):
    path = Path(receipt['path'])
    assert ref(path) == receipt
    return load(path)


def tree(source, paths):
    output = git('ls-tree', '-r', '-z', source, '--', *paths)
    blobs = {}
    for row in filter(None, output.split(b'\0')):
        item, path = row.split(b'\t', 1)
        mode, kind, digest = item.decode().split(' ')
        assert kind == 'blob' and mode == '100644'
        blobs[path.decode()] = digest
    return blobs


def class_owners(by_module):
    return {path.removesuffix('.class').replace('/', '.'): module
            for module, rows in by_module.items() for path in rows}


def analyze(lines, owners):
    permissions = Counter()
    internal = set()
    missing_internal = set()
    external_missing = set()
    unknown_origins = set()
    for origin, target, artifact in lines:
        if origin not in owners:
            unknown_origins.add(origin)
        if target in owners:
            internal.add((origin, target))
            if owners[origin] != owners[target]:
                permissions[f'{owners[origin]}->{owners[target]}'] += 1
        elif target.startswith(SOURCE_ROOT):
            missing_internal.add((origin, target))
        elif artifact == 'not found':
            external_missing.add((origin, target))
    assert not unknown_origins
    return dict(total=len(lines), internal=len(internal), edges=dict(sorted(permissions.items())),
                internalUnresolved=sorted(missing_internal), externalUnresolved=len(external_missing))


def edges(text):
    return [parsed.groups() for line in text.splitlines() if (parsed := JDEPS_LINE.fullmatch(line))]


def posture(start):
    values = start['values']
    source, core = values['source'], values['productionCoreMain']
    assert git('rev-parse', 'HEAD').decode().strip() == source
    assert git('rev-parse', 'origin/dev-foundation').decode().strip() == source
    build_file = matching_path('PG39462*/compile/manifest.json')
    build = load(build_file)
    assert build['actualExit'] == build['productTestsExecuted'] == 0 and build['inputHashesReverified']
    for name, expected in build['logs'].items():
        archived = build_file.parent / (name + '.gz')
        assert sha(gzip.decompress(archived.read_bytes())) == expected
    assert load(build_file.parent / 'maven-process-exit.safe.json')['actualExit'] == 0
    inputs = build['sourceInputs']
    folders = [f'src/schubert-nk-{m}/src/main/java' for m in MODULES]
    poms = [path for path in inputs if path.endswith('/pom.xml') or path == 'pom.xml']
    targets = [*poms, *folders]
    build_tree = tree(build['sourceCore'], targets)
    assert set(build_tree) == set(inputs) and len(build_tree) == 490 and len(poms) == 8
    assert build_tree == tree(core, targets) == tree(source, targets)
    assert sum(build['mainCounts'].values()) == 482
    return values, build_file, build, poms


def check_physical(build):
    historical_file = matching_path('PG38182*/manifest.json')
    old = {module: data['classHashes'] for module, data in load(historical_file)['rows'].items()}
    new = build['physicalClassHashes']
    assert list(old) == list(new) == list(MODULES)
    old_owner, current_owner = map(class_owners, (old, new))
    assert len(old_owner) == 1102 and len(current_owner) == 1101
    old_edges = matching_path('PG38202*/manifest.json')
    prior = load(old_edges)
    zipped = old_edges.parent / 'jdeps.stdout.gz'
    assert sha(zipped.read_bytes()) == prior['evidence'][zipped.name]
    original = gzip.decompress(zipped.read_bytes())
    assert sha(original) == prior['rawOutputSHA256']
    original_rows = edges(original.decode())
    before = analyze(original_rows, old_owner)
    assert before['total'] == prior['totalDependencyReferences']
    assert before['internal'] == prior['internalDependencyReferences']
    assert before['externalUnresolved'] == prior['externalUnavailableReferences']
    assert before['edges'] == prior['crossModuleDependencyReferences']
    changed, gone = [], set(old_owner) - set(current_owner)
    consumed = {}
    work = Path(build['cwd'])
    assert work.parent == Path('../pgpt-runs/PG379').resolve()
    for module, rows in new.items():
        for filename, key in rows.items():
            if old[module].get(filename) == key:
                continue
            assert Path(filename).stem.split('$', 1)[0] in EXACT_CHANGED_PARENTS
            assert not any(guard in filename for guard in PROTECTED)
            path = work / f'src/schubert-nk-{module}/target/classes' / filename
            assert path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == key
            changed.append(str(path))
            consumed[filename.removesuffix('.class').replace('/', '.')] = key
    assert len(changed) == 27 and {x.rsplit('.', 1)[-1] for x in gone} == {
        'ServiceCredentialId$1', 'ServiceDatabaseAdmission$1'}
    launcher = Path('../toolchain/jdk-25.0.4/bin/jdeps').resolve()
    java = launcher.with_name('java')
    assert sha(java.read_bytes()) == build['tools']['javaSha256']
    command = [str(launcher), '-verbose:class', '-filter:none', '--ignore-missing-deps', *changed]
    start = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, capture_output=True, timeout=90)
    end = datetime.now(timezone.utc).isoformat()
    with (OUT / 'jdeps-delta.stdout.gz').open('xb') as out:
        out.write(gzip.compress(result.stdout, mtime=0))
    write(OUT / 'jdeps-delta-process.json', dict(command=command, startedAtUTC=start, terminalAtUTC=end,
                                                 exit=result.returncode, stdoutSha256=sha(result.stdout),
                                                 stderrSha256=sha(result.stderr), jdepsSha256=sha(launcher.read_bytes())))
    assert result.returncode == 0 and not result.stderr
    update = edges(result.stdout.decode())
    assert set(issuer for issuer, _, _ in update) == set(consumed)
    combined_rows = [(a, b, c) for a, b, c in original_rows if a not in gone and a not in consumed] + update
    current = analyze(combined_rows, current_owner)
    assert set(current['edges']) == ALLOWED and not current['internalUnresolved']
    assert any(a.endswith('.StorageIoException') and b == 'java.sql.SQLException' for a, b, _ in combined_rows)
    assert not any(a in gone or b in gone for a, b, _ in combined_rows)
    return dict(historicalBaseline=ref(old_edges), historicalClassIndex=ref(historical_file),
                actualPhysicalCount={m: len(v) for m, v in new.items()}, identicalByteReuse=1074,
                changedAndNewPhysical=dict(sorted(consumed.items())), removed=sorted(gone),
                rawAnalysis=ref(OUT / 'jdeps-delta.stdout.gz'), actualCommand=ref(OUT / 'jdeps-delta-process.json'),
                current=current, before=before, externalFullResolution=False, storageSqlEdgeStillOpen=True,
                protectedClassesRead=0, fullArchitectureGate=False, newAppExecutions=0)


def declared_graph(core, poms):
    qualified = matching_path('PG38186*/manifest.json')
    source = load(qualified)
    original = revalidate_reference(source['producer'])
    current = {p: sha(git('show', core + ':' + p)) for p in poms}
    assert all(original['inputHashes'][p] == k for p, k in current.items())
    assert source['mavenNumericExit'] == 0 and source['productClassfilesGenerated'] == 0
    assert source['declaredProductionAndTestGraph']['web']['testEdges'] == [['api', 'jar'], ['bootstrap', 'test-jar']]
    assert not any('api' in n['productionEdges'] or 'web' in n['productionEdges']
                   for n in source['declaredProductionAndTestGraph'].values())
    return dict(pomHashes=current, qualifiedOriginal=ref(qualified), productionAndTestEdges=source['declaredProductionAndTestGraph'],
                reportUse='EXACT_POM_INPUT_ONLY', newPackageOrReactorExecution=0)


def reconcile_static(values):
    previous = matching_path('PG39454*/manifest.json')
    old = load(previous)
    core, head = values['productionCoreMain'], values['source']
    checks = [
        matching_path('PG39463*/manifest.json'),
        *[Path(load(matching_path(f'{k}*/manifest.json'))['proofs']['post']['path'])
          for k in ('PG39500', 'PG39518', 'PG39536', 'PG39578', 'PG39606')]
    ]
    for k, file in zip(('PG39500', 'PG39518', 'PG39536', 'PG39578', 'PG39606'), checks[1:]):
        assert ref(file) == load(matching_path(f'{k}*/manifest.json'))['proofs']['post']
    pins = {path: (key, ref(file)) for file in checks for path, key in load(file)['inputHashes'].items()}
    partitions = {'main': [], 'test': []}
    for kind in partitions:
        items = git('diff', '--name-only', '-z', old['source'], head, '--',
                    f':(glob)src/*/src/{kind}/java/**/*.java').decode().rstrip('\0').split('\0')
        for path in sorted(items):
            assert not any(guard in path for guard in PROTECTED)
            pin, proof = pins[path]
            observed = sha(git('show', head + ':' + path))
            assert observed == pin
            if kind == 'main':
                assert observed == sha(git('show', core + ':' + path))
            partitions[kind].append(dict(sourcePath=path, sha256=observed, exactLocalEvidence=proof))
    assert len(partitions['main']) == 4 and len(partitions['test']) == 7
    assert old['f03']['currentMainEligibleConfirmed'] == 1023 and old['f03']['currentTestEligibleConfirmed'] == 1101
    return dict(previousHandoff=ref(previous), historicalSSC447=old['ssc447Historical'],
                C02=old['c02'], F04=old['f04'], criteriaByRole=old['criteriaByRole'],
                mainEligibility={'total': 1027, 'evidence': 1023, 'held': 4},
                testEligibility={'total': 1133, 'evidence': 1101, 'held': 32},
                exactCurrentStaticInputChanges=partitions, originalWholeSixStillOpen=True)


def main():
    start = load(next(D.glob('467_*')))
    values, build_file, build, poms = posture(start)
    declarations = declared_graph(values['productionCoreMain'], poms)
    exact = reconcile_static(values)
    for path, expected in exact['C02']['verifiedTemplateHashes'].items():
        assert sha(git('show', values['source'] + ':' + path)) == expected
    physical = check_physical(build)
    result = dict(actualExit=0, id='W66-HANDOFF-20261118-07', startEvent=start['eventId'],
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(), source=values['productionCoreMain'],
                  inspectionHead=values['source'], buildReceipt=ref(build_file), originalBuildSource=build['sourceCore'],
                  currentFourEligibleSourceEquality={'all490': True, 'main': 482, 'poms': 8},
                  observedNewBuilds=0, historicalBuildActualExit=build['actualExit'],
                  f02PhysicalEdges=physical, sixPomDeclaration=declarations, fourRoleHandoff=exact,
                  currentWbsCriteriaAccepted=0, actualNewTests=0, actualExternalOperations=0,
                  newAcceptance=0, formalAcceptance=17, formalDenominator=190, officialPt=1964, officialScope=53,
                  externalAcknowledgements=0, effortCompletionRate=None, verifier=ref(Path(__file__).relative_to(Path.cwd())))
    write(OUT / 'manifest.json', result)
    print(ref(OUT / 'manifest.json'))
    print(physical['actualPhysicalCount'], physical['current'])


if __name__ == '__main__':
    main()
