"""Compact the exact owned older public projection after fully verifying restorable bytes."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import os
import re
import runpy
import shutil
import stat
import subprocess
import tarfile

HERE = Path(__file__).resolve()
B = runpy.run_path(str(HERE.with_name('5126_g07_preserve_duplicate_text_projections.py')))
E, RUNS = B['EVIDENCE'], B['RUNS']
read, digest, write = B['load'], B['hash_file'], B['write']
D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
NAME = 'pg38796-g07-current-public-delta-survey-v1'
PROTECTED = {'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py'}


def state(path):
    s = path.lstat()
    assert path.resolve() == path and stat.S_ISREG(s.st_mode)
    assert s.st_uid == os.getuid() and s.st_nlink == 1
    return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns


def git_objects(objects):
    assert all(re.fullmatch(r'[0-9a-f]{40}', item) for item in objects)
    text = ''.join(oid + '\n' for oid in sorted(objects)).encode()
    result = subprocess.check_output(['git', 'cat-file', '--batch-check=%(objecttype)'],
                                     input=text, timeout=35)
    assert result.splitlines() == [b'blob'] * len(objects)
    return hashlib.sha256(text).hexdigest()


def main():
    start = read(next(D.glob('603_G07*.json')))
    values = start['values']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == values['source']
    assert all(digest(Path(row['path'])) == row['sha256'] for row in values['oracleReferences'])
    manifest = read(Path(values['oracleReferences'][0]['path']))
    assert manifest['actualExit'] == 0 and manifest['freshUnresolvedFindings'] == 0
    assert manifest['privateLogRead'] == manifest['untrackedRead'] == 0
    work = RUNS / NAME
    assert work.resolve() == work and work.stat().st_uid == os.getuid()
    index = work / 'projection.json'
    raw_report = work / 'report.json'
    assert digest(index) == manifest['rawProjectionManifestSha256']
    assert digest(raw_report) == manifest['rawReportSha256']
    rows = read(index)['versions']
    assert len(rows) == 845 and sum(row['text'] for row in rows) == 840
    assert not any(Path(row['path']).name in PROTECTED for row in rows)

    expected, states = {}, {}
    raw_blob_ids = {row['blob'] for row in rows}
    oid_hash = git_objects(raw_blob_ids)
    for row in rows:
        if not row['text']:
            continue
        name = Path(row['prefix'])
        assert len(name.parts) == 3 and name.parts[0] == 'text' and re.fullmatch(r'[0-9]{4}', name.parts[1])
        assert str(name) not in expected
        file = work / name
        s = state(file)
        assert digest(file) == row['decodedSha256']
        expected[str(name)] = dict(bytes=s[2], sha256=row['decodedSha256'])
        states[str(name)] = s
    assert {str(p.relative_to(work)) for p in (work / 'text').glob('*/*')} == set(expected)
    before = shutil.disk_usage(work).free
    assert before > 512 * 1024**2
    archive = work / 'text-projection-retained.tar.gz'
    with archive.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        with tarfile.open(fileobj=stream, mode='w:gz', compresslevel=6) as out:
            for name in sorted(expected):
                out.add(work / name, arcname=name, recursive=False)
        stream.flush()
        os.fsync(stream.fileno())
    B['verify_member_inventory'](archive, expected)
    assert digest(index) == manifest['rawProjectionManifestSha256']
    assert all(state(work / name) == original for name, original in states.items())
    a_sha = digest(archive)
    receipt = work / 'text-projection-retained.json'
    proof = dict(actualExit=0, source=values['source'], originalQualifier=values['oracleReferences'][0],
                 archive=dict(path=str(archive), sha256=a_sha, bytes=archive.stat().st_size),
                 everyTextMemberVerified=840, preservedExistingBinaryCount=5, preservedGitBlobIds=len(raw_blob_ids),
                 preservedGitIdentityListSha256=oid_hash, originalIndexSha256=digest(index),
                 originalReportSha256=manifest['rawReportSha256'], before=before,
                 restoreCommand=['tar', '-xzf', str(archive), '--no-same-owner', '-C', str(work)])
    write(receipt, proof)
    assert digest(archive) == a_sha
    for name, item in expected.items():
        file = work / name
        assert state(file) == states[name] and digest(file) == item['sha256']
        file.unlink()
    assert not list((work / 'text').glob('*/*'))
    assert digest(raw_report) == manifest['rawReportSha256'] and digest(index) == manifest['rawProjectionManifestSha256']
    assert git_objects(raw_blob_ids) == oid_hash
    after = shutil.disk_usage(work).free
    summary = dict(proof, after=after, netRecoveredBytes=after-before, duplicatesReleased=840,
                   initialPreparationExit=1, initialIssue='Legacy manifest loader requires Path, not a string',
                   receipt=dict(path=str(receipt), sha256=digest(receipt)),
                   identifiedOriginalArtifactsRemoved=0, productTests=0, scannerReexecuted=False,
                   privateRuntimeRead=0, latestRawNativeTouched=0, newAcceptance=0,
                   terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=digest(HERE))
    out = E / values['run']
    out.mkdir()
    result = out / 'manifest.json'
    write(result, summary)
    print(digest(result), summary['netRecoveredBytes'])


if __name__ == '__main__':
    main()
