"""SSC253 full fixed observer byte/mode/ACL closure and failed once empty proof."""
import hashlib
import os
from pathlib import Path
import stat
from pg1090_cold_finite_capture import metadata

NAMES=('pg1107-observer-v1','pg1108-ordinary-cold-once-v1','pg1112-observer-v1')


def proof(root,expected):
    if not isinstance(root,Path)or type(expected)is not dict or set(expected)!=set(NAMES):
        raise ValueError('fixed private sibling proof refused')
    observed={}
    for name in NAMES:
        path=root/name;s=path.lstat()
        if path.is_symlink()or(s.st_uid,s.st_gid,s.st_mode,s.st_nlink)!=(0,0,stat.S_IFDIR|0o700,2)or os.listxattr(path):
            raise ValueError('fixed private sibling authority refused')
        rows=expected[name]
        if type(rows)is not dict or set(os.listdir(path))!=set(rows):raise ValueError('fixed private payload closure refused')
        digests={}
        for file,digest in rows.items():
            if type(file)is not str or '/'in file or type(digest)is not str or len(digest)!=64:raise ValueError('fixed private payload record refused')
            p=path/file;a=p.lstat()
            if p.is_symlink()or(a.st_uid,a.st_gid,a.st_mode,a.st_nlink)!=(0,0,stat.S_IFREG|0o400,1)or os.listxattr(p):
                raise ValueError('fixed private payload authority refused')
            if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('fixed private payload bytes refused')
            if metadata(a)!=metadata(p.lstat()):raise ValueError('fixed private payload changed during proof')
            digests[file]=digest
        if set(os.listdir(path))!=set(rows)or metadata(s)!=metadata(path.lstat()):raise ValueError('fixed private sibling changed during proof')
        observed[name]=digests
    return observed
