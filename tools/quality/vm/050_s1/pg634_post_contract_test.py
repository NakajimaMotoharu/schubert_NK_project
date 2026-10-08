"""Independent scalar literals, protected nineteen observations, no tool encoder."""
import copy
import unittest
from pg634_post_contract import finite, fresh_join


def fixed():
    before={k:{'literal':'retain'}for k in 'backup bootstrapOldProofs bootstrapTools configuration credentials dependencies native oldProofs originals parentPid1 pid1Stop rows runtime startup units current approval unitFiles caddyPre'.split()}
    before['runtime']=None;before['current']='/opt/schubert-nk/releases/0.1.0-PG621'
    before['approval']={'metadata':[20,40,0,0,33024,1,120,1,1],'sha256':'before'}
    after=copy.deepcopy(before);after['current']='/opt/schubert-nk/releases/0.1.0-PG631'
    # Digest independently fixed from literal approval, not Production encode/finite.
    after['approval']={'metadata':[20,41,0,0,33024,1,120,2,2],'sha256':'placeholder'}
    import hashlib
    after['approval']['sha256']=hashlib.sha256(b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG631\nmanifest_sha256=57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe\n').hexdigest()
    return before,after


class Post(unittest.TestCase):
    def test_fresh_same_byte_inode_unknown_runtime_and_unit_paths(self):
        _,after=fixed();paths=['/etc/systemd/system/fixture-'+str(i)for i in range(18)]
        after['unitFiles']={p:{'sealed':True}for p in paths}
        approval=copy.deepcopy(after['approval']);current=after['current']
        self.assertTrue(fresh_join(after,current,approval,[],paths))
        changed=copy.deepcopy(approval);changed['metadata'][1]+=1
        with self.assertRaises(ValueError):fresh_join(after,current,changed,[],paths)
        changed=copy.deepcopy(approval);changed['metadata'][2]=False
        with self.assertRaises(ValueError):fresh_join(after,current,changed,[],paths)
        for runtime in (['foreign.conf'],['pg492-once-resume.conf'],None,{}):
            with self.assertRaises(ValueError):fresh_join(after,current,approval,runtime,paths)
        for actual in (paths[:-1],paths+['foreign'],paths[:-1]+['foreign'],paths[:-1]+[paths[0]],None):
            with self.assertRaises(ValueError):fresh_join(after,current,approval,[],actual)
        with self.assertRaises(ValueError):fresh_join(after,'/opt/foreign',approval,[],paths)

    def test_finite_two_and_all_protected(self):
        b,a=fixed();self.assertTrue(finite(b,b,'verify'));self.assertTrue(finite(b,a,'activate'))
        for k in b.keys()-{'approval','current'}:
            b,a=fixed();a[k]={'changed':False}
            with self.subTest(field=k),self.assertRaises(ValueError):finite(b,a,'activate')
        b,a=fixed()
        with self.assertRaises(ValueError):finite(b,a,'verify')
        for mode in ('foreign',None):
            with self.assertRaises(ValueError):finite(b,a,mode)

    def test_replacement_metadata_and_type(self):
        for i,v in [(0,21),(1,40),(2,1),(3,1),(4,33152),(5,2),(6,121)]:
            b,a=fixed();a['approval']['metadata'][i]=v
            with self.assertRaises(ValueError):finite(b,a,'activate')
        b,a=fixed();a['approval']['metadata'][0]=True
        with self.assertRaises(ValueError):finite(b,a,'activate')
        b,a=fixed();a['approval']['sha256']='0'*64
        with self.assertRaises(ValueError):finite(b,a,'activate')
        b,a=fixed();a['startup']={'literal':True};b['startup']={'literal':1}
        with self.assertRaises(ValueError):finite(b,a,'activate')


if __name__=='__main__':unittest.main()
