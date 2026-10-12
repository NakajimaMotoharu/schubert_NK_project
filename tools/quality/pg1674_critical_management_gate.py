"""SSC275 host-side exclusion for critical guest management connections.

All new guest diagnostics in a critical interval must use this same guard;
host log reads and reattachment do not acquire or mutate guest state.
"""
from contextlib import contextmanager
import fcntl
import os
import stat


@contextmanager
def management_gate(path):
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        value = os.fstat(fd)
        if not stat.S_ISREG(value.st_mode) or (value.st_uid, stat.S_IMODE(value.st_mode), value.st_nlink) != (os.geteuid(), 0o600, 1) or os.listxattr(fd):
            raise ValueError('private host critical gate identity refused')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        linked = os.stat(path, follow_symlinks=False)
        if (linked.st_dev, linked.st_ino, linked.st_uid, linked.st_mode, linked.st_nlink) != (value.st_dev, value.st_ino, value.st_uid, value.st_mode, value.st_nlink):
            raise ValueError('critical gate namespace changed')
        yield fd
    finally:
        os.close(fd)
