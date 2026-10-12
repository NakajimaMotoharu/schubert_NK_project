"""Handwritten six-phase expected snapshots, startup is never changed."""
import copy
import hashlib
import stat
import unittest
from pg1551_pending_publication_contract import verify,verify_retained

S='/run/schubert-nk/startup';A='/etc/schubert-nk/release-approval';C='/opt/schubert-nk';P=C+'/pg1551-current.part'
OLD=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1292\nmanifest_sha256=ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99\n'
NEW=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1544\nmanifest_sha256=e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c\n'
PHASES=['before','approval','link-staged','exchanged','old-linked-private','release']
OLDLINK='/opt/schubert-nk/releases/0.1.0-PG1292';NEWLINK='/opt/schubert-nk/releases/0.1.0-PG1544'

def row(dev,ino,mode,size,sha=None,target=None,gid=0,links=1,time=10):
    return {'metadata':[dev,ino,0,gid,mode,links,size,time,time],'sha256':sha,'target':target,'acl':[]}

def before():
    return {S:{S:row(28,1,stat.S_IFDIR|0o700,260,links=2),S+'/epoch.current':row(28,2,stat.S_IFREG|0o600,318,'a'*64),S+'/former.permit':row(28,3,stat.S_IFREG|0o600,123,'b'*64)},A:{A:row(7,4,stat.S_IFDIR|0o700,4096,links=2),A+'/current':row(7,5,stat.S_IFREG|0o400,len(OLD),hashlib.sha256(OLD).hexdigest())},C:{C:row(7,6,stat.S_IFDIR|0o750,4096,gid=986,links=3),C+'/current':row(7,7,stat.S_IFLNK|0o777,len(OLDLINK),target=OLDLINK),C+'/releases':row(7,8,stat.S_IFDIR|0o750,4096,gid=986,links=5)}}

def actual(phase):
    v=before();i=PHASES.index(phase)
    if i>=1:v[A][A]['metadata'][7:]=[22,22];v[A][A+'/current']=row(7,10,stat.S_IFREG|0o400,len(NEW),hashlib.sha256(NEW).hexdigest(),time=22)
    if i>=2:v[C][C]['metadata'][7:]=[23,23]
    if i==2:v[C][P]=row(7,11,stat.S_IFLNK|0o777,len(NEWLINK),target=NEWLINK,time=23)
    if i>=3:v[C][C+'/current']=row(7,11,stat.S_IFLNK|0o777,len(NEWLINK),target=NEWLINK,time=23)
    if i==3:v[C][P]=copy.deepcopy(before()[C][C+'/current']);v[C][P]['metadata'][8]=24
    return v

class PendingOracleTest(unittest.TestCase):
    def test_all_six_phases_keep_startup_identical(self):
        for p in PHASES:self.assertTrue(verify(before(),actual(p),p,20,30));self.assertEqual(actual(p)[S],before()[S])

    def test_every_metadata_acl_unknown_entry_and_existing_epoch_mutation(self):
        for phase in PHASES:
            for root in [S,A,C]:
                for path in actual(phase)[root]:
                    for i in range(9):
                        v=actual(phase);v[root][path]['metadata'][i]+=100
                        fresh=(path==A+'/current'and phase!='before'or path==C+'/current'and phase in PHASES[3:]or path==P and phase=='link-staged')
                        if i==1 and fresh:v[root][path]['metadata'][1]=before()[root][C+'/current'if path==P else path]['metadata'][1]
                        with self.assertRaises(ValueError):verify(before(),v,phase,20,30)
                    v=actual(phase);v[root][path]['acl']=['foreign']
                    with self.assertRaises(ValueError):verify(before(),v,phase,20,30)
                v=actual(phase);v[root][root+'/foreign']=copy.deepcopy(v[root][root])
                with self.assertRaises(ValueError):verify(before(),v,phase,20,30)
            for path in [S+'/epoch.current',S+'/former.permit']:
                v=actual(phase);v[S][path]['sha256']='0'*64
                with self.assertRaises(ValueError):verify(before(),v,phase,20,30)

    def test_old_unlinked_approval_and_preserved_link_not_epoch(self):
        for phase in PHASES[1:]:
            for root,path in [(A,A+'/current'),(C,C+'/current')]:
                fixed=before()[root][path];observed=copy.deepcopy(fixed)
                if root==A:observed['metadata'][5]=0;observed['metadata'][8]=24
                elif phase in PHASES[3:]:observed['metadata'][8]=24
                self.assertTrue(verify_retained(path,fixed,observed,phase,actual(phase),20,30))
                for i in range(9):
                    bad=copy.deepcopy(observed);bad['metadata'][i]+=100
                    with self.assertRaises(ValueError):verify_retained(path,fixed,bad,phase,actual(phase),20,30)
        fixed=before()[S][S+'/epoch.current'];bad=copy.deepcopy(fixed);bad['metadata'][5]=0
        with self.assertRaises(ValueError):verify_retained(S+'/epoch.current',fixed,bad,'release',actual('release'),20,30)

    def test_unknown_order_null_and_foreign_pointer(self):
        for p in [None,'epoch','cold','unknown',[]]:
            with self.assertRaises(ValueError):verify(before(),actual('approval'),p,20,30)
        for p in ['before','exchanged','release']:
            with self.assertRaises(ValueError):verify(before(),actual('link-staged'),p,20,30)
        for v in [None,{},dict(before(),**{S:{}})]:
            with self.assertRaises(ValueError):verify(v,actual('release'),'release',20,30)
        v=actual('release');v[C][C+'/current']['target']='/tmp/foreign'
        with self.assertRaises(ValueError):verify(before(),v,'release',20,30)

if __name__=='__main__':unittest.main()
