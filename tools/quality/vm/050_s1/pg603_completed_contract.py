"""SS343 SSC227 current completed code-only finite delta, independent of Production codecs."""
import hashlib
import math
import re
import stat
import uuid

OLD='/opt/schubert-nk/releases/0.1.0-PG548'
NEXT='/opt/schubert-nk/releases/0.1.0-PG600'
STARTUP='/run/schubert-nk/startup'
EPOCH=STARTUP+'/epoch.current'
APPROVAL='/etc/schubert-nk/release-approval/current'
DIGEST='a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f'
NEW_APPROVAL=('NKRELEASEAPPROVAL1\nversion=0.1.0-PG600\nmanifest_sha256='+DIGEST+'\n').encode()
SNAPSHOT_FIELDS=frozenset('backup bootstrapOldProofs bootstrapTools configuration credentials dependencies native oldProofs originals parentPid1 pid1Stop rows runtime startup units current approval unitFiles caddyPre'.split())


def require(value):
    if not value:raise ValueError('completed code-only contract refused')


def same_value(left,right):
    if type(left)is not type(right):return False
    if isinstance(left,dict):
        return set(left)==set(right)and all(type(k)is str and same_value(left[k],right[k])for k in left)
    if isinstance(left,list):return len(left)==len(right)and all(same_value(a,b)for a,b in zip(left,right))
    if isinstance(left,float):return math.isfinite(left)and math.isfinite(right)and left==right
    return type(left)in(type(None),bool,int,str)and left==right


def epoch(raw):
    require(type(raw)is bytes and 0<len(raw)<=4096)
    rows=raw.decode('ascii').split('\n')
    keys=('state','boot_id','epoch_id','run_id','cutoff_utc','activation_id','permit_sha256')
    require(len(rows)==9 and rows[0]=='NKEPOCH1' and rows[-1]=='')
    value={}
    for row,key in zip(rows[1:-1],keys):
        require(row.startswith(key+'='));value[key]=row[len(key)+1:]
    for key in ('boot_id','epoch_id','run_id','activation_id'):
        identifier=uuid.UUID(value[key]);require(identifier.int!=0 and str(identifier)==value[key])
    require(value['boot_id']=='cc9ed874-7f4f-450e-a188-8de1e42c8441' and value['run_id']=='b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e' and value['activation_id']=='57f0e73d-d334-4882-9284-04246011da54' and value['cutoff_utc']=='2026-10-08T07:36:21.802335Z')
    return value


def epoch_transition(before,after):
    old,new=epoch(before),epoch(after)
    require(old['state']=='ISSUED' and re.fullmatch('[0-9a-f]{64}',old['permit_sha256'])is not None)
    require(new['state']=='INVALID' and new['permit_sha256']=='-' and uuid.UUID(new['epoch_id']).version==4 and new['epoch_id']!=old['epoch_id'])
    require(all(old[k]==new[k]for k in old if k not in('state','epoch_id','permit_sha256')))


def replacement(old,new,raw,mode):
    require(type(old)is dict and type(new)is dict and set(old)==set(new)=={'metadata','sha256'})
    require(new['sha256']==hashlib.sha256(raw).hexdigest())
    a,b=old['metadata'],new['metadata']
    require(type(a)is list and type(b)is list and len(a)==len(b)==9 and all(type(v)is int for v in a+b))
    require(a[0]>0 and a[0]==b[0]and a[1]>0 and b[1]>0 and a[1]!=b[1])
    require(a[2:6]==[0,0,stat.S_IFREG|mode,1]and b[2:7]==[0,0,stat.S_IFREG|mode,1,len(raw)])


def changed_only(before,after,old_epoch,new_epoch):
    require(type(before)is dict and type(after)is dict and set(before)==set(after)==SNAPSHOT_FIELDS)
    require(before['runtime']is None and after['runtime']is None and all(v is not None for k,v in before.items()if k!='runtime')and all(v is not None for k,v in after.items()if k!='runtime'))
    require(before['current']==OLD and after['current']==NEXT)
    for key in before.keys()-{'current','startup','approval'}:require(same_value(before[key],after[key]))
    old,new=before['startup'],after['startup'];require(set(old)==set(new) and EPOCH in old and STARTUP in old)
    require(type(old_epoch)is bytes and old[EPOCH]['sha256']==hashlib.sha256(old_epoch).hexdigest()and old[EPOCH]['metadata'][6]==len(old_epoch))
    for name,value in old.items():
        if name==EPOCH:replacement(value,new[name],new_epoch,0o600)
        elif name==STARTUP:
            require(value['metadata'][:7]==new[name]['metadata'][:7] and value['sha256']==new[name]['sha256'])
        else:require(same_value(value,new[name]))
    replacement(before['approval'],after['approval'],NEW_APPROVAL,0o400)
    epoch_transition(old_epoch,new_epoch)
    return True


def phase_action(state,action):
    transitions={'READY':{'before':'READY','after':'CHECKED'},'CHECKED':{'release':'CLOSED'}}
    require(type(state)is str and type(action)is str and action in transitions.get(state,{}))
    return transitions[state][action]
