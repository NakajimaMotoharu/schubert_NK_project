"""Fixed current method bindings and public Program-spec corpus, no runtime or private inputs."""
import hashlib
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
HEAD='854c8b6e2cee973939fdffa05cca9121d6f9450c'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1946_G13ExplicitCaseRows_既存仕様対応候補仕様.md'
SPEC_SHA='cd7788615a7f2a70e8d4921fee285b02ae94eda69b2c4ec3aff03ac38f259e6f'

def methods():
    assert data.sha(SPEC.read_bytes())==SPEC_SHA
    manifest=data.read_checked(BASE/'PG9592-current-test-method-post-v1/manifest.json','d73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    assert manifest['actualExit']==0 and manifest['source']==SOURCE and manifest['exactDeclarationBindings']==5622
    return data.read_checked(BASE/'PG9592-current-test-method-post-v1/method-declaration-bindings.json',manifest['bindingsSha256'])

def corpus():
    listing=subprocess.check_output(['git','ls-tree','-rz',HEAD,'--','evidence/01_PT'],cwd=ROOT)
    rows=[]
    for record in listing.split(b'\0'):
        if not record:continue
        header,name=record.split(b'\t',1);path=name.decode('utf-8');parts=Path(path).parts
        if len(parts)!=4 or not path.endswith('.md') or '仕様' not in parts[-1]:continue
        mode,kind,blob=header.decode().split();assert mode=='100644' and kind=='blob'
        actual=ROOT/path;assert actual.resolve()==actual and not actual.is_symlink()
        raw=actual.read_bytes();raw.decode('utf-8')
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
        rows.append((dict(path=path,sha256=data.sha(raw),gitBlob=blob,bytes=len(raw)),raw.decode('utf-8')))
    assert rows
    return sorted(rows,key=lambda r:r[0]['path'])
