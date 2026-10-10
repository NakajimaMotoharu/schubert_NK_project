"""SS343/353: exact current completed resume retirement, no start/DB mutation.

PT-DEP-1223001..004. Full original fields retained, declaration/history split.
This pure oracle grants no mutation authority; caller holds M/A/DB/tenRefs.
"""
import hashlib
import os
import stat
from pg847_configuration import FIELDS

MORNING='schubert-nk-morning-controller.service'
ROOT='/run/systemd/system/'+MORNING+'.d'
NAME='zz-pg1160-once-resume.conf'
TARGET=ROOT+'/'+NAME
RUN='343a5a1b-d064-47d5-88c2-31c36d7ba7a4'
SHA='d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0'
EMPTY=('n/a','n/a','0','(null)','0/0')

def require(value):
    if not value:raise ValueError('completed current runtime contract rejected')

def same_except_runtime(before,after,parse):
    require(type(before)is dict and type(after)is dict and set(before)==set(after))
    require(set(before)>={'configuration','runtime','unitFilesActual','units','rows','startup','originals','backup','extraDurable','pid1'})
    for k in before.keys()-{'configuration','runtime','unitFilesActual'}:require(before[k]==after[k])
    old_files=before['unitFilesActual'];new_files=after['unitFilesActual']
    require(type(old_files)is dict and new_files=={k:v for k,v in old_files.items()if k!=TARGET})
    old_tree=before['runtime'];new_tree=after['runtime']
    require(type(old_tree)is dict and set(new_tree)==set(old_tree)-{TARGET}and ROOT in new_tree)
    item=old_tree[TARGET];require(item['sha256']==SHA and item['metadata'][2:7]==[0,0,stat.S_IFREG|0o644,1,647])
    if TARGET in old_files:require(old_files[TARGET]==item['metadata']+[item['sha256']])
    for path,v in new_tree.items():
        if path!=ROOT:require(v==old_tree[path])
        else:
            a=old_tree[path]['metadata'];b=v['metadata']
            require(v['sha256']==old_tree[path]['sha256']and len(a)==len(b)==9 and a[:6]==b[:6]and b[6]>=0 and b[7]>=a[7]and b[8]>=a[8])
            require(b[2:6]==[0,0,stat.S_IFDIR|0o755,2])
    old=before['configuration'];new=after['configuration'];require(type(old)is dict and set(old)==set(new)and len(old)==10)
    for u,a in old.items():
        b=new[u];require(type(a)is dict and type(b)is dict and set(a)==set(b)==FIELDS and all(type(v)is str for v in (*a.values(),*b.values())))
        allowed={'ExecStart','DropInPaths'}if u==MORNING else {'ExecStart','ExecStop'}
        require(all(a[k]==b[k]for k in FIELDS-allowed))
        for k in ('ExecStart','ExecStop'):
            if a[k]==b[k]:continue
            x=parse(a[k]);y=parse(b[k]);require(x is not None and y is not None)
            if u==MORNING and k=='ExecStart':
                suffix=' --resume '+RUN
                require(x[1].endswith(suffix)and y[:3]==(x[0],x[1][:-len(suffix)],x[2])and y[3:]==EMPTY)
            else:require(x[:3]==y[:3]and y[3:]==EMPTY)
        if u==MORNING:
            require(a['ExecStart']!=b['ExecStart'])
            parts=a['DropInPaths'].split();require(parts.count(TARGET)==1 and parts[-1]==TARGET and b['DropInPaths']==' '.join(parts[:-1]))
    return True

def metadata(fd):
    s=os.fstat(fd);return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]

def retire_entry(parent,expected_parent,expected_file):
    """Real typed held FD operation. Unknown partial is retained, never retried."""
    require(type(parent)is int and parent>=0 and type(expected_parent)is list and type(expected_file)is list and len(expected_parent)==9 and len(expected_file)==10)
    require(metadata(parent)==expected_parent and expected_parent[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(parent)and os.listdir(parent)==[NAME])
    fd=os.open(NAME,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
    try:
        a=metadata(fd);require(a==expected_file[:9]and a[2:7]==[0,0,stat.S_IFREG|0o644,1,647]and expected_file[9]==SHA and not os.listxattr(fd))
        data=os.read(fd,648);require(len(data)==647 and hashlib.sha256(data).hexdigest()==SHA and metadata(fd)==a)
        named=os.stat(NAME,dir_fd=parent,follow_symlinks=False);require((named.st_dev,named.st_ino)==tuple(a[:2])and metadata(parent)==expected_parent)
        os.unlink(NAME,dir_fd=parent);os.fsync(parent)
        require(os.listdir(parent)==[]and metadata(fd)[:5]==a[:5]and metadata(fd)[5]==0)
    finally:os.close(fd)
