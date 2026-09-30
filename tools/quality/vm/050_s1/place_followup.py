"""New-only isolated signed candidate placement; no current/approval/permit mutation."""
import grp
import hashlib
import os
import pathlib
import shutil
import sys
import tarfile
import re

assert len(sys.argv) == 3 and os.geteuid() == 0
label, digest = sys.argv[1:]
assert re.fullmatch(r'PG[0-9]{3}', label) and re.fullmatch(r'[0-9a-f]{64}', digest)
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip() == 'pgpt-r2-20260927-01'
stem = label.lower()
stage = pathlib.Path('/home/ubuntu') / (stem + '-stage')
candidate = pathlib.Path('/opt/schubert-nk/releases') / ('0.1.0-' + label)
signature = pathlib.Path('/var/lib/pgpt-s1-preservation') / (stem + '-manifest.sig')
assert not candidate.exists() and not candidate.is_symlink()
assert not signature.exists() and not signature.is_symlink()
group = grp.getgrnam('schubert').gr_gid
candidate.mkdir(mode=0o750)
with tarfile.open(stage / (stem + '-release.tar'), 'r:') as archive:
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
assert hashlib.sha256((candidate / 'RELEASE-MANIFEST.json').read_bytes()).hexdigest() == digest
shutil.copyfile(stage / (stem + '-manifest.sig'), signature)
os.chown(signature, 0, 0)
os.chmod(signature, 0o400)
assert signature.stat().st_size == 64
print(label + ' CANDIDATE_PLACED fixedManifestHash=true currentUnchanged=true approvalIssued=false permitsIssued=0')
