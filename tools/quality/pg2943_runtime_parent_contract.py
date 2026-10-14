"""Exact sole-directory/file delta for current empty runtime root or retained empty parent."""
import hashlib
import stat

ROOT='/run/systemd/system'
DIRECTORY=ROOT+'/schubert-nk-morning-controller.service.d'
TARGET=DIRECTORY+'/zz-pg2942-once-resume.conf'


def row(value):
    return type(value)is dict and set(value)=={'metadata','sha256'}and type(value['metadata'])is list and len(value['metadata'])==9 and all(type(x)is int and x>=0 for x in value['metadata'])


def runtime_tree(before,actual,dropin,lower_ns,upper_ns):
    if type(before)is not dict or type(actual)is not dict or set(before)not in [{ROOT},{ROOT,DIRECTORY}]or set(actual)!={ROOT,DIRECTORY,TARGET}:return False
    if type(dropin)is not bytes or not 0<len(dropin)<=4096 or type(lower_ns)is not int or type(upper_ns)is not int or not 0<=lower_ns<=upper_ns:return False
    if not all(row(x)for x in [*before.values(),*actual.values()]):return False
    left=before[ROOT]['metadata'];right=actual[ROOT]['metadata'];directory=actual[DIRECTORY]['metadata'];file=actual[TARGET]['metadata']
    if before[ROOT]['sha256']is not None or actual[ROOT]['sha256']is not None or actual[DIRECTORY]['sha256']is not None:return False
    if left[2:5]!=[0,0,stat.S_IFDIR|0o755]or right[:5]!=left[:5]:return False
    if directory[0]!=left[0]or directory[1]==left[1]or directory[2:6]!=[0,0,stat.S_IFDIR|0o755,2]:return False
    if DIRECTORY in before:
        old=before[DIRECTORY]['metadata']
        if actual[ROOT]!=before[ROOT]or before[DIRECTORY]['sha256']is not None or old[:6]!=directory[:6]or directory[6]<old[6]:return False
        if any(not max(old[i],lower_ns)<=directory[i]<=upper_ns for i in [7,8]):return False
    else:
        if left[5]!=2 or right[5]!=3 or right[6]<left[6]:return False
        if any(not max(left[i],lower_ns)<=right[i]<=upper_ns for i in [7,8]):return False
        if any(not lower_ns<=directory[i]<=upper_ns for i in [7,8]):return False
    if file[0]!=left[0]or file[1]in {left[1],directory[1]}or file[2:7]!=[0,0,stat.S_IFREG|0o644,1,len(dropin)]:return False
    if any(not lower_ns<=file[i]<=upper_ns for i in [7,8]):return False
    return actual[TARGET]['sha256']==hashlib.sha256(dropin).hexdigest()


def owned_create_parent(expected_root,unit,require,metadata,named_metadata):
    """Caller owns continuous M/A/DB/Refs. Partial create is retained on failure, not repaired."""
    import os
    flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
    held=[]
    try:
        require(os.geteuid()==os.getegid()==0)
        require(unit=='schubert-nk-morning-controller.service.d')
        fd=os.open('/',flags);held.append(fd)
        for name in ['run','systemd','system']:
            child=os.open(name,flags,dir_fd=fd);held.append(child)
            m=metadata(child)
            require(m[2:4]==[0,0]and stat.S_ISDIR(m[4])and not m[4]&0o022 and not os.listxattr(child))
            require(named_metadata(name,fd)==m);fd=child
        require(metadata(fd)==expected_root and expected_root[2:6]==[0,0,stat.S_IFDIR|0o755,2]and os.listdir(fd)==[])
        os.mkdir(unit,0o700,dir_fd=fd)
        child=os.open(unit,flags,dir_fd=fd);held.append(child)
        m=metadata(child);require(m[0]==expected_root[0]and m[1]!=expected_root[1]and m[2:6]==[0,0,stat.S_IFDIR|0o700,2]and not os.listxattr(child)and os.listdir(child)==[])
        os.fchmod(child,0o755);os.fsync(child);os.fsync(fd)
        require(named_metadata(unit,fd)==metadata(child)and os.listdir(fd)==[unit])
        require(metadata(child)[2:6]==[0,0,stat.S_IFDIR|0o755,2])
        for index,name in enumerate(['run','systemd','system',unit],1):
            require(named_metadata(name,held[index-1])[:5]==metadata(held[index])[:5])
        return metadata(child)
    finally:
        for fd in reversed(held):os.close(fd)
