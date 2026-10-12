"""Independent finite parent metadata deltas and generated partial-original binding."""
import ast
import copy
import unittest
from pg1536_pending_candidate_sources import PARENT_CONTRACT, java, refs

class PlacementTest(unittest.TestCase):
    def validator(self):
        def require(v):
            if not v:raise ValueError('independent finite parent delta refused')
        ns={'require':require};exec(PARENT_CONTRACT,ns);return ns['parent_delta']

    def fixture(self,links):
        before={'metadata':[1,2,0,0,0o40755,3,4096,10,10],'entries':['prior'],'xattrs':{}}
        after=copy.deepcopy(before);after['metadata'][5]+=links;after['metadata'][7:]=[25,25];after['entries']=['candidate','prior']
        return before,after

    def test_directory_and_signature_finite_deltas(self):
        f=self.validator()
        for links in [0,1]:
            before,after=self.fixture(links);self.assertTrue(f(before,after,'candidate',links,20,30))

    def test_all_metadata_identity_link_size_time_and_acl_tamper(self):
        f=self.validator()
        for index in range(9):
            with self.subTest(index=index):
                before,after=self.fixture(1)
                after['metadata'][index]=after['metadata'][index]+1 if index not in [6,7,8] else 9000
                with self.assertRaises(ValueError):f(before,after,'candidate',1,20,30)
        before,after=self.fixture(1);after['xattrs']={'system.posix_acl_access':'00'}
        with self.assertRaises(ValueError):f(before,after,'candidate',1,20,30)

    def test_foreign_missing_duplicate_and_null(self):
        f=self.validator()
        for entries in [['prior'],['candidate'],['prior','candidate','foreign'],['prior','candidate','candidate']]:
            before,after=self.fixture(1);after['entries']=entries
            with self.assertRaises(ValueError):f(before,after,'candidate',1,20,30)
        before,after=self.fixture(1)
        for v in [None,{}, {'metadata':None,'entries':[],'xattrs':{}}]:
            with self.assertRaises(ValueError):f(v,after,'candidate',1,20,30)
        for links in [None,True,2,-1]:
            with self.assertRaises(ValueError):f(before,after,'candidate',links,20,30)

    def test_generated_actual_partial_context_and_no_activation(self):
        s=refs('a'*64,'b'*64);tree=ast.parse(s);j=java()
        assigns={n.targets[0].id:n.value.value for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and isinstance(n.value,ast.Constant)}
        self.assertEqual(assigns['SOURCE'],'769ddb15cd735c25fef581b5f9850ef9d0053c0f')
        self.assertIn('15700a87-9117-4f63-a0ff-768dd604d0f1',j);self.assertIn('proof.completed().isEmpty()',j)
        self.assertIn('pg1511-publication-gc-closing-v1',s);self.assertIn('StartupAdmissionFile.create().tryExclusive',j)
        self.assertIn('require(not placed and not held)',s);self.assertIn('acquire_after_placement();placed=True',s)
        self.assertIn("phase='READONLY_'",s);self.assertIn('if action in {\'run\',\'release\'}:require(placed)',s)
        for banned in ['.invalidate(','.revoke(','RENAME_EXCHANGE','daemon-reload','StartUnit','StopUnit']:
            self.assertNotIn(banned,s+j)

    def test_missing_and_invalid_hashes_before_generation(self):
        for h in [None,'','a'*63,'G'*64]:
            with self.assertRaises(ValueError):refs(h,'b'*64)
            with self.assertRaises(ValueError):refs('a'*64,h)

if __name__=='__main__':unittest.main()
