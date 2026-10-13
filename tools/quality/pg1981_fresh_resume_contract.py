"""Exact sole runtime/argv delta, no old terminal or business result is rewritten."""
import hashlib
import stat

MORNING='schubert-nk-morning-controller.service'
RUNTIME='/run/systemd/system'
DIRECTORY=RUNTIME+'/'+MORNING+'.d'
NAME='zz-pg1980-once-resume.conf'
TARGET=DIRECTORY+'/'+NAME
RUN='4148e3e8-f107-431a-ab27-d6e6d1f1772e'
CLOSED=('n/a','n/a','0','(null)','0/0')


def configuration(expected,actual,parse,ordinary):
    if type(expected)is not dict or type(actual)is not dict or set(expected)!=set(actual):return False
    for unit,old in expected.items():
        new=actual[unit]
        if unit!=MORNING:
            if not ordinary(old,new,parse):return False
            continue
        if type(old)is not dict or type(new)is not dict or set(old)!=set(new)or len(old)!=32:return False
        if any(type(v)is not str for v in (*old.values(),*new.values())):return False
        if any(old[k]!=new[k]for k in old if k not in {'ExecStart','DropInPaths'}):return False
        before=parse(old['ExecStart']);after=parse(new['ExecStart'])
        if before is None or after is None or len(before)!=8 or len(after)!=8:return False
        if after[:3]!=(before[0],before[1]+' --resume '+RUN,before[2])or tuple(after[3:])!=CLOSED:return False
        if new['DropInPaths']!=old['DropInPaths']+' '+TARGET:return False
    return MORNING in expected


def runtime_tree(before,actual,dropin,lower_ns,upper_ns):
    if type(before)is not dict or type(actual)is not dict or set(before)!={RUNTIME,DIRECTORY}or set(actual)!=set(before)|{TARGET}:return False
    if type(dropin)is not bytes or not 0<len(dropin)<=4096 or type(lower_ns)is not int or type(upper_ns)is not int or not 0<=lower_ns<=upper_ns:return False
    if actual[RUNTIME]!=before[RUNTIME]:return False
    old,new=before[DIRECTORY],actual[DIRECTORY]
    for row in [old,new,actual[TARGET]]:
        if type(row)is not dict or set(row)!={'metadata','sha256'}or type(row['metadata'])is not list or len(row['metadata'])!=9 or any(type(v)is not int or v<0 for v in row['metadata']):return False
    left,right=old['metadata'],new['metadata']
    if left[2:6]!=[0,0,stat.S_IFDIR|0o755,2]or right[:6]!=left[:6]or right[6]<left[6]or old['sha256']is not None or new['sha256']is not None:return False
    if any(not max(left[i],lower_ns)<=right[i]<=upper_ns for i in [7,8]):return False
    file=actual[TARGET]['metadata']
    if file[0]!=left[0]or file[1]==left[1]or file[2:7]!=[0,0,stat.S_IFREG|0o644,1,len(dropin)]or any(not lower_ns<=file[i]<=upper_ns for i in [7,8]):return False
    return actual[TARGET]['sha256']==hashlib.sha256(dropin).hexdigest()
