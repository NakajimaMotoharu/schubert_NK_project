"""Freeze the 211-case comparison candidate without contacting or starting a host."""

from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
from tempfile import TemporaryDirectory


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
FILESTORE = 'dev.codex.schubert.characterization.GateOwnedFileStoreContract'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def folder_bytes(root):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob('*.class')}


def checksums(files):
    return {name: sha(data) for name, data in sorted(files.items())}


def main():
    start = json.loads(next(PLAN.glob('1030_P020*')).read_bytes())
    values = start['values']
    refs = values['oracleReferences']
    assert len(refs) == 6 and all(pin(Path(item['path'])) == item for item in refs)
    unit, post, old, older = (json.loads(Path(ref['path']).read_bytes()) for ref in refs[1:5])
    entry = next(OPS.glob('PG40658-*/begin.json'))
    begin = json.loads(entry.read_bytes())
    assert unit['source'] == begin['source'] == post['source'] and unit['expected'] == post['fullOfflineCases'] == 210
    assert unit['productionCore'] == post['productionCore'] == values['productionCoreMain']
    assert old['expectedTests'] == older['tests'] == 209 and old['previousToolSource'] == older['exactToolSource']
    assert all(result['actualExit'] == 0 for result in unit['stages'].values())
    assert all(pin(Path(ref['path'])) == ref for ref in [begin['java'], begin['javac'], *begin['tools'].values()])

    source_files = {}
    snapshot = Path(begin['snapshot'])
    for name, digest in begin['inputHashes'].items():
        assert name == 'pom.xml' or name.startswith('program/characterization/')
        body = (snapshot / name).read_bytes()
        assert digest == sha(body)
        assert body == subprocess.check_output(['git', 'show', f'{unit["source"]}:{name}'])
        source_files['snapshot/' + name] = body
    physical = folder_bytes(Path(unit['classesDir']))
    assert len(physical) == 17 and checksums(physical) == unit['mainPhysical']
    compile_test = unit['stages']['test']['command']
    original_classes = Path(compile_test[compile_test.index('-d') + 1])
    fixture = Path(refs[-1]['path']).resolve()
    with TemporaryDirectory(dir='/dev/shm', prefix='pgpt-211-inputs-') as temp:
        target = Path(temp) / 'tests'
        repl = [str(target) if arg == str(original_classes) else arg for arg in compile_test]
        subprocess.run(repl, check=True, capture_output=True, timeout=90)
        tests = folder_bytes(target)
        assert tests == folder_bytes(original_classes)
        combined = Path(temp) / 'filestore'
        end_cp = compile_test.index('-cp') + 2
        subprocess.run([*compile_test[:end_cp], '-proc:none', '-d', str(combined), str(fixture)],
                       check=True, capture_output=True, timeout=45)
        file_store = folder_bytes(combined)
    class_name = FILESTORE.replace('.', '/') + '.class'
    assert set(file_store) == {class_name} and class_name not in tests
    assert sha(file_store[class_name]) == old['spec']['tests'][class_name]
    tests.update(file_store)
    command = unit['stages']['unit']['command']
    selectors = [command[index + 1] for index, arg in enumerate(command) if arg == '--select-class']
    assert len(set(selectors)) == 20 and selectors + [FILESTORE] == old['spec']['selectors']
    sdk = {'sdk/' + name: Path(ref['path']).read_bytes() for name, ref in begin['tools'].items()}
    files = {**source_files, **{'classes/' + name: body for name, body in physical.items()},
             **{'testclasses/' + name: body for name, body in tests.items()}, **sdk}
    assert len(tests) == 37 and set(files) == set(old['spec']['files'])
    inventory = checksums(files)
    delta = sorted(name for name, digest in inventory.items() if old['spec']['files'][name] != digest)
    assert len(delta) >= 3 and all('ArtifactComparator' in name for name in delta)

    memory = io.BytesIO()
    with tarfile.open(fileobj=memory, mode='w:', format=tarfile.PAX_FORMAT) as archive:
        for name, body in sorted(files.items()):
            member = tarfile.TarInfo(name)
            member.size, member.mode = len(body), 0o600
            archive.addfile(member, io.BytesIO(body))
    raw = memory.getvalue()
    payload = gzip.compress(raw, mtime=0)
    assert 0 < len(payload) < 7 * 1024**2 and len(raw) < 12 * 1024**2
    target = Path('../pgpt-runs/PG379').resolve() / values['run'].lower()
    target.mkdir(mode=0o700)
    handoff = target / 'verified-characterization.tar.gz'
    with handoff.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(payload)
    host_input = dict(capsuleSha256=sha(payload), size=len(payload), rawTarSha256=sha(raw),
                      rawTarSize=len(raw), files=inventory, physical=checksums(physical),
                      tests=checksums(tests), selectors=selectors + [FILESTORE],
                      session='PG40664-A02-CHARACTERIZATION-211-FILESTORE',
                      java=old['spec']['java'], javac=old['spec']['javac'], expectedTests=211)
    with (target/'host-input.json').open('x') as stream:
        os.fchmod(stream.fileno(), 0o600)
        json.dump(host_input, stream, indent=2)
        stream.write('\n')
    public = OPS / values['run']
    public.mkdir()
    manifest = public / 'manifest.json'
    with manifest.open('x') as stream:
        json.dump(dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                       source=unit['source'], productionCore=unit['productionCore'],
                       sourceVerifiedBy=pin(entry), publicReceipts=refs[1:], capsule=pin(handoff),
                       hostInput=pin(target/'host-input.json'), changedPathsFrom209=delta,
                       physicalClasses=17, testPhysical=37, files=len(files), selectors=21,
                       expectedTests=211, collectedActualTests=0, extraCompilerOnly=2,
                       alreadyExecutedLocalOfflineTests=210, remoteActions=0,
                       needsFreshOrdinaryAuthentication=True, freshOwnerAndSpaceChecked=False,
                       independentTerminalMissing=True, newFormalAcceptance=0), stream, indent=2)
        stream.write('\n')
    print(pin(manifest), len(files), len(delta))


if __name__ == '__main__':
    main()
