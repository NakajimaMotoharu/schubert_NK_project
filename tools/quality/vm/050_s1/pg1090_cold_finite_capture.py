"""SSC249250 full held/linked metadata capture for finite publication observers.

No write, dispatch, signal, fallback or publication authority.
"""
import hashlib
import os
from pathlib import Path
import stat


def metadata(value):
    return [value.st_dev,value.st_ino,value.st_uid,value.st_gid,value.st_mode,value.st_nlink,
            value.st_size,value.st_mtime_ns,value.st_ctime_ns]


def fd_record(fd):
    if type(fd)is not int or fd<0:raise ValueError('held descriptor refused')
    first=os.fstat(fd);m=metadata(first)
    attrs=list(os.listxattr(fd));target=None;digest=None
    if stat.S_ISREG(first.st_mode):
        if not 0<=first.st_size<=2147483647:raise ValueError('held size refused')
        h=hashlib.sha256();offset=0
        while offset<first.st_size:
            part=os.pread(fd,min(131072,first.st_size-offset),offset)
            if not part:raise ValueError('held bytes truncated')
            h.update(part);offset+=len(part)
        digest=h.hexdigest()
    elif not stat.S_ISDIR(first.st_mode):raise ValueError('held ordinary type refused')
    if metadata(os.fstat(fd))!=m or list(os.listxattr(fd))!=attrs:raise ValueError('held observation changed')
    return {'metadata':m,'sha256':digest,'target':target,'acl':attrs}


def path_record(path):
    if not isinstance(path,(str,Path)):raise ValueError('linked path refused')
    p=Path(path);first=p.lstat();m=metadata(first)
    attrs=list(os.listxattr(p,follow_symlinks=False));target=None;digest=None
    if stat.S_ISLNK(first.st_mode):target=os.readlink(p)
    elif stat.S_ISREG(first.st_mode):
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        try:
            observed=fd_record(fd)
            if observed['metadata']!=m:raise ValueError('linked ordinary identity changed')
            digest=observed['sha256']
        finally:os.close(fd)
    elif not stat.S_ISDIR(first.st_mode):raise ValueError('linked type refused')
    if metadata(p.lstat())!=m or list(os.listxattr(p,follow_symlinks=False))!=attrs:
        raise ValueError('linked observation changed')
    if target is not None and target!=os.readlink(p):raise ValueError('linked target changed')
    return {'metadata':m,'sha256':digest,'target':target,'acl':attrs}


def direct_tree(root):
    if not isinstance(root,(str,Path)):raise ValueError('parent path refused')
    p=Path(root);first=path_record(p)
    if not stat.S_ISDIR(first['metadata'][4]):raise ValueError('parent ordinary directory refused')
    names=sorted(os.listdir(p));value={str(p):first}
    for name in names:value[str(p/name)]=path_record(p/name)
    if names!=sorted(os.listdir(p))or first!=path_record(p):raise ValueError('parent observation changed')
    return value
