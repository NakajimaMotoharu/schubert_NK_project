"""New-only isolated candidate placement; no current/approval/permit activation."""
import hashlib
import os
import pathlib
import grp
import tarfile
import shutil

assert os.geteuid() == 0
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip() == 'pgpt-r2-20260927-01'
stage = pathlib.Path('/home/ubuntu/pg383-stage')
candidate = pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG383')
assert not candidate.exists() and not candidate.is_symlink()
group = grp.getgrnam('schubert').gr_gid
candidate.mkdir(mode=0o750)
with tarfile.open(stage / 'pg383-release.tar', 'r:') as archive:
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
assert hashlib.sha256((candidate / 'RELEASE-MANIFEST.json').read_bytes()).hexdigest() == 'd46f50479c21c9d332c0d8a555df48fce09cc45239a9ba8b460748afb2cae39d'
signature = pathlib.Path('/var/lib/pgpt-s1-preservation/pg383-manifest.sig')
assert not signature.exists()
shutil.copyfile(stage / 'pg383-manifest.sig', signature)
os.chown(signature, 0, 0)
os.chmod(signature, 0o400)
assert signature.stat().st_size == 64
print('PG383 CANDIDATE_PLACED source=741a02f7b fixedManifestHash=true currentUnchanged=true approvalIssued=false permitsIssued=0')
