"""Verify the unchanged-disk private export before the VM retention post oracle.

Only original metadata/digest/time are returned; raw dump/config/credential
bytes never enter a guest script, Git or model output.
"""
import hashlib
import json
from pathlib import Path
from pg1090_cold_finite_capture import metadata

ROOT=Path('/home/mini/codex/project1/work/pgpt-vm/private/pg1128-retired-backup-v1')
SHA='511b28d0358d2573cbb1cbb145c04c8ccd3a3bd28d9fd189f91742ba5ff295e4'
NAMES={'MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'}


def proof():
    raw=(ROOT/'manifest.private.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('fixed private preservation proof refused')
    doc=json.loads(raw)
    if (set(doc['files'])!=NAMES or not doc['sourceIdentityUnchanged']or
        doc['currentBackupVmDbModified']or not doc['rawOutsideGit']):
        raise ValueError('private export closure refused')
    files={}
    for name,value in doc['files'].items():
        p=ROOT/'bundle'/name;s=p.lstat()
        if not p.is_file()or p.is_symlink()or s.st_nlink!=1 or s.st_mode&0o077:
            raise ValueError('private preserved regular artifact refused')
        h=hashlib.sha256()
        with p.open('rb')as f:
            while block:=f.read(131072):h.update(block)
        if s.st_size!=value['size']or h.hexdigest()!=value['sha256']or metadata(p.lstat())!=metadata(s):
            raise ValueError('private preserved original digest refused')
        files[name]={key:value[key]for key in ['size','sha256','originalMetadata']}
    # Manifest input itself is bounded and already matches the old original SHA.
    manifest=json.loads((ROOT/'bundle/MANIFEST.json').read_bytes())
    return {'folder':doc['originalPath'],'startedAt':manifest['startedAt'],
            'files':files,'privateProofSha256':SHA}
