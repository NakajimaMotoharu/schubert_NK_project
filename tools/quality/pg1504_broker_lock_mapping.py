"""SSC266 internal kernel proof: two journal FDs and one fixed JVM perfdata mmap.

No M/A proof relaxation: its locks still require actual owner FDs. This module
is data-only, never reads files or signals processes.
"""
import re

def require(v):
    if not v:raise ValueError('fixed broker kernel ownership refused')

def lock_keys(lines,pid):
    require(type(lines)is list and type(pid)is int and pid>1)
    result=[]
    for line in lines:
        require(type(line)is str)
        fields=line.split()
        if len(fields)==8 and fields[4]==str(pid):
            require(fields[1]in {'POSIX','FLOCK'} and fields[2:4]==['ADVISORY','WRITE'] and fields[6:]==['0','EOF'])
            device=fields[5].split(':');require(len(device)==3 and all(re.fullmatch(r'[0-9a-fA-F]+',v)is not None for v in device[:2])and device[2].isdigit())
            key=(int(device[0],16),int(device[1],16),int(device[2]));require(key[2]>0)
            result.append((fields[1],key))
    require(len(result)==3 and len(set(result))==3 and [k for k,_ in result].count('POSIX')==2 and [k for k,_ in result].count('FLOCK')==1)
    return sorted(result)

def fixed_mapping(lines,pid,key):
    require(type(lines)is list and type(pid)is int and pid>1 and type(key)is tuple and len(key)==3)
    found=[]
    for line in lines:
        require(type(line)is str);fields=line.split(None,5)
        if len(fields)>=5:
            dev=fields[3].split(':')
            require(len(dev)==2 and all(re.fullmatch(r'[0-9a-fA-F]+',v)is not None for v in dev)and fields[4].isdigit())
            actual=(int(dev[0],16),int(dev[1],16),int(fields[4]))
            if actual==key:found.append(fields)
    require(len(found)==1);v=found[0]
    require(len(v)==6 and v[1]=='rw-s'and v[2]=='00000000'and v[5]=='/tmp/hsperfdata_schubert-artemis/'+str(pid))
    span=v[0].split('-');require(len(span)==2 and all(re.fullmatch(r'[0-9a-fA-F]+',x)is not None for x in span)and int(span[0],16)>0 and int(span[1],16)-int(span[0],16)==32768)
    return {'key':key,'size':32768,'path':v[5]}

def validate(lines,pid,fd_keys,mappings):
    require(type(fd_keys)is list and all(type(k)is tuple and len(k)==3 and all(type(v)is int and v>=0 for v in k)for k in fd_keys))
    locks=lock_keys(lines,pid)
    for kind,key in locks:
        if kind=='POSIX':require(key in fd_keys)
        else:fixed_mapping(mappings,pid,key)
    return locks
