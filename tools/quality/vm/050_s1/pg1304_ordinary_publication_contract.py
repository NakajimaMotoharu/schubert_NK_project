"""SSC262 independent finite ordinary-ISSUED/DONE oracle; never authority or IO."""
import hashlib
import stat
import uuid
from pg1083_cold_publication_contract import _row,_changed_time

STARTUP='/run/schubert-nk/startup'
APPROVAL='/etc/schubert-nk/release-approval'
CURRENT='/opt/schubert-nk'
PART=CURRENT+'/pg1305-current.part'
OLD_LINK='/opt/schubert-nk/releases/0.1.0-PG1068'
NEW_LINK='/opt/schubert-nk/releases/0.1.0-PG1292'
OLD_APPROVAL=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1068\nmanifest_sha256=0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d\n'
NEW_APPROVAL=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1292\nmanifest_sha256=ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99\n'
PHASES=('before','epoch','approval','link-staged','exchanged','old-linked-private','release')


def require(value):
    if not value:raise ValueError('ordinary finite publication refused')


def epoch_bytes(value):
    require(type(value)is str)
    try:parsed=uuid.UUID(value)
    except (ValueError,AttributeError):raise ValueError('canonical fresh epoch refused')from None
    require(str(parsed)==value and parsed.version==4 and parsed.variant==uuid.RFC_4122 and value not in (
      'cbca8738-3b24-4090-b77c-bf029677cdd6','9f651096-aef9-4fba-90b0-a653e99f035a','27accac0-c118-4c98-9244-02625a2d88a7'))
    return ('NKEPOCH1\nstate=INVALID\nboot_id=cbca8738-3b24-4090-b77c-bf029677cdd6\nepoch_id='+value+
      '\nrun_id=9f651096-aef9-4fba-90b0-a653e99f035a\ncutoff_utc=2026-10-10T20:03:22.718197Z\nactivation_id=27accac0-c118-4c98-9244-02625a2d88a7\npermit_sha256=-\n').encode('ascii')


def canonical_epoch(raw):
    require(type(raw)is bytes)
    try:fields=raw.decode('ascii').splitlines();expected=epoch_bytes(fields[3].removeprefix('epoch_id='))
    except (UnicodeError,IndexError,ValueError):raise ValueError('canonical epoch required')from None
    require(raw==expected)


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


def verify(before,actual,phase,epoch,begin,end):
    require(type(phase)is str and phase in PHASES and type(begin)is int and type(end)is int and 0<=begin<=end)
    require(type(before)is dict and type(actual)is dict and set(before)==set(actual)=={STARTUP,APPROVAL,CURRENT})
    if phase!='before':canonical_epoch(epoch)
    for root,entries in before.items():
        require(type(entries)is dict and entries and root in entries and type(actual[root])is dict)
        for path,row in entries.items():
            require(type(path)is str and(path==root or path.startswith(root+'/')));_row(row)
        m=_row(entries[root]);require(m[0]>0 and m[1]>0 and m[2]==0 and stat.S_ISDIR(m[4])and entries[root]['target']is None and entries[root]['sha256']is None and entries[root]['acl']==[])
        require((m[3],stat.S_IMODE(m[4]))==((986,0o750)if root==CURRENT else(0,0o700)))
    require(STARTUP+'/epoch.current'in before[STARTUP]and len(before[STARTUP])>2)
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
            directory=(path==STARTUP and phase!='before'or path==APPROVAL and phase in PHASES[2:]or path==CURRENT and phase in PHASES[3:])
            if directory:
                require(m[:7]==f[:7]and row['sha256']==fixed['sha256']and row['target']==fixed['target']and row['acl']==fixed['acl'])
                _changed_time(m,begin,end)
            elif path==STARTUP+'/epoch.current'and phase!='before':new_entry(row,fixed,stat.S_IFREG|0o600,epoch,begin,end)
            elif path==APPROVAL+'/current'and phase in PHASES[2:]:new_entry(row,fixed,stat.S_IFREG|0o400,NEW_APPROVAL,begin,end)
            elif path==CURRENT+'/current'and phase in PHASES[4:]:new_entry(row,fixed,stat.S_IFLNK|0o777,NEW_LINK.encode('ascii'),begin,end)
            else:require(row==fixed)
    return True


def verify_retained(path,fixed,observed,phase,actual,begin,end):
    require(type(path)is str and type(phase)is str and phase in PHASES and type(begin)is int and type(end)is int and 0<=begin<=end)
    old=_row(fixed);now=_row(observed)
    regular_replaced=(path==STARTUP+'/epoch.current'and phase!='before'or path==APPROVAL+'/current'and phase in PHASES[2:])
    if regular_replaced:
        require(stat.S_ISREG(old[4])and now[:5]==old[:5]and now[5]==0 and now[6:8]==old[6:8]and begin<=now[8]<=end)
        require(observed['sha256']==fixed['sha256']and observed['target']==fixed['target']is None and observed['acl']==fixed['acl']==[])
    elif path==CURRENT+'/current'and phase in PHASES[4:]:moved_old_link(fixed,observed,begin,end)
    elif path in (STARTUP,APPROVAL,CURRENT):
        require(type(actual)is dict and path in actual and path in actual[path]and observed==actual[path][path])
    else:require(fixed==observed)
    return True
