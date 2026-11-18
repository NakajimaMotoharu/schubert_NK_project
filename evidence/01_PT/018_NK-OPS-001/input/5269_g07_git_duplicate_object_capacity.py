"""Pack exact, independently verified Git objects. Keep old packs and every logical object."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
RUN = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
GIT = Path('/home/mini/codex/project1/schubert_NK_project/.git')
FANOUT = re.compile(r'[0-9a-f]{2}')
SUFFIX = re.compile(r'[0-9a-f]{38}')
OBJECT_ID = re.compile(r'[0-9a-f]{40}')


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def fingerprint(path):
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_nlink)


def git(*args, data=None, timeout=45):
    reply = subprocess.run(['git', *map(str, args)], input=data, capture_output=True,
                           check=True, timeout=timeout)
    return reply.stdout


def ref_markers():
    return {
        'refs': hashlib.sha256(git('for-each-ref', '--format=%(refname) %(objectname)')).hexdigest(),
        'stashOrder': hashlib.sha256(git('stash', 'list', '--format=%H')).hexdigest(),
        'index': sha(Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())),
    }


def snapshot(objects):
    loose = {}
    for fanout in objects.iterdir():
        if not FANOUT.fullmatch(fanout.name):
            continue
        assert fanout.is_dir() and not fanout.is_symlink()
        for item in fanout.iterdir():
            if SUFFIX.fullmatch(item.name):
                loose[fanout.name + item.name] = (item, fingerprint(item))
    return loose


def ensure_idle_git():
    reading = subprocess.run(['ps', '-C', 'git,git-pack-objects,git-gc,git-fetch,git-remote-https',
                              '-o', 'comm='], capture_output=True, check=False, timeout=8)
    assert reading.returncode in (0, 1) and not reading.stdout.strip()


def write(path, values):
    with path.open('x') as stream:
        json.dump(values, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def install_one(source, destination, stage_dir):
    temporary = stage_dir / source.name
    with source.open('rb') as original, temporary.open('xb') as target:
        shutil.copyfileobj(original, target)
        target.flush()
        os.fsync(target.fileno())
    assert sha(source) == sha(temporary)
    os.link(temporary, destination)
    assert sha(destination) == sha(source)
    temporary.unlink()


def verify(pack_index, objects):
    lines = git('verify-pack', '-v', pack_index, timeout=120).decode().splitlines()
    identifiers = [parts[0] for line in lines if (parts := line.split()) and OBJECT_ID.fullmatch(parts[0])]
    assert len(identifiers) == len(objects) and set(identifiers) == set(objects)
    assert lines[-1].endswith(': ok')
    return len(identifiers)


def run_pack_step(run, label, args, output, data=None):
    errors = run / (label + '.stderr')
    with output.open('xb') as stdout, errors.open('xb') as stderr:
        reply = subprocess.run(['git', *map(str, args)], input=data, stdout=stdout,
                               stderr=stderr, check=False, timeout=150)
    exit_record = dict(stage=label, actualExit=reply.returncode, stderrBytes=errors.stat().st_size,
                       stderrSha256=sha(errors))
    write(run / (label + '-exit.json'), exit_record)
    assert reply.returncode == 0, f'{label} exited {reply.returncode}'
    return exit_record


def main():
    start = json.loads(next(PLAN.glob('578_G07*.json')).read_text())
    values = start['values']
    assert git('diff', '--name-only', '-z', values['source'], 'HEAD').decode().split('\0')[:-1] == [
        str(next(Path('documents/900_OTHER/910_台帳').glob('915_*.md')))
    ]
    head = git('rev-parse', 'HEAD').decode().strip()
    assert git('rev-parse', 'origin/dev-foundation').decode().strip() == values['source']
    assert Path(git('rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip()) == GIT
    ensure_idle_git()
    markers = ref_markers()
    assert len(git('stash', 'list', '--format=%H').splitlines()) == 7
    objects = GIT / 'objects'
    pack_dir = objects / 'pack'
    assert objects.resolve() == objects and pack_dir.resolve() == pack_dir
    assert not (objects / 'info/alternates').exists()
    before = shutil.disk_usage(GIT).free
    original_packs = {p.name: fingerprint(p) for p in pack_dir.glob('pack-*')}
    loose = snapshot(objects)
    assert loose
    ordered = ''.join(oid + '\n' for oid in sorted(loose)).encode()
    frozen = dict(startEvent=start['eventId'], startedAtUTC=now(), source=values['source'], executionHead=head,
                  looseObjects=len(loose), looseIdentityListSha256=hashlib.sha256(ordered).hexdigest(),
                  availableBefore=before, refsAndIndex=markers, preexistingPackFiles=len(original_packs))
    previous = RUN / values['run'].lower()
    assert (previous / 'prepare.json').is_file() and not (previous / 'verified-before-removing.json').exists()
    run = RUN / (values['run'].lower() + '-streamed')
    run.mkdir(mode=0o700)
    write(run / 'prepare.json', frozen)
    with tempfile.TemporaryDirectory(dir='/dev/shm', prefix='pgpt-loose-object-pack-') as space:
        temp = Path(space)
        disk_stage = run / 'install-stage'
        disk_stage.mkdir(mode=0o700)
        candidate = temp / 'streamed.pack'
        packed = run_pack_step(run, 'pack-stdout', ('pack-objects', '--stdout', '--compression=6',
                               '--window=10', '--threads=2'), candidate, ordered)
        index = temp / 'streamed.idx'
        result = run / 'index-pack.stdout'
        indexed = run_pack_step(run, 'index-pack', ('index-pack', '-o', index, candidate), result)
        pack_id = result.read_text().strip()
        assert OBJECT_ID.fullmatch(pack_id)
        names = [f'pack-{pack_id}.{suffix}' for suffix in ('pack', 'idx')]
        ram_pack, ram_index = (temp / name for name in names)
        candidate.rename(ram_pack)
        index.rename(ram_index)
        checked = verify(ram_index, loose)
        size = ram_pack.stat().st_size + ram_index.stat().st_size
        assert size <= shutil.disk_usage(GIT).free - 192 * 1024**2, 'retain metadata emergency margin'
        ensure_idle_git()
        assert ref_markers() == markers and snapshot(objects) == loose
        assert all(fingerprint(pack_dir / name) == identity for name, identity in original_packs.items())
        installed = []
        for name in names:
            destination = pack_dir / name
            install_one(temp / name, destination, disk_stage)
            installed.append(dict(name=name, sha256=sha(destination), bytes=destination.stat().st_size))
        sync_dir(pack_dir)
        assert verify(pack_dir / names[1], loose) == checked
        assert ref_markers() == markers and snapshot(objects) == loose
        receipt = dict(frozen, verifiedObjects=checked, installed=installed,
                       packAndIndexBytes=size, identicalInstalledPackVerified=True,
                       expectedConfirmedOriginals=len(loose), writtenBeforeRemovingCopiesUTC=now(),
                       gitStepReceipts=[packed, indexed], earlierPrepare=sha(previous / 'prepare.json'),
                       earlierExit=128, earlierReason='Git child diagnostic not captured; staging path on a separate filesystem')
        write(run / 'verified-before-removing.json', receipt)
        sync_dir(run)
        moved = 0
        for path, identity in loose.values():
            assert fingerprint(path) == identity
            path.unlink()
            moved += 1
        assert moved == len(loose)
        assert ref_markers() == markers
        assert all(fingerprint(pack_dir / name) == identity for name, identity in original_packs.items())
        assert verify(pack_dir / names[1], loose) == checked
        assert not any(path.exists() for path, _ in loose.values())
        disk_stage.rmdir()
    after = shutil.disk_usage(GIT).free
    value = dict(receipt, actualExit=0, availableAfter=after, netRecoveredBytes=after-before,
                 redundantLooseCopiesReleased=moved, previousPacksRetained=True, logicalGitObjectsRemoved=0,
                 gitRefsIndexAndStashUntouched=True, originalDatabaseOrPrivateEvidenceActions=0,
                 productTests=0, externalOperations=0, newAcceptance=0,
                 terminalAtUTC=now(), verifier=dict(path=__file__, sha256=sha(Path(__file__))))
    p = E / values['run'] / 'manifest.json'
    p.parent.mkdir()
    write(p, value)
    print(moved, before, after, after-before, sha(p))


if __name__ == '__main__':
    main()
