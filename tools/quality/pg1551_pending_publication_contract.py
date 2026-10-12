"""SS198/266 partial publication oracle. Existing INVALID/startup is immutable.

Reuse only pure row checks from SSC262, never its DONE/ISSUED authority or epoch
issuance. Actual byte/FD identities and full source trees remain in scope.
"""
import hashlib
import stat
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vm/050_s1'))
from pg1083_cold_publication_contract import _row,_changed_time

STARTUP='/run/schubert-nk/startup'
APPROVAL='/etc/schubert-nk/release-approval'
CURRENT='/opt/schubert-nk'
PART=CURRENT+'/pg1551-current.part'
OLD_LINK='/opt/schubert-nk/releases/0.1.0-PG1292'
NEW_LINK='/opt/schubert-nk/releases/0.1.0-PG1544'
OLD_APPROVAL=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1292\nmanifest_sha256=ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99\n'
NEW_APPROVAL=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1544\nmanifest_sha256=e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c\n'
PHASES=('before','approval','link-staged','exchanged','old-linked-private','release')

def require(v):
    if not v:raise ValueError('fixed partial code-only publication refused')

def new_entry(row,fixed,mode,body,begin,end):
    m=_row(row);old=_row(fixed)
    require(m[0]==old[0]and m[1]>0 and m[1]!=old[1]and m[2:7]==[0,0,mode,1,len(body)]and row['acl']==[])
    if stat.S_ISLNK(mode):require(row['sha256']is None and row['target']==body.decode('ascii'))
    else:require(row['target']is None and row['sha256']==hashlib.sha256(body).hexdigest())
    _changed_time(m,begin,end)

def moved_old_link(fixed,observed,begin,end):
    old=_row(fixed);now=_row(observed)
    require(now[:8]==old[:8]and stat.S_ISLNK(now[4])and now[5]==1 and observed['target']==fixed['target']==OLD_LINK and observed['sha256']is None and observed['acl']==fixed['acl']==[])
    require(begin<=now[8]<=end)

def verify(before,actual,phase,begin,end):
    require(type(phase)is str and phase in PHASES and type(begin)is int and type(end)is int and 0<=begin<=end)
    require(type(before)is dict and type(actual)is dict and set(before)==set(actual)=={STARTUP,APPROVAL,CURRENT})
    for root,entries in before.items():
        require(type(entries)is dict and entries and root in entries and type(actual[root])is dict)
        for path,row in entries.items():require(type(path)is str and(path==root or path.startswith(root+'/')));_row(row)
        m=_row(entries[root]);require(m[0]>0 and m[1]>0 and m[2]==0 and stat.S_ISDIR(m[4])and entries[root]['target']is None and entries[root]['sha256']is None and entries[root]['acl']==[])
        require((m[3],stat.S_IMODE(m[4]))==((986,0o750)if root==CURRENT else(0,0o700)))
    require(STARTUP+'/epoch.current'in before[STARTUP]and set(actual[STARTUP])==set(before[STARTUP]))
    require(APPROVAL+'/current'in before[APPROVAL]and CURRENT+'/current'in before[CURRENT])
    require(before[APPROVAL][APPROVAL+'/current']['sha256']==hashlib.sha256(OLD_APPROVAL).hexdigest())
    require(before[CURRENT][CURRENT+'/current']['target']==OLD_LINK and PART not in before[CURRENT])
    for root,old in before.items():
        now=actual[root];added={PART}if root==CURRENT and phase in ('link-staged','exchanged')else set()
        require(set(now)==set(old)|added)
        for path,row in now.items():
            m=_row(row)
            if path==PART:
                if phase=='link-staged':new_entry(row,old[CURRENT+'/current'],stat.S_IFLNK|0o777,NEW_LINK.encode('ascii'),begin,end)
                else:moved_old_link(old[CURRENT+'/current'],row,begin,end)
                continue
            fixed=old[path];f=_row(fixed)
            directory=(path==APPROVAL and phase in PHASES[1:]or path==CURRENT and phase in PHASES[2:])
            if directory:
                require(m[:7]==f[:7]and row['sha256']==fixed['sha256']and row['target']==fixed['target']and row['acl']==fixed['acl']);_changed_time(m,begin,end)
            elif path==APPROVAL+'/current'and phase in PHASES[1:]:new_entry(row,fixed,stat.S_IFREG|0o400,NEW_APPROVAL,begin,end)
            elif path==CURRENT+'/current'and phase in PHASES[3:]:new_entry(row,fixed,stat.S_IFLNK|0o777,NEW_LINK.encode('ascii'),begin,end)
            else:require(row==fixed)
    return True

def verify_retained(path,fixed,observed,phase,actual,begin,end):
    require(type(path)is str and type(phase)is str and phase in PHASES and type(begin)is int and type(end)is int and 0<=begin<=end)
    old=_row(fixed);now=_row(observed)
    if path==APPROVAL+'/current'and phase in PHASES[1:]:
        require(stat.S_ISREG(old[4])and now[:5]==old[:5]and now[5]==0 and now[6:8]==old[6:8]and begin<=now[8]<=end)
        require(observed['sha256']==fixed['sha256']and observed['target']==fixed['target']is None and observed['acl']==fixed['acl']==[])
    elif path==CURRENT+'/current'and phase in PHASES[3:]:moved_old_link(fixed,observed,begin,end)
    elif path in (APPROVAL,CURRENT):require(type(actual)is dict and path in actual and path in actual[path]and observed==actual[path][path])
    else:require(fixed==observed)
    return True
