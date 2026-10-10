"""SSC249 independent finite cold-empty publication oracle; no IO or authority."""
import hashlib
import re
import stat
import uuid

STARTUP='/run/schubert-nk/startup'
APPROVAL='/etc/schubert-nk/release-approval'
CURRENT='/opt/schubert-nk'
OLD_LINK='/opt/schubert-nk/releases/0.1.0-PG932'
NEW_LINK='/opt/schubert-nk/releases/0.1.0-PG1068'
OLD_APPROVAL=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG932\nmanifest_sha256=b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524\n'
NEW_APPROVAL=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1068\nmanifest_sha256=0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d\n'


def epoch_bytes(value):
    if type(value)is not str:raise ValueError('fresh epoch refused')
    try:parsed=uuid.UUID(value)
    except (ValueError,AttributeError):raise ValueError('fresh epoch refused')from None
    if (str(parsed)!=value or parsed.version!=4 or parsed.variant!=uuid.RFC_4122
        or value in ('cbca8738-3b24-4090-b77c-bf029677cdd6','eeae04ea-713c-4f2d-888d-358fb4bed274','091663ce-1cf4-47e7-8311-218ebb0c8653')):
        raise ValueError('fresh epoch refused')
    return ('NKEPOCH1\nstate=INVALID\nboot_id=cbca8738-3b24-4090-b77c-bf029677cdd6\n'
      'epoch_id='+value+'\nrun_id=eeae04ea-713c-4f2d-888d-358fb4bed274\n'
      'cutoff_utc=2026-10-09T23:31:22.087768Z\nactivation_id=091663ce-1cf4-47e7-8311-218ebb0c8653\n'
      'permit_sha256=-\n').encode('ascii')


def _row(value):
    if type(value)is not dict or set(value)!={'metadata','sha256','target','acl'}:
        raise ValueError('finite row shape refused')
    m=value['metadata']
    if (type(m)is not list or len(m)!=9 or any(type(x)is not int or x<0 for x in m)
        or value['acl']!=[] or value['sha256']is not None and
        (type(value['sha256'])is not str or re.fullmatch('[0-9a-f]{64}',value['sha256'])is None)
        or value['target']is not None and type(value['target'])is not str):
        raise ValueError('finite row metadata refused')
    return m


def _changed_time(m,begin,end):
    if not begin<=m[7]<=end or not begin<=m[8]<=end:raise ValueError('finite mutation time refused')


def verify(before,actual,phase,epoch,begin_ns,end_ns):
    """All complete selected parent trees plus caller's separate immutable state.

    Caller independently proves before byte identity/security, tmpfs startup,
    whole immutable releases/originals/DB/Units/dispatch inhibition and own leases.
    This oracle never derives approved content from the actual new pointer.
    """
    if phase not in ('before','epoch','approval','after','release'):
        raise ValueError('finite phase refused')
    if (type(before)is not dict or type(actual)is not dict or set(before)!={STARTUP,APPROVAL,CURRENT}
        or set(actual)!=set(before)or type(begin_ns)is not int or type(end_ns)is not int
        or not 0<=begin_ns<=end_ns):
        raise ValueError('finite snapshot refused')
    if phase!='before':
        if type(epoch)is not bytes:raise ValueError('finite epoch refused')
        try:
            fields=epoch.decode('ascii').splitlines()
            canonical=epoch_bytes(fields[3].removeprefix('epoch_id='))
        except (UnicodeError,ValueError,IndexError):raise ValueError('finite epoch refused')from None
        if canonical!=epoch:raise ValueError('finite epoch refused')
    if any(type(before[root])is not dict or type(actual[root])is not dict for root in before):
        raise ValueError('finite tree refused')
    if set(before[STARTUP])!={STARTUP}:raise ValueError('cold startup not empty')
    for root,entries in before.items():
        if root not in entries:raise ValueError('finite parent missing')
        for path,value in entries.items():
            if type(path)is not str or path!=root and not path.startswith(root+'/'):
                raise ValueError('finite tree path refused')
            _row(value)
    if (APPROVAL+'/current'not in before[APPROVAL]or CURRENT+'/current'not in before[CURRENT]
        or before[APPROVAL][APPROVAL+'/current']['sha256']!=hashlib.sha256(OLD_APPROVAL).hexdigest()
        or before[CURRENT][CURRENT+'/current']['target']!=OLD_LINK):
        raise ValueError('fixed old pointers refused')
    for root,old in before.items():
        now=actual[root]
        if type(old)is not dict or type(now)is not dict:raise ValueError('finite tree refused')
        added={STARTUP+'/epoch.current'}if root==STARTUP and phase!='before'else set()
        if set(now)!=set(old)|added or root not in old:raise ValueError('finite tree entries refused')
        for path,row in now.items():
            m=_row(row)
            if path in added:
                if m[0]!=_row(old[root])[0]or m[2:7]!=[0,0,stat.S_IFREG|0o600,1,len(epoch)]or row['sha256']!=hashlib.sha256(epoch).hexdigest()or row['target']is not None:
                    raise ValueError('finite new epoch refused')
                _changed_time(m,begin_ns,end_ns);continue
            previous=old[path];fixed=_row(previous)
            directory_changed=(path==STARTUP and phase!='before'
              or path==APPROVAL and phase in ('approval','after','release')
              or path==CURRENT and phase in ('after','release'))
            approval_changed=path==APPROVAL+'/current'and phase in ('approval','after','release')
            link_changed=path==CURRENT+'/current'and phase in ('after','release')
            if directory_changed:
                size=fixed[6]+20 if path==STARTUP else fixed[6]
                if m[:6]!=fixed[:6]or m[6]!=size or row['sha256']!=previous['sha256']or row['target']!=previous['target']:
                    raise ValueError('finite parent effect refused')
                _changed_time(m,begin_ns,end_ns)
            elif approval_changed or link_changed:
                expected=NEW_APPROVAL if approval_changed else NEW_LINK.encode('ascii')
                mode=stat.S_IFREG|0o400 if approval_changed else stat.S_IFLNK|0o777
                if m[0]!=fixed[0]or m[1]==fixed[1]or m[2:7]!=[0,0,mode,1,len(expected)]:
                    raise ValueError('finite pointer identity refused')
                if approval_changed:
                    if row['sha256']!=hashlib.sha256(expected).hexdigest()or row['target']is not None:raise ValueError('finite approval refused')
                elif row['sha256']is not None or row['target']!=NEW_LINK:raise ValueError('finite current link refused')
                _changed_time(m,begin_ns,end_ns)
            elif row!=previous:raise ValueError('unexpected finite mutation refused')
    return True


def verify_retained(path,fixed,observed,phase,after,begin_ns,end_ns):
    """After verify(), check each still-held old inode without a silent rebase.

    Linked new objects are independently checked by the whole finite-tree oracle.
    Unrelated old objects must retain all nine metadata fields/content/ACL.
    """
    if type(path)is not str or phase not in ('before','epoch','approval','after','release'):
        raise ValueError('retained phase/path refused')
    old=_row(fixed);now=_row(observed)
    changed_directory=(path==STARTUP and phase!='before'
      or path==APPROVAL and phase in ('approval','after','release')
      or path==CURRENT and phase in ('after','release'))
    replaced=(path==APPROVAL+'/current'and phase in ('approval','after','release')
      or path==CURRENT+'/current'and phase in ('after','release'))
    if changed_directory:
        if type(after)is not dict or path not in after or path not in after[path]:
            raise ValueError('retained parent proof absent')
        if observed!=after[path][path]:raise ValueError('retained parent FD/link differs')
        size=old[6]+20 if path==STARTUP else old[6]
        if now[:6]!=old[:6]or now[6]!=size:raise ValueError('retained parent identity refused')
        _changed_time(now,begin_ns,end_ns)
    elif replaced:
        if now[:5]!=old[:5]or now[5]!=0 or now[6:8]!=old[6:8]or not begin_ns<=now[8]<=end_ns:
            raise ValueError('retained replaced inode refused')
        if observed['sha256']!=fixed['sha256']or observed['target']!=fixed['target']:
            raise ValueError('retained original bytes/link refused')
    elif observed!=fixed:raise ValueError('retained unrelated object changed')
    return True
