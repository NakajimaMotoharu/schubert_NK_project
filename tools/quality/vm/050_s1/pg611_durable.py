"""File then same held directory durability, no overwrite or namespace substitution."""
import os
import pathlib
import stat


def identity(s):return s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink


def save(root,name,data):
    if not isinstance(root,pathlib.Path)or type(name)is not str or not name or name in ('.','..')or '/'in name or '\\'in name or type(data)is not bytes:
        raise ValueError('durable private record input refused')
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        held=identity(os.fstat(fd))
        if identity(root.lstat())!=held or not stat.S_ISDIR(held[4]):raise ValueError('held record namespace changed')
        f=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        with os.fdopen(f,'wb')as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.fsync(fd)
        if identity(root.lstat())!=held or identity(os.fstat(fd))!=held:raise ValueError('held record namespace changed')
    finally:os.close(fd)
