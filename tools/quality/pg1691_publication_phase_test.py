"""Independent new-cohort literal seven-phase and retained-inode vectors."""
import copy
import hashlib
import stat
import types
import unittest
from pg1691_completed_ordinary_publication_sources import sources

S='/run/schubert-nk/startup';A='/etc/schubert-nk/release-approval';C='/opt/schubert-nk';P=C+'/pg1692-current.part'
OLD=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1544\nmanifest_sha256=e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c\n'
NEW=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1638\nmanifest_sha256=195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1\n'
E=b'NKEPOCH1\nstate=INVALID\nboot_id=3d69f5af-6bac-46b1-a540-7591c4a79a0d\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=0be226b1-bbb7-43d3-aa9e-59d0bda70f9a\ncutoff_utc=2026-10-12T06:23:13.176261Z\nactivation_id=d28eead2-941c-4b97-9747-1758c0809e29\npermit_sha256=-\n'
PHASES=('before','epoch','approval','link-staged','exchanged','old-linked-private','release')


def row(dev,ino,mode,size,sha=None,target=None,gid=0,links=1,time=10):
    return dict(metadata=[dev,ino,0,gid,mode,links,size,time,time],sha256=sha,target=target,acl=[])


def fixture():
    return {S:{S:row(28,1,stat.S_IFDIR|0o700,260,links=2),S+'/epoch.current':row(28,2,stat.S_IFREG|0o600,318,'a'*64),S+'/opaque-old-owner':row(28,3,stat.S_IFREG|0o600,123,'b'*64)},A:{A:row(7,4,stat.S_IFDIR|0o700,4096,links=2),A+'/current':row(7,5,stat.S_IFREG|0o400,len(OLD),hashlib.sha256(OLD).hexdigest())},C:{C:row(7,6,stat.S_IFDIR|0o750,4096,gid=986,links=3),C+'/current':row(7,7,stat.S_IFLNK|0o777,38,target='/opt/schubert-nk/releases/0.1.0-PG1544'),C+'/releases':row(7,8,stat.S_IFDIR|0o750,4096,gid=986,links=5)}}


def actual(phase):
    v=fixture();i=PHASES.index(phase)
    if i>=1:
        v[S][S]['metadata'][7:]=[21,21]
        v[S][S+'/epoch.current']=row(28,9,stat.S_IFREG|0o600,len(E),hashlib.sha256(E).hexdigest(),time=21)
    if i>=2:
        v[A][A]['metadata'][7:]=[22,22]
        v[A][A+'/current']=row(7,10,stat.S_IFREG|0o400,len(NEW),hashlib.sha256(NEW).hexdigest(),time=22)
    if i>=3:v[C][C]['metadata'][7:]=[23,23]
    if i==3:v[C][P]=row(7,11,stat.S_IFLNK|0o777,38,target='/opt/schubert-nk/releases/0.1.0-PG1638',time=23)
    if i>=4:v[C][C+'/current']=row(7,11,stat.S_IFLNK|0o777,38,target='/opt/schubert-nk/releases/0.1.0-PG1638',time=23)
    if i==4:
        v[C][P]=copy.deepcopy(fixture()[C][C+'/current']);v[C][P]['metadata'][8]=24
    return v


class PublicationPhaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle=types.ModuleType('fixed_new_publication')
        exec(compile(sources()['pg1691_ordinary_publication_contract.py'],'<new fixed actual contract>','exec'),cls.oracle.__dict__)

    def test_independent_epoch_all_seven_phases(self):
        self.assertEqual(E,self.oracle.epoch_bytes('11111111-2222-4333-8444-555555555555'))
        self.assertEqual(PHASES,self.oracle.PHASES)
        for phase in PHASES:self.assertTrue(self.oracle.verify(fixture(),actual(phase),phase,E,20,30))
        for bad in [None,True,b'',E.replace(b'state=INVALID',b'state=ISSUED'),E.replace(b'3d69f5af',b'cbca8738'),E+b'\n']:
            with self.assertRaises(ValueError):self.oracle.canonical_epoch(bad)

    def test_each_field_and_extra_unknown_rejected(self):
        for phase in PHASES:
            good=actual(phase)
            for root in good:
                for path in good[root]:
                    for index in range(9):
                        bad=copy.deepcopy(good);bad[root][path]['metadata'][index]+=100
                        fresh=(path==S+'/epoch.current'and phase!='before'or path==A+'/current'and PHASES.index(phase)>=2 or path==C+'/current'and PHASES.index(phase)>=4 or path==P and phase=='link-staged')
                        if index==1 and fresh:bad[root][path]['metadata'][index]=fixture()[root].get(path,fixture()[C][C+'/current'])['metadata'][index]
                        with self.assertRaises(ValueError):self.oracle.verify(fixture(),bad,phase,E,20,30)
            bad=copy.deepcopy(good);bad[S][S+'/foreign']=row(28,999,stat.S_IFREG|0o600,1,'c'*64)
            with self.assertRaises(ValueError):self.oracle.verify(fixture(),bad,phase,E,20,30)

    def test_retained_unlinked_old_regular_inode(self):
        fixed=fixture()[A][A+'/current'];observed=copy.deepcopy(fixed);observed['metadata'][5]=0;observed['metadata'][8]=22
        self.assertTrue(self.oracle.verify_retained(A+'/current',fixed,observed,'approval',actual('approval'),20,30))
        for index in [0,1,2,3,4,5,6,7,8]:
            bad=copy.deepcopy(observed);bad['metadata'][index]+=100
            with self.assertRaises(ValueError):self.oracle.verify_retained(A+'/current',fixed,bad,'approval',actual('approval'),20,30)


if __name__=='__main__':unittest.main()
