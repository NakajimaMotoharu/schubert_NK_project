"""SSC259 finite cold runtime writer; caller must own continuous M/A/DB/Refs.

No start, permit, business DB or original mutation. PT-DEP-1160001..003.
"""
import os
from pathlib import Path
import stat

UNIT='schubert-nk-morning-controller.service.d'
NAME='pg1160-once-resume.conf'
RUN_ID='343a5a1b-d064-47d5-88c2-31c36d7ba7a4'


def require(value):
    if not value:raise ValueError('finite cold runtime writer refused')


def metadata(fd):
    s=os.fstat(fd)
    return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]


def named_metadata(name,fd):
    s=os.stat(name,dir_fd=fd,follow_symlinks=False)
    return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]


def owned_prepare(expected,dropin):
    """Pin exact ancestors until writer close; volatile ancestor times not immutable."""
    flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
    held=[]
    try:
        fd=os.open('/',flags);held.append(fd)
        for name in ['run','systemd','system']:
            child=os.open(name,flags,dir_fd=fd);held.append(child)
            m=metadata(child);require(m[2:4]==[0,0]and stat.S_ISDIR(m[4])and not m[4]&0o022 and not os.listxattr(child))
            require(named_metadata(name,fd)==m);fd=child
        require(metadata(fd)==expected)
        prepare(Path('/proc/self/fd')/str(fd),expected,dropin)
        # Reopen the fixed graph through held ancestors after mutation, preserving identities.
        for index,name in enumerate(['run','systemd','system'],1):
            require(named_metadata(name,held[index-1])[:5]==metadata(held[index])[:5])
    finally:
        for fd in reversed(held):os.close(fd)


def fixed_dropin(base,native):
    require(type(base)is bytes and type(native)is bytes)
    starts=[v[len(b'ExecStart='):]for v in base.splitlines()if v.startswith(b'ExecStart=')]
    require(len(starts)==1 and starts[0].startswith(b'/usr/bin/java ')and starts[0].endswith(b' dev.codex.schubert.nk.batch.file.MorningProcessMain')and b'--resume'not in starts[0]and b'-javaagent'not in starts[0])
    agent=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false '
    argv=agent+starts[0][len(b'/usr/bin/java '):]
    wanted=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
    require(native==wanted)
    return b'# SSC259: cold fixed same-active same-cutoff resume; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv+b' --resume '+RUN_ID.encode('ascii')+b'\n'


def prepare(parent,expected,dropin):
    """Held-parent EXCL writer; failures leave partial files for isolation, never repair."""
    require(type(parent)is Path or isinstance(parent,Path))
    require(type(expected)is list and len(expected)==9 and expected[2:6]==[0,0,stat.S_IFDIR|0o755,2])
    require(type(dropin)is bytes and 0<len(dropin)<=4096)
    flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
    # A /proc/self/fd root is an already owned ancestor handle; reopen via '.'
    # beneath that descriptor, never follow a caller-supplied path symlink.
    if str(parent).startswith('/proc/self/fd/')and parent.name.isdecimal():
        root=os.open('.',flags,dir_fd=int(parent.name))
    else:root=os.open(parent,flags)
    try:
        require(metadata(root)==expected and not os.listxattr(root)and os.listdir(root)==[]and not os.fstatvfs(root).f_flag&os.ST_RDONLY)
        os.mkdir(UNIT,0o700,dir_fd=root)
        child=os.open(UNIT,flags,dir_fd=root)
        try:
            initial=metadata(child);require(initial[2:6]==[0,0,stat.S_IFDIR|0o700,2]and not os.listxattr(child)and os.listdir(child)==[])
            require(named_metadata(UNIT,root)==initial)
            os.fchmod(child,0o755)
            after=metadata(child);require(after[:4]==initial[:4]and after[4]==stat.S_IFDIR|0o755 and after[5:8]==initial[5:8]and not os.listxattr(child))
            fd=os.open(NAME,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=child)
            try:
                file=metadata(fd);require(file[2:7]==[0,0,stat.S_IFREG|0o600,1,0]and not os.listxattr(fd))
                os.fchmod(fd,0o644);offset=0
                while offset<len(dropin):
                    size=os.write(fd,dropin[offset:]);require(type(size)is int and 0<size<=len(dropin)-offset);offset+=size
                os.fsync(fd)
                file=metadata(fd);require(file[2:7]==[0,0,stat.S_IFREG|0o644,1,len(dropin)])
            finally:os.close(fd)
            os.fsync(child)
            require(os.listdir(child)==[NAME])
            fd=os.open(NAME,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=child)
            try:
                require(metadata(fd)==file and os.read(fd,4097)==dropin and os.read(fd,1)==b'')
                require(metadata(fd)==file and not os.listxattr(fd))
            finally:os.close(fd)
            child_after=metadata(child);require(child_after[:5]==after[:5]and child_after[5]==2 and not os.listxattr(child))
            require(named_metadata(UNIT,root)==child_after)
        finally:os.close(child)
        os.fsync(root)
        now=metadata(root);require(now[:5]==expected[:5]and now[5]==expected[5]+1 and now[6]>=expected[6]and now[7]>=expected[7]and now[8]>=expected[8]and not os.listxattr(root)and os.listdir(root)==[UNIT])
    finally:os.close(root)
