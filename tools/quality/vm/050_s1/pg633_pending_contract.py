"""SS343 SSC228 current pending code-only finite delta, independent of Production codecs."""
import hashlib
import math
import stat

OLD='/opt/schubert-nk/releases/0.1.0-PG621'
NEXT='/opt/schubert-nk/releases/0.1.0-PG631'
STARTUP='/run/schubert-nk/startup'
EPOCH=STARTUP+'/epoch.current'
APPROVAL='/etc/schubert-nk/release-approval/current'
DIGEST='57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'
NEW_APPROVAL=('NKRELEASEAPPROVAL1\nversion=0.1.0-PG631\nmanifest_sha256='+DIGEST+'\n').encode()
SNAPSHOT_FIELDS=frozenset('backup bootstrapOldProofs bootstrapTools configuration credentials dependencies native oldProofs originals parentPid1 pid1Stop rows runtime startup units current approval unitFiles caddyPre'.split())


def require(value):
    if not value:raise ValueError('pending code-only contract refused')


def same_value(left,right):
    if type(left)is not type(right):return False
    if isinstance(left,dict):
        return set(left)==set(right)and all(type(k)is str and same_value(left[k],right[k])for k in left)
    if isinstance(left,list):return len(left)==len(right)and all(same_value(a,b)for a,b in zip(left,right))
    if isinstance(left,float):return math.isfinite(left)and math.isfinite(right)and left==right
    return type(left)in(type(None),bool,int,str)and left==right


def replacement(old,new,raw,mode):
    require(type(old)is dict and type(new)is dict and set(old)==set(new)=={'metadata','sha256'})
    require(new['sha256']==hashlib.sha256(raw).hexdigest())
    a,b=old['metadata'],new['metadata']
    require(type(a)is list and type(b)is list and len(a)==len(b)==9 and all(type(v)is int for v in a+b))
    require(a[0]>0 and a[0]==b[0]and a[1]>0 and b[1]>0 and a[1]!=b[1])
    require(a[2:6]==[0,0,stat.S_IFREG|mode,1]and b[2:7]==[0,0,stat.S_IFREG|mode,1,len(raw)])


def changed_only(before,after):
    require(type(before)is dict and type(after)is dict and set(before)==set(after)==SNAPSHOT_FIELDS)
    require(before['runtime']is None and after['runtime']is None and all(v is not None for k,v in before.items()if k!='runtime')and all(v is not None for k,v in after.items()if k!='runtime'))
    require(before['current']==OLD and after['current']==NEXT)
    for key in before.keys()-{'current','approval'}:require(same_value(before[key],after[key]))
    replacement(before['approval'],after['approval'],NEW_APPROVAL,0o400)
    return True


def phase_action(state,action):
    transitions={'READY':{'before':'READY','after':'CHECKED'},'CHECKED':{'release':'CLOSED'}}
    require(type(state)is str and type(action)is str and action in transitions.get(state,{}))
    return transitions[state][action]
