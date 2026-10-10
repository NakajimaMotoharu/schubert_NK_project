import copy
import hashlib
import stat
import unittest
from pg1304_ordinary_publication_contract import verify,verify_retained,epoch_bytes,PHASES

S='/run/schubert-nk/startup';A='/etc/schubert-nk/release-approval';C='/opt/schubert-nk';P=C+'/pg1305-current.part'
OLD=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1068\nmanifest_sha256=0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d\n'
NEW=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1292\nmanifest_sha256=ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99\n'
E=b'NKEPOCH1\nstate=INVALID\nboot_id=cbca8738-3b24-4090-b77c-bf029677cdd6\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=9f651096-aef9-4fba-90b0-a653e99f035a\ncutoff_utc=2026-10-10T20:03:22.718197Z\nactivation_id=27accac0-c118-4c98-9244-02625a2d88a7\npermit_sha256=-\n'


def row(dev,ino,mode,size,sha=None,target=None,gid=0,links=1,time=10):
    return dict(metadata=[dev,ino,0,gid,mode,links,size,time,time],sha256=sha,target=target,acl=[])


def fixture():
    return {S:{S:row(28,1,stat.S_IFDIR|0o700,260,links=2),S+'/epoch.current':row(28,2,stat.S_IFREG|0o600,318,'a'*64),S+'/opaque-old-owner':row(28,3,stat.S_IFREG|0o600,123,'b'*64)},
      A:{A:row(7,4,stat.S_IFDIR|0o700,4096,links=2),A+'/current':row(7,5,stat.S_IFREG|0o400,len(OLD),hashlib.sha256(OLD).hexdigest())},
      C:{C:row(7,6,stat.S_IFDIR|0o750,4096,gid=986,links=3),C+'/current':row(7,7,stat.S_IFLNK|0o777,38,target='/opt/schubert-nk/releases/0.1.0-PG1068'),C+'/releases':row(7,8,stat.S_IFDIR|0o750,4096,gid=986,links=5)}}


def actual(phase):
    v=fixture();index=PHASES.index(phase)
    if index>=1:
        v[S][S]['metadata'][7:]=[21,21]
        v[S][S+'/epoch.current']=row(28,9,stat.S_IFREG|0o600,len(E),hashlib.sha256(E).hexdigest(),time=21)
    if index>=2:
        v[A][A]['metadata'][7:]=[22,22]
        v[A][A+'/current']=row(7,10,stat.S_IFREG|0o400,len(NEW),hashlib.sha256(NEW).hexdigest(),time=22)
    if index>=3:v[C][C]['metadata'][7:]=[23,23]
    if index==3:v[C][P]=row(7,11,stat.S_IFLNK|0o777,38,target='/opt/schubert-nk/releases/0.1.0-PG1292',time=23)
    if index>=4:
        v[C][C+'/current']=row(7,11,stat.S_IFLNK|0o777,38,target='/opt/schubert-nk/releases/0.1.0-PG1292',time=23)
    if index==4:
        v[C][P]=copy.deepcopy(fixture()[C][C+'/current']);v[C][P]['metadata'][8]=24
    return v


class OrdinaryFiniteOracleTest(unittest.TestCase):
    def test_independent_epoch_and_all_seven_phases(self):
        self.assertEqual(E,epoch_bytes('11111111-2222-4333-8444-555555555555'))
        for phase in PHASES:self.assertTrue(verify(fixture(),actual(phase),phase,E,20,30))

    def test_each_public_field_and_unknown_entry_negative(self):
        for phase in PHASES:
            for root in [S,A,C]:
                for path in actual(phase)[root]:
                    for index in range(9):
                        value=actual(phase);value[root][path]['metadata'][index]+=100
                        fresh=(path==S+'/epoch.current'and phase!='before'or path==A+'/current'and PHASES.index(phase)>=2 or path==C+'/current'and PHASES.index(phase)>=4 or path==P and phase=='link-staged')
                        # A kernel-selected fresh inode cannot be predicted from
                        # the old one. Test illegal old inode reuse; real caller
                        # additionally retains each actual new FD across phases.
                        if index==1 and fresh:
                            key=C+'/current'if path==P else path
                            value[root][path]['metadata'][1]=fixture()[root][key]['metadata'][1]
                        with self.assertRaises(ValueError):verify(fixture(),value,phase,E,20,30)
                    value=actual(phase);value[root][path]['acl']=['unexpected']
                    with self.assertRaises(ValueError):verify(fixture(),value,phase,E,20,30)
                value=actual(phase);value[root][root+'/outside']=copy.deepcopy(value[root][root])
                with self.assertRaises(ValueError):verify(fixture(),value,phase,E,20,30)

    def test_null_unknown_cold_shape_wrong_order_and_canonical_binding(self):
        for e in [None,b'',E+b'x',E.replace(b'20:03:22',b'20:03:23')]:
            with self.assertRaises(ValueError):verify(fixture(),actual('epoch'),'epoch',e,20,30)
        for before in [None,{},dict(fixture(),**{S:{S:fixture()[S][S]}})]:
            with self.assertRaises(ValueError):verify(before,actual('epoch'),'epoch',E,20,30)
        for phase in [None,'unknown','cold',[]]:
            with self.assertRaises(ValueError):verify(fixture(),actual('epoch'),phase,E,20,30)
        for phase in ['epoch','approval','exchanged','release']:
            with self.assertRaises(ValueError):verify(fixture(),actual('link-staged'),phase,E,20,30)
        for v in [None,'','00000000-0000-0000-0000-000000000000','9f651096-aef9-4fba-90b0-a653e99f035a']:
            with self.assertRaises(ValueError):epoch_bytes(v)

    def test_old_regular_unlinked_and_old_link_always_linked(self):
        before=fixture()
        for phase,path,root in [('epoch',S+'/epoch.current',S),('approval',A+'/current',A),('exchanged',C+'/current',C),('old-linked-private',C+'/current',C),('release',C+'/current',C)]:
            old=before[root][path];observed=copy.deepcopy(old);observed['metadata'][8]=24
            if root!=C:observed['metadata'][5]=0
            self.assertTrue(verify_retained(path,old,observed,phase,actual(phase),20,30))
            for index in range(9):
                bad=copy.deepcopy(observed);bad['metadata'][index]+=100
                with self.assertRaises(ValueError):verify_retained(path,old,bad,phase,actual(phase),20,30)
            bad=copy.deepcopy(observed);bad['sha256']='0'*64
            with self.assertRaises(ValueError):verify_retained(path,old,bad,phase,actual(phase),20,30)

    def test_pointer_hash_target_acl_and_row_schema_and_null_element(self):
        for root,path in [(S,S+'/epoch.current'),(A,A+'/current'),(C,C+'/current')]:
            for field,bad in [('sha256','0'*64),('target','/tmp/foreign'),('acl',['foreign'])]:
                value=actual('release');value[root][path][field]=bad
                with self.assertRaises(ValueError):verify(fixture(),value,'release',E,20,30)
            for bad in [None,[],{},dict(actual('release')[root][path],metadata=None),dict(actual('release')[root][path],metadata=[True]*9),dict(actual('release')[root][path],unknown='value')]:
                value=actual('release');value[root][path]=bad
                with self.assertRaises(ValueError):verify(fixture(),value,'release',E,20,30)
        for root in [S,A,C]:
            for bad in [None,[],{}, {'unknown':None}]:
                before=fixture();before[root]=bad
                with self.assertRaises(ValueError):verify(before,actual('release'),'release',E,20,30)
        for begin,end in [(None,30),(False,30),(-1,30),(31,30),(20,None),(20,True)]:
            with self.assertRaises(ValueError):verify(fixture(),actual('release'),'release',E,begin,end)

    def test_retained_parents_regular_foreign_fields_and_same_phase_stability(self):
        before=fixture();after=actual('release')
        for root in [S,A,C]:
            self.assertTrue(verify_retained(root,before[root][root],after[root][root],'release',after,20,30))
            with self.assertRaises(ValueError):verify_retained(root,before[root][root],after[root][root],'release',None,20,30)
        path=S+'/opaque-old-owner';fixed=before[S][path]
        self.assertTrue(verify_retained(path,fixed,copy.deepcopy(fixed),'release',after,20,30))
        bad=copy.deepcopy(fixed);bad['metadata'][8]+=1
        with self.assertRaises(ValueError):verify_retained(path,fixed,bad,'release',after,20,30)
        fixed=before[S][S+'/epoch.current'];observed=copy.deepcopy(fixed);observed['metadata'][5]=0;observed['metadata'][8]=24
        for field,bad in [('sha256','0'*64),('target','foreign'),('acl',['foreign'])]:
            changed=copy.deepcopy(observed);changed[field]=bad
            with self.assertRaises(ValueError):verify_retained(S+'/epoch.current',fixed,changed,'release',after,20,30)


if __name__=='__main__':unittest.main()
