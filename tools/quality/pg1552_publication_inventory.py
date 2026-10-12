"""Full signed FD inventory with only independently checked publication deltas.

Never rebase retained metadata, skip payload entries or treat a path switch as
unchanged. Old approval remains authenticated through its actual detached FD.
"""
import hashlib
import os
from pathlib import PurePosixPath
import stat

def capture(inv, contract, oracle, before, actual, phase, begin, end):
    if inv.closed or inv.root_fd is None:raise ValueError('publication inventory scope unavailable')
    output=[]
    for fd,parent,name,fixed,acl in inv.held:
        current=contract.metadata(fd);attrs=contract.attributes(fd)
        if attrs!=acl:raise ValueError('publication inventory ACL changed')
        linked=os.stat(name,dir_fd=parent,follow_symlinks=False)
        identity=(linked.st_dev,linked.st_ino,linked.st_uid,linked.st_gid,linked.st_mode,linked.st_nlink,linked.st_size,linked.st_mtime_ns,linked.st_ctime_ns)
        path=os.readlink('/proc/self/fd/'+str(fd))
        detached=(str(inv.root)==oracle.APPROVAL and name=='current' and phase in oracle.PHASES[1:])
        if detached:
            path=oracle.APPROVAL+'/current'
        digest=None
        if stat.S_ISREG(current[4]):
            h=hashlib.sha256();offset=0
            while offset<current[6]:
                chunk=os.pread(fd,min(131072,current[6]-offset),offset)
                if not chunk:raise ValueError('publication signed FD truncated')
                h.update(chunk);offset+=len(chunk)
            digest=h.hexdigest()
            relative=str(PurePosixPath(path).relative_to(inv.root));record=inv.records[relative]
            if current[6]!=record['size']or digest!=record['sha256']:raise ValueError('publication signed FD bytes changed')
        if path in [oracle.APPROVAL,oracle.CURRENT] or detached:
            root=oracle.APPROVAL if path.startswith(oracle.APPROVAL)else oracle.CURRENT
            row={'metadata':list(current),'sha256':digest,'target':None,'acl':[n for n,_ in attrs]}
            oracle.verify_retained(path,before[root][path],row,phase,actual,begin,end)
            if not detached and identity!=current:raise ValueError('publication retained parent not same linked inode')
            if detached:
                # The new linked approval is independently accepted as the exact
                # replacement. Never equate the new pathname with the old FD.
                if list(identity)!=actual[oracle.APPROVAL][path]['metadata']:raise ValueError('publication linked approval identity differs')
        elif current!=fixed or identity!=fixed:raise ValueError('unapproved inventory metadata change')
        if contract.metadata(fd)!=current or contract.attributes(fd)!=attrs:raise ValueError('publication inventory changed during observation')
        output.append((name,current,attrs,digest))
    return tuple(output)
