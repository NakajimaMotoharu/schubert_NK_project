"""Independent complete11role/18exec vector and one-role finite effect matrix."""
import copy
import stat
import unittest
import pg1369_bootstrap_role_policy as p

def fixture():
    root=p.ROOT;roles=('backup','cleanup','expiry','inspector','parent','root-api',
        'root-api193','root-web193','ordinary-api193','ordinary-web193','ordinary-inspector196')
    before={root:{'metadata':[28,3371,0,0,stat.S_IFDIR|0o755,13,260,1,1],'sha256':None}}
    for i,role in enumerate(roles):
        before[root+'/'+role]={'metadata':[28,4000+i,0,0,stat.S_IFDIR|0o700,2,40,1,1],'sha256':None}
    for i in range(18):
        before[root+'/parent/vector'+str(i)+'.exec']={'metadata':[28,5000+i,0,0,stat.S_IFREG|0o600,1,50,1,1],'sha256':'a'*64}
    after=copy.deepcopy(before);after[root]['metadata'][5:]=[14,280,100,101]
    after[root+'/ordinary-bootstrap196']={'metadata':[28,6000,999,981,stat.S_IFDIR|0o700,2,40,100,101],'sha256':None}
    return before,after

class Test(unittest.TestCase):
    def test_literal_one_role_and_every_protected_field(self):
        before,after=fixture();self.assertTrue(p.before_valid(before));self.assertTrue(p.delta(before,after,100,101))
        for path in before:
            if path==p.ROOT:continue
            for index in range(9):
                changed=copy.deepcopy(after);changed[path]['metadata'][index]+=1
                if path!=p.ROOT and index==1:
                    changed[path]['metadata'][index]=3371
                with self.assertRaises(ValueError):p.delta(before,changed,100,101)
            changed=copy.deepcopy(after);changed[path]['sha256']='b'*64
            with self.assertRaises(ValueError):p.delta(before,changed,100,101)

    def test_parent_child_unknown_and_time_boundaries(self):
        before,after=fixture()
        for path in (p.ROOT,p.ROOT+'/ordinary-bootstrap196'):
            for index in range(7):
                changed=copy.deepcopy(after);changed[path]['metadata'][index]+=1
                if path!=p.ROOT and index==1:
                    changed[path]['metadata'][index]=3371
                with self.assertRaises(ValueError):p.delta(before,changed,100,101)
            for index in (7,8):
                for value in (99,102):
                    changed=copy.deepcopy(after);changed[path]['metadata'][index]=value
                    with self.assertRaises(ValueError):p.delta(before,changed,100,101)
        for start,end in ((None,101),(True,101),(100,None),(0,101),(102,101)):
            with self.assertRaises(ValueError):p.delta(before,after,start,end)
        changed=copy.deepcopy(after);changed[p.ROOT+'/foreign']={'metadata':[28,7000,0,0,stat.S_IFDIR|0o700,2,40,100,101],'sha256':None}
        with self.assertRaises(ValueError):p.delta(before,changed,100,101)
        for bad in (None,{},after):
            with self.assertRaises(ValueError):p.before_valid(bad)

if __name__=='__main__':
    unittest.main()
