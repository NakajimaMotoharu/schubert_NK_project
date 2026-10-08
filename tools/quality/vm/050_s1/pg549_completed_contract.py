"""SS343 SSC190 completed code-only finite delta, independent of Production codecs."""
import hashlib
import re
import stat
import uuid

OLD='/opt/schubert-nk/releases/0.1.0-PG495'
NEXT='/opt/schubert-nk/releases/0.1.0-PG548'
STARTUP='/run/schubert-nk/startup'
EPOCH=STARTUP+'/epoch.current'
APPROVAL='/etc/schubert-nk/release-approval/current'
DIGEST='a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b'
NEW_APPROVAL=('NKRELEASEAPPROVAL1\nversion=0.1.0-PG548\nmanifest_sha256='+DIGEST+'\n').encode()


def require(value):
    if not value:raise ValueError('completed code-only contract refused')


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
    require(value['boot_id']=='cc9ed874-7f4f-450e-a188-8de1e42c8441' and value['run_id']=='91a748b4-1abe-484c-9682-44f46429b324' and value['activation_id']=='179758d2-5b77-443a-a743-bf0065e732ea' and value['cutoff_utc']=='2026-10-06T12:06:14.564793Z')
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
    require(a[0]==b[0] and a[1]!=b[1] and b[2:7]==[0,0,stat.S_IFREG|mode,1,len(raw)])


def changed_only(before,after,old_epoch,new_epoch):
    require(type(before)is dict and type(after)is dict and set(before)==set(after))
    require(before['current']==OLD and after['current']==NEXT)
    for key in before.keys()-{'current','startup','approval'}:require(before[key]==after[key])
    old,new=before['startup'],after['startup'];require(set(old)==set(new) and EPOCH in old and STARTUP in old)
    for name,value in old.items():
        if name==EPOCH:replacement(value,new[name],new_epoch,0o600)
        elif name==STARTUP:
            require(value['metadata'][:7]==new[name]['metadata'][:7] and value['sha256']==new[name]['sha256'])
        else:require(value==new[name])
    replacement(before['approval'],after['approval'],NEW_APPROVAL,0o400)
    epoch_transition(old_epoch,new_epoch)
    return True
