"""Appended to closed actual861 snapshot primitives; fixed child Ref/FD scope."""
import sys,time,uuid
phase='before';expected_epoch=None
SAVE=None
def validate_current(value,base,runtime):
    assert runtime==[] and value['rows']==base['rows'] and len(value['rows'])==24 and len(value['rows']['schubert.batch_runs'])==564
    assert value['configuration']==base['configuration'] and all(len(v)==32 for v in value['configuration'].values())
    assert value['units']==base['units'] and finite_trees(base['trees'],value['trees'],phase,expected_epoch)
    assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862'if phase in ('after','release')else'/opt/schubert-nk/releases/0.1.0-PG832')
    s=current.lstat();assert stat.S_ISLNK(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o777 and s.st_nlink==1
class NamespaceFDs:
    def __init__(self):
        self.files=[]
        for name in ('/var/lib/schubert-nk/maintenance','/run/schubert-nk/startup','/etc/schubert-nk/release-approval','/opt/schubert-nk','/srv/schubert-nk/backup','/srv/schubert-nk/data/assets','/srv/schubert-nk/data/transfer','/etc/schubert-nk/credentials'):
            p=pathlib.Path(name);fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);a=metadata(os.fstat(fd));b=metadata(p.lstat());assert a==b
            assert stat.S_ISDIR(a[4]) and not p.is_symlink()
            if str(p)=='/opt/schubert-nk':assert a[2:6]==[0,986,stat.S_IFDIR|0o750,3]
            self.files.append((p,fd,a,sorted(os.listxattr(p))))
        self.check()
    def check(self):
        for p,fd,old,xattrs in self.files:
            a=metadata(os.fstat(fd));b=metadata(p.lstat());assert a==b and sorted(os.listxattr(p))==xattrs
            if str(p)in ('/run/schubert-nk/startup','/etc/schubert-nk/release-approval','/opt/schubert-nk'):assert a[:6]==old[:6]
            else:assert a==old
    def close(self):
        self.check()
        for p,fd,a,xattrs in reversed(self.files):os.close(fd)
def server_check(released=False):
    sql="select json_build_object('batch',exists(select 1 from pg_stat_activity where pid="+str(batch)+" and usename='schubert_batch' and datname='schubert_nk' and application_name='PG864-fixed-completed'),'schema',exists(select 1 from pg_stat_activity where pid="+str(schema)+" and usename='schubert_migration' and datname='schubert_nk' and application_name='PG864-fixed-snapshot'),'advisory',exists(select 1 from pg_locks where pid="+str(batch)+" and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock' and granted));"
    v=json.loads(subprocess.check_output(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],text=True));assert v=={'batch':not released,'schema':not released,'advisory':not released}
def expected():
    p=SAVE/'new-epoch.private';s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and s.st_size<1024
    data=p.read_bytes();lines=data.decode('ascii').splitlines();assert data==epoch_bytes(lines[3].removeprefix('epoch_id='));return data
def execute():
    global phase,expected_epoch,SAVE,batch,schema
    assert len(sys.argv)==4 and sys.argv[1].isdigit()and sys.argv[2].isdigit()
    batch=int(sys.argv[1]);schema=int(sys.argv[2]);assert batch>1 and schema>1 and batch!=schema
    SAVE=pathlib.Path(sys.argv[3]);assert str(SAVE)in ('/var/lib/pgpt-s1-preservation/pg864-prepare-ro-v1','/var/lib/pgpt-s1-preservation/pg864-verify-v1','/var/lib/pgpt-s1-preservation/pg864-activate-v1')
    s=SAVE.lstat();assert stat.S_ISDIR(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o700
    refs=StageReferences();refs.__enter__();fds=NamespaceFDs()
    server_check();first=protected();assert first==protected();fds.check()
    print('REF_READY',flush=True)
    for command in sys.stdin:
        action=command.removesuffix('\n');assert command==action+'\n' and action in ('before','epoch','approval','after','release')
        transitions={'before':{'before','epoch','release'},'epoch':{'approval'},'approval':{'after'},'after':{'after','release'}}
        assert action in transitions[phase]
        if action=='epoch':assert SAVE.name=='pg864-activate-v1';expected_epoch=expected()
        if action=='release'and phase=='before':assert SAVE.name!='pg864-activate-v1'
        phase=action if action!='release'or phase!='before'else 'before'
        server_check(action=='release');fds.check();value=protected();assert value==protected()
        if action=='release':
            refs.__exit__(None,None,None);fds.close();print('REF_RELEASED',flush=True);return
        print('REF_CHECKED',flush=True)
    raise ValueError('reference EOF refused')
if __name__=='__main__':
    try:execute()
    except BaseException as failure:
        print('PG864_REF_UNKNOWN type='+type(failure).__name__+' ownershipNotInferred=true',file=sys.stderr,flush=True)
        # Preserve all still-live objects/descriptors; never infer clean release after failure.
        while True:
            try:time.sleep(1)
            except BaseException:pass
