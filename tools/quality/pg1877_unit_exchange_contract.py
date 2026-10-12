"""SSC283 sole regular Morning Unit exchange; no service start or old failure reset."""
import ctypes
import hashlib
import os
import stat
import subprocess
import time

UNIT='schubert-nk-morning-controller.service'
DIRECTORY='/etc/systemd/system'
PATH=DIRECTORY+'/'+UNIT
PART='pg1877-morning-unit.part'
PRIVATE='morning-unit-old.private'
OLD_SHA='28e6e23ddcfeacac7dc1daf326a1a2b1bc91895bbd34b313fe89a1b04f499bd6'
NEW_SHA='e9ce87045404893edede09b86dfb55523698ed26eeef3c4cb2b386f16518613b'
NEW_PATH='/opt/schubert-nk/releases/0.1.0-PG1846/systemd/'+UNIT


def require(value):
    if not value:raise ValueError('SSC283 exact regular Unit exchange refused')


def attributes(fd,digest):
    s=os.fstat(fd)
    require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o644,1))
    require(not os.listxattr(fd))
    raw=os.pread(fd,s.st_size+1,0)
    require(s.st_size==len(raw)and hashlib.sha256(raw).hexdigest()==digest)
    return s


def rename(directory,source,destination,target,flags):
    require(all(type(x)is int and x>=0 for x in [directory,destination]))
    require((source,target,flags)in [(PART,UNIT,2),(PART,PRIVATE,1)])
    libc=ctypes.CDLL(None,use_errno=True);call=libc.renameat2
    call.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];call.restype=ctypes.c_int
    ctypes.set_errno(0);result=call(directory,source.encode(),destination,target.encode(),flags)
    if result:raise OSError(ctypes.get_errno(),'Unit exchange unknown; no automatic retry')


class UnitExchange:
    def __init__(self,save):
        require(os.geteuid()==0)
        self.directory=os.open(DIRECTORY,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        self.private=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        require(os.fstat(self.directory).st_dev==os.fstat(self.private).st_dev)
        d=os.fstat(self.directory);p=os.fstat(self.private)
        require((d.st_uid,d.st_gid,stat.S_IMODE(d.st_mode))==(0,0,0o755)and(p.st_uid,p.st_gid,stat.S_IMODE(p.st_mode))==(0,0,0o700))
        self.names=sorted(os.listdir(self.directory));self.begin_ns=time.time_ns()
        self.old=os.open(UNIT,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.directory)
        self.old_attributes=attributes(self.old,OLD_SHA)
        self.exchanged=False;self.reloaded=False

    def exchange(self):
        require(not self.exchanged and not self.reloaded)
        require(os.stat(UNIT,dir_fd=self.directory,follow_symlinks=False)==os.fstat(self.old))
        attributes(self.old,OLD_SHA)
        source=os.open(NEW_PATH,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            raw=os.pread(source,1948,0);s=os.fstat(source)
            require(stat.S_ISREG(s.st_mode)and s.st_uid==0 and s.st_nlink==1 and s.st_size==len(raw)==1947 and not os.listxattr(source))
            require(hashlib.sha256(raw).hexdigest()==NEW_SHA)
        finally:os.close(source)
        require(not os.path.lexists(DIRECTORY+'/'+PART))
        fd=os.open(PART,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o644,dir_fd=self.directory)
        try:
            os.fchmod(fd,0o644);os.fchown(fd,0,0)
            with os.fdopen(os.dup(fd),'wb')as stream:stream.write(raw);stream.flush()
            os.fsync(fd)
        finally:os.close(fd)
        os.fsync(self.directory)
        require(not os.path.exists('/proc/self/fd/'+str(self.private)+'/'+PRIVATE))
        require(os.stat(UNIT,dir_fd=self.directory,follow_symlinks=False)==os.fstat(self.old))
        rename(self.directory,PART,self.directory,UNIT,2);os.fsync(self.directory)
        moved=os.stat(PART,dir_fd=self.directory,follow_symlinks=False)
        require((moved.st_dev,moved.st_ino)==(self.old_attributes.st_dev,self.old_attributes.st_ino))
        rename(self.directory,PART,self.private,PRIVATE,1);os.fsync(self.directory);os.fsync(self.private)
        self.exchanged=True;self.verify()

    def verify(self):
        require(self.exchanged)
        old=attributes(self.old,OLD_SHA);named=os.stat(PRIVATE,dir_fd=self.private,follow_symlinks=False)
        require(old==named and(old.st_dev,old.st_ino,old.st_mtime_ns)==(self.old_attributes.st_dev,self.old_attributes.st_ino,self.old_attributes.st_mtime_ns))
        now=time.time_ns();require(self.begin_ns<=old.st_ctime_ns<=now)
        fd=os.open(UNIT,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.directory)
        try:
            new=attributes(fd,NEW_SHA);require((new.st_dev,new.st_ino)!=(old.st_dev,old.st_ino))
            require(self.begin_ns<=new.st_mtime_ns<=now and self.begin_ns<=new.st_ctime_ns<=now)
        finally:os.close(fd)
        require(not os.path.lexists(DIRECTORY+'/'+PART))
        require(sorted(os.listdir(self.directory))==self.names)

    def reload(self):
        require(self.exchanged and not self.reloaded);self.verify()
        fd=os.open('daemon-reload-reserved.private',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600,dir_fd=self.private)
        try:os.write(fd,b'one normal daemon-reload; no retry\n');os.fsync(fd)
        finally:os.close(fd)
        os.fsync(self.private)
        result=subprocess.run(['/usr/bin/systemctl','daemon-reload'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
        require(result.returncode==0 and result.stdout==result.stderr==b'')
        self.reloaded=True;self.verify()

    def close(self):
        require(self.reloaded);self.verify()
        for fd in [self.old,self.private,self.directory]:os.close(fd)
