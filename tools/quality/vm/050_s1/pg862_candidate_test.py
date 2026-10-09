"""Independent missing/extra/foreign byte delta refusal; no signing/deployment."""
import unittest
import pg862_candidate_contract as p
class Test(unittest.TestCase):
    def test_finite_three_source_family_delta(self):
        self.assertEqual(15,len(p.CHANGED['batch']));self.assertEqual({},p.ADDED)
        old={m:{'stable.class':'0'*64}for m in p.MODULES};new={m:dict(v)for m,v in old.items()}
        for name in p.CHANGED['batch']:old['batch'][name]='1'*64;new['batch'][name]='2'*64
        p.verify_delta(old,new)
        for module,name,mode in [('batch',next(iter(p.CHANGED['batch'])),'missing'),('api','stable.class','foreign'),('batch','extra.class','extra')]:
            changed={m:dict(v)for m,v in new.items()}
            if mode=='missing':changed[module][name]=old[module][name]
            else:changed[module][name]='3'*64
            with self.assertRaises((ValueError,AssertionError)):p.verify_delta(old,changed)
if __name__=='__main__':unittest.main()
