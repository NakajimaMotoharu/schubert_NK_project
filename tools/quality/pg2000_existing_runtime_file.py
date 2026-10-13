"""Pin already published runtime inode; finish only remaining reload, never rewrite."""
import hashlib
import os
import stat
import subprocess

DIRECTORY='/run/systemd/system/schubert-nk-morning-controller.service.d'
NAME='zz-pg1980-once-resume.conf'
FILE_META=[28,15250,0,0,stat.S_IFREG|0o644,1,644,1791850609774873609,1791850609774873609]
DIR_META=[28,5514,0,0,stat.S_IFDIR|0o755,2,60,1791850609774000000,1791850609774000000]
SHA='78f1488383951e0fc2716bcf63ab41f75c64e975440e7f5e079fd6129f8612ec'


def metadata(value):
    return [value.st_dev,value.st_ino,value.st_uid,value.st_gid,value.st_mode,value.st_nlink,value.st_size,value.st_mtime_ns,value.st_ctime_ns]


def require(value):
    if not value:raise ValueError('existing fixed runtime refused')


class ExistingRuntime:
    def __init__(self,save):
        require(os.geteuid()==0);self.held=[];self.reloaded=False
        flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
        root=os.open('/',flags);self.held.append(root)
        for name in ['run','systemd','system','schubert-nk-morning-controller.service.d']:
            child=os.open(name,flags,dir_fd=root);self.held.append(child)
            a=os.fstat(child);b=os.stat(name,dir_fd=root,follow_symlinks=False)
            require(metadata(a)[:5]==metadata(b)[:5]and stat.S_ISDIR(a.st_mode)and a.st_uid==a.st_gid==0 and not a.st_mode&0o022 and not os.listxattr(child));root=child
        self.directory=root;require(metadata(os.fstat(root))==DIR_META and not os.fstatvfs(root).f_flag&os.ST_RDONLY)
        self.file=os.open(NAME,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=root);self.held.append(self.file)
        self.record=os.open(save,flags);self.held.append(self.record)
        s=os.fstat(self.record);require((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o700))
        self.verify()

    def verify(self):
        require(metadata(os.fstat(self.directory))==metadata(os.stat(DIRECTORY,follow_symlinks=False))==DIR_META)
        require(os.listdir(self.directory)==[NAME]and not os.listxattr(self.directory))
        require(metadata(os.fstat(self.file))==metadata(os.stat(NAME,dir_fd=self.directory,follow_symlinks=False))==FILE_META and not os.listxattr(self.file))
        value=os.pread(self.file,645,0);require(len(value)==644 and hashlib.sha256(value).hexdigest()==SHA)
        require(metadata(os.fstat(self.file))==FILE_META)
        for index,name in enumerate(['run','systemd','system','schubert-nk-morning-controller.service.d'],1):
            require(metadata(os.stat(name,dir_fd=self.held[index-1],follow_symlinks=False))[:5]==metadata(os.fstat(self.held[index]))[:5])

    def reload(self):
        require(not self.reloaded);self.verify()
        fd=os.open('daemon-reload-reserved.private',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.record)
        try:
            value=b'one normal existing-runtime daemon-reload; no retry\n'
            require(os.write(fd,value)==len(value));os.fsync(fd)
        finally:os.close(fd)
        os.fsync(self.record)
        r=subprocess.run(['/usr/bin/systemctl','daemon-reload'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
        require(r.returncode==0 and r.stdout==r.stderr==b'');self.reloaded=True;self.verify()

    def close(self):
        require(self.reloaded);self.verify()
        for fd in reversed(self.held):os.close(fd)
