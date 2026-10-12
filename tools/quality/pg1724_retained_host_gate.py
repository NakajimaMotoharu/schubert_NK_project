"""SSC276 queue on the unchanged kernel gate, never force-unlock the owner.

Only a frozen failed-phase recovery uses this handoff. All other management
still uses the ordinary nonblocking exclusive gate.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import os
from pathlib import Path
import stat
import threading

def identity(fd, path):
    a=os.fstat(fd);b=os.stat(path,follow_symlinks=False)
    if not stat.S_ISREG(a.st_mode)or(a.st_uid,stat.S_IMODE(a.st_mode),a.st_nlink)!=(os.geteuid(),0o600,1)or os.listxattr(fd)or(a.st_dev,a.st_ino,a.st_uid,a.st_mode,a.st_nlink)!=(b.st_dev,b.st_ino,b.st_uid,b.st_mode,b.st_nlink):
        raise ValueError('same private gate inode required')
    return a.st_dev,a.st_ino

def current_owner(path):
    p=Path('/proc/230583');st=(p/'stat').read_text().rpartition(')')[2].split()
    if int(st[19])!=7555645 or int(st[1])!=230523 or hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()!='5a5cff3ba9f3379bceb96da8fda3ef4a6ab51547f4b5cd0c1d9305e99b4c2ad0':
        raise ValueError('current retained wrapper required')
    s=path.stat();f=(p/'fd/3').stat()
    if(s.st_dev,s.st_ino)!=(66306,9337730)or(s.st_dev,s.st_ino)!=(f.st_dev,f.st_ino):raise ValueError('actual retained gate FD required')
    matches=[]
    for line in Path('/proc/locks').read_text().splitlines():
        v=line.split()
        if len(v)>=8 and v[1]=='FLOCK'and v[5]==f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}':matches.append(v)
    if len(matches)!=1 or matches[0][1:5]!=['FLOCK','ADVISORY','WRITE','230583']:raise ValueError('sole retained host lock owner required')
    return True

@contextmanager
def queued_gate(path, validate_owner=current_owner):
    fd=os.open(path,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
    acquired=threading.Event();errors=[]
    try:
        identity(fd,path);validate_owner(path)
        def wait():
            try:
                fcntl.flock(fd,fcntl.LOCK_EX);identity(fd,path);acquired.set()
            except (OSError,ValueError)as error:errors.append(error)
        # Kernel queues the successor while the original retains exclusion.
        thread=threading.Thread(target=wait,daemon=True);thread.start()
        yield acquired
        if not acquired.wait(30)or errors:raise ValueError('retained gate handoff not complete')
        thread.join(1)
        if thread.is_alive():raise ValueError('gate waiter must be terminal')
        identity(fd,path)
    finally:
        os.close(fd)
