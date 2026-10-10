"""Independent SS343 literal vectors, finite phases and metadata/entry counterexamples."""
import copy
import hashlib
import stat
import unittest
from pg1083_cold_publication_contract import verify,epoch_bytes,verify_retained

S='/run/schubert-nk/startup';A='/etc/schubert-nk/release-approval';C='/opt/schubert-nk'
OLD=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG932\nmanifest_sha256=b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524\n'
NEW=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG1068\nmanifest_sha256=0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d\n'
E=b'NKEPOCH1\nstate=INVALID\nboot_id=cbca8738-3b24-4090-b77c-bf029677cdd6\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=eeae04ea-713c-4f2d-888d-358fb4bed274\ncutoff_utc=2026-10-09T23:31:22.087768Z\nactivation_id=091663ce-1cf4-47e7-8311-218ebb0c8653\npermit_sha256=-\n'


def row(device,inode,mode,size,sha=None,target=None,gid=0,links=1,time=10):
    return {'metadata':[device,inode,0,gid,mode,links,size,time,time],'sha256':sha,'target':target,'acl':[]}


def fixture():
    return {S:{S:row(28,1,stat.S_IFDIR|0o700,40,links=2)},
      A:{A:row(7,2,stat.S_IFDIR|0o700,4096,links=2),A+'/current':row(7,3,stat.S_IFREG|0o400,len(OLD),hashlib.sha256(OLD).hexdigest())},
      C:{C:row(7,4,stat.S_IFDIR|0o750,4096,gid=986,links=3),C+'/current':row(7,5,stat.S_IFLNK|0o777,37,target='/opt/schubert-nk/releases/0.1.0-PG932'),C+'/releases':row(7,6,stat.S_IFDIR|0o750,4096,gid=986,links=4)}}


def actual(phase):
    v=fixture()
    if phase!='before':
        v[S][S]['metadata'][6:]=[60,21,21]
        v[S][S+'/epoch.current']=row(28,7,stat.S_IFREG|0o600,len(E),hashlib.sha256(E).hexdigest(),time=21)
    if phase in ('approval','link-staged','after','release'):
        v[A][A]['metadata'][7:]=[22,22]
        v[A][A+'/current']=row(7,8,stat.S_IFREG|0o400,len(NEW),hashlib.sha256(NEW).hexdigest(),time=22)
    if phase in ('after','release'):
        v[C][C]['metadata'][7:]=[23,23]
        v[C][C+'/current']=row(7,9,stat.S_IFLNK|0o777,38,target='/opt/schubert-nk/releases/0.1.0-PG1068',time=23)
    if phase=='link-staged':
        v[C][C]['metadata'][7:]=[23,23]
        v[C][C+'/pg1088-current.part']=row(7,9,stat.S_IFLNK|0o777,38,target='/opt/schubert-nk/releases/0.1.0-PG1068',time=23)
    return v


class Finite(unittest.TestCase):
    def test_independent_epoch_golden_and_null_unknown_bound_values(self):
        self.assertEqual(E,epoch_bytes('11111111-2222-4333-8444-555555555555'))
        for value in (None,'','unknown','aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'.upper(),
                      '00000000-0000-0000-0000-000000000000','cbca8738-3b24-4090-b77c-bf029677cdd6',
                      'eeae04ea-713c-4f2d-888d-358fb4bed274','091663ce-1cf4-47e7-8311-218ebb0c8653'):
            with self.assertRaises(ValueError):epoch_bytes(value)

    def test_all_fixed_publication_phases(self):
        for phase in ('before','epoch','approval','link-staged','after','release'):
            self.assertTrue(verify(fixture(),actual(phase),phase,E,20,30))

    def test_null_unknown_epoch_phase_and_incomplete_tree(self):
        for old,now,phase,e,b,end in [(None,actual('after'),'after',E,20,30),
          (fixture(),None,'after',E,20,30),(fixture(),actual('after'),'unknown',E,20,30),
          (fixture(),actual('after'),'after',None,20,30),(fixture(),actual('after'),'after',E+b'x',20,30),
          (fixture(),actual('after'),'after',E,31,30),(fixture(),actual('after'),'after',E,False,30)]:
            with self.assertRaises(ValueError):verify(old,now,phase,e,b,end)

    def test_each_pointer_metadata_acl_content_and_unrelated_entry_change_refused(self):
        for path,root in [(S+'/epoch.current',S),(A+'/current',A),(C+'/current',C)]:
            for index in (0,2,3,4,5,6,7,8):
                value=actual('after');value[root][path]['metadata'][index]+=100
                with self.assertRaises(ValueError):verify(fixture(),value,'after',E,20,30)
            value=actual('after');value[root][path]['acl']=['unexpected']
            with self.assertRaises(ValueError):verify(fixture(),value,'after',E,20,30)
        for root,path in [(A,A+'/current'),(S,S+'/epoch.current')]:
            value=actual('after');value[root][path]['sha256']='0'*64
            with self.assertRaises(ValueError):verify(fixture(),value,'after',E,20,30)
        value=actual('after');value[C][C+'/current']['target']='/tmp/wrong'
        with self.assertRaises(ValueError):verify(fixture(),value,'after',E,20,30)
        value=actual('after');value[C][C+'/releases']['metadata'][8]+=1
        with self.assertRaises(ValueError):verify(fixture(),value,'after',E,20,30)

    def test_parent_finite_effect_and_unknown_entry_no_rebase(self):
        for root in (S,A,C):
            for index in (0,1,2,3,4,5,6,7,8):
                value=actual('after');value[root][root]['metadata'][index]+=100
                with self.assertRaises(ValueError):verify(fixture(),value,'after',E,20,30)
            value=actual('after');value[root][root+'/unexpected']=copy.deepcopy(value[root][root])
            with self.assertRaises(ValueError):verify(fixture(),value,'after',E,20,30)
        value=actual('before');value[S][S+'/epoch.current']=row(28,7,stat.S_IFREG|0o600,len(E),hashlib.sha256(E).hexdigest())
        with self.assertRaises(ValueError):verify(fixture(),value,'before',None,20,30)

    def test_old_binding_collection_null_and_row_shape_never_accept(self):
        for root in (S,A,C):
            for malformed in (None,[],{},{'unexpected':None}):
                before=fixture();before[root]=malformed
                with self.assertRaises(ValueError):verify(before,actual('after'),'after',E,20,30)
        before=fixture();before[A][A+'/current']['sha256']='0'*64
        with self.assertRaises(ValueError):verify(before,actual('after'),'after',E,20,30)
        before=fixture();before[C][C+'/current']['target']='/tmp/unapproved'
        with self.assertRaises(ValueError):verify(before,actual('after'),'after',E,20,30)
        for malformed in (None,[],{},dict(fixture()[A][A+'/current'],metadata=None),
                          dict(fixture()[A][A+'/current'],metadata=[True]*9),
                          dict(fixture()[A][A+'/current'],sha256='unknown')):
            value=actual('after');value[A][A+'/current']=malformed
            with self.assertRaises(ValueError):verify(fixture(),value,'after',E,20,30)

    def test_old_fd_original_remains_same_despite_known_atomic_unlink(self):
        before=fixture();after=actual('after')
        for path,root in ((A+'/current',A),(C+'/current',C)):
            old=before[root][path];fd=copy.deepcopy(old);fd['metadata'][5]=1 if root==C else 0;fd['metadata'][8]=25
            self.assertTrue(verify_retained(path,old,fd,'after',after,20,30))
            for index in (0,1,2,3,4,5,6,7,8):
                bad=copy.deepcopy(fd);bad['metadata'][index]+=100
                with self.assertRaises(ValueError):verify_retained(path,old,bad,'after',after,20,30)
            with self.assertRaises(ValueError):verify_retained(path,old,fd,'before',before,20,30)
        for root in (S,A,C):
            self.assertTrue(verify_retained(root,before[root][root],after[root][root],'after',after,20,30))
            with self.assertRaises(ValueError):verify_retained(root,before[root][root],after[root][root],'after',None,20,30)
        old=before[C][C+'/releases'];bad=copy.deepcopy(old);bad['metadata'][8]+=1
        with self.assertRaises(ValueError):verify_retained(C+'/releases',old,bad,'after',after,20,30)

    def test_staged_fixed_link_allowed_only_exact_exchange_phase(self):
        value=actual('link-staged')
        for phase in ('approval','after','release'):
            with self.assertRaises(ValueError):verify(fixture(),value,phase,E,20,30)
        for field,bad in [('target','/tmp/foreign'),('sha256','0'*64),('acl',['foreign'])]:
            wrong=copy.deepcopy(value);wrong[C][C+'/pg1088-current.part'][field]=bad
            with self.assertRaises(ValueError):verify(fixture(),wrong,'link-staged',E,20,30)
        for index in (0,2,3,4,5,6,7,8):
            wrong=copy.deepcopy(value);wrong[C][C+'/pg1088-current.part']['metadata'][index]+=100
            with self.assertRaises(ValueError):verify(fixture(),wrong,'link-staged',E,20,30)


if __name__=='__main__':unittest.main()
