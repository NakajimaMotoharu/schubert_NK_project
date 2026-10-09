"""SSC242/DEP864001: finite completed-INVALID publication; no generic repair."""
import hashlib,stat,uuid
STARTUP='/run/schubert-nk/startup';APPROVAL='/etc/schubert-nk/release-approval/current'
OLD_EPOCH='8b153538-1523-4987-a456-6cbea0d345ee'
NEW_APPROVAL=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG862\nmanifest_sha256=20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe\n'
def epoch_bytes(epoch):
    value=uuid.UUID(epoch)
    if str(value)!=epoch or value.version!=4 or value.variant!=uuid.RFC_4122 or epoch==OLD_EPOCH:raise ValueError('fresh epoch refused')
    return ('NKEPOCH1\nstate=INVALID\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id='+epoch+'\nrun_id=9de2d03c-28c7-4647-97d9-c66ace06048c\ncutoff_utc=2026-10-09T05:42:22.532331Z\nactivation_id=021111b4-6de5-4733-917d-5ac176240ffc\npermit_sha256=-\n').encode('ascii')
def finite_trees(old,new,phase,expected_epoch):
    if phase not in ('before','epoch','approval','after','release') or not isinstance(old,dict)or not isinstance(new,dict)or set(old)!=set(new):return False
    if phase!='before':
        try:
            fields=expected_epoch.decode('ascii').splitlines();canonical=epoch_bytes(fields[3].removeprefix('epoch_id='))
            if expected_epoch!=canonical:return False
        except (ValueError,TypeError,AttributeError,IndexError,UnicodeError):return False
    for root,entries in old.items():
        if not isinstance(entries,dict)or not isinstance(new[root],dict)or set(entries)!=set(new[root]):return False
        for name,previous in entries.items():
            actual=new[root][name]
            changed_epoch=phase!='before' and name==STARTUP+'/epoch.current'
            changed_approval=phase in ('approval','after','release') and name==APPROVAL
            if changed_epoch or changed_approval:
                expected=expected_epoch if changed_epoch else NEW_APPROVAL
                try:
                    m=actual['metadata'];oldm=previous['metadata']
                    if len(m)!=9 or m[0]!=oldm[0]or m[2:7]!=[0,0,stat.S_IFREG|(0o600 if changed_epoch else 0o400),1,len(expected)]or actual['sha256']!=hashlib.sha256(expected).hexdigest():return False
                except (KeyError,TypeError,IndexError):return False
            elif phase!='before'and name==STARTUP or phase in ('approval','after','release')and name==str(APPROVAL.rsplit('/',1)[0]):
                try:
                    if actual['metadata'][:7]!=previous['metadata'][:7] or len(actual['metadata'])!=9 or actual['sha256']!=previous['sha256']:return False
                except (KeyError,TypeError):return False
            elif actual!=previous:return False
    return True
