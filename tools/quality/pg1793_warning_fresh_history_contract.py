"""SSC280 structural history match; management identity remains fully immutable."""
import json
import stat
from pg1780_warning_live_peer_proof import validate_peers


def same(a,b):
    return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))


def match_parent_history(old,new):
    if type(old)is not dict or type(new)is not dict or set(old)!=set(new):raise ValueError('complete parent image required')
    if any(not same(old[k],new[k])for k in old if k!='fds'):raise ValueError('parent identity/authority changed')
    a=old.get('fds');b=new.get('fds')
    if type(a)is not dict or type(b)is not dict or set(a)!=set(b)or len(a)!=101:raise ValueError('exact original 101 FD set required')
    for fd,left in a.items():
        right=b[fd]
        if fd not in {'29','32'}:
            if not same(left,right):raise ValueError('nonshared FD changed')
            continue
        if type(left)is not dict or type(right)is not dict or set(left)!=set(right)or set(left)!={'metadata','target'}or left['target']!=right['target']or right['target']!='/run':raise ValueError('fixed shared directory only')
        x=left['metadata'];y=right['metadata']
        if type(x)not in (tuple,list)or type(y)not in (tuple,list)or len(x)!=9 or len(y)!=9 or any(type(v)is not int for v in [*x,*y]):raise ValueError('complete typed metadata9 required')
        if not stat.S_ISDIR(x[4])or not stat.S_ISDIR(y[4])or list(x[:7])!=list(y[:7])or any(y[i]<x[i]for i in [7,8]):raise ValueError('shared inode/attributes/time regression')
    return True


def match_peer_history(old,new):
    if type(old)is not dict or type(new)is not dict or set(old)!=set(new):raise ValueError('complete peer image required')
    if not same(old['activity'],new['activity']):raise ValueError('management activity changed')
    validate_peers(new['allPeers'],1)
    before=[b for b in old['bindings']if b.get('role')=='schubert_batch']
    after=[b for b in new['bindings']if b.get('role')=='schubert_batch']
    if len(before)!=1 or not same(before,after)or new.get('liveDaemonPeersPreserved')is not True:raise ValueError('management socket binding changed')
    # Normal service socket bindings themselves were freshly checked by same_peer.
    if len(new['bindings'])!=4:raise ValueError('every current service peer must be bound')
    return True
