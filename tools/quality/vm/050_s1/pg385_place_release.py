"""New-only isolated candidate placement; no current/approval/permit activation."""
import hashlib
import os
import pathlib
import grp
import tarfile
import shutil

assert os.geteuid() == 0
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip() == 'pgpt-r2-20260927-01'
stage = pathlib.Path('/home/ubuntu/pg385-stage')
candidate = pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG385')
assert not candidate.exists() and not candidate.is_symlink()
group = grp.getgrnam('schubert').gr_gid
candidate.mkdir(mode=0o750)
with tarfile.open(stage / 'pg385-release.tar', 'r:') as archive:
    for item in archive.getmembers():
        path = pathlib.PurePosixPath(item.name)
        assert not path.is_absolute() and '..' not in path.parts
        assert item.isfile() or item.isdir()
    archive.extractall(candidate, filter='data')
for path in [candidate, *candidate.rglob('*')]:
    assert not path.is_symlink()
    os.chown(path, 0, group)
    os.chmod(path, 0o750 if path.is_dir() or path.name == 'schubert-nk-inbox-inspector' else 0o640)
    if path.is_file():
        with path.open('rb') as stream:
            os.fsync(stream.fileno())
assert hashlib.sha256((candidate / 'RELEASE-MANIFEST.json').read_bytes()).hexdigest() == '55beeb489a31b04ad0c717fdc3f6b0ddb03fd1db9cf9c59d73278782e678f62d'
signature = pathlib.Path('/var/lib/pgpt-s1-preservation/pg385-manifest.sig')
assert not signature.exists()
shutil.copyfile(stage / 'pg385-manifest.sig', signature)
os.chown(signature, 0, 0)
os.chmod(signature, 0o400)
assert signature.stat().st_size == 64
print('PG385 CANDIDATE_PLACED source=a6b5c7c8b fixedManifestHash=true currentUnchanged=true approvalIssued=false permitsIssued=0')
