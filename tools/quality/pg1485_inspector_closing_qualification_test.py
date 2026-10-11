"""Handwritten PID1 vectors, foreign ownership and deadline rejection."""
import copy
import unittest
from pg1485_inspector_closing_qualification import bounds,payload

class InspectorClosingTest(unittest.TestCase):
    def fixture(self):
        common={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','UNIT':'schubert-nk-inbox-inspector.service','INVOCATION_ID':'d69f0f99b48a47a5b51ad571ac996c31'}
        return [dict(common,MESSAGE_ID=mid,JOB_TYPE=kind,JOB_ID=job,JOB_RESULT=result,__MONOTONIC_TIMESTAMP=str(t),__REALTIME_TIMESTAMP=str(w))for mid,kind,job,result,t,w in [
          ('7d4958e842da4a758f6c1cdc7b36dcc5','start','13787','',5711141320,2000001),
          ('39f53479d3a045ac8e11786248231fbf','start','13787','done',5711141321,3000000),
          ('9d1aaa27d60140bd96365438aad20286','stop','13934','done',5711141322,4000001),
          ('other','start','13787','',5711141321,3000000),('other2','stop','13934','',5711141322,4000001)]]
    def test_handwritten_bounds_rounding(self):
        self.assertEqual((2000,4001),bounds(self.fixture()))
    def test_foreign_missing_duplicate_and_deadline(self):
        for key,value in [('_BOOT_ID','foreign'),('_PID','2'),('_UID','1'),('UNIT','other'),('INVOCATION_ID','foreign'),('JOB_ID','9'),('__MONOTONIC_TIMESTAMP','5711141318'),('__MONOTONIC_TIMESTAMP','7511141318')]:
            with self.subTest(key=key,value=value):
                v=self.fixture();v[0][key]=value
                with self.assertRaises(ValueError):bounds(v)
        for v in [None,[],self.fixture()[:-1],self.fixture()+[self.fixture()[0]],self.fixture()[:3]+[copy.deepcopy(self.fixture()[0]),self.fixture()[4]]]:
            with self.assertRaises(ValueError):bounds(v)
    def test_readonly_export_code(self):
        raw=payload();compile(raw,'<saved export>','exec')
        self.assertNotIn('subprocess',raw);self.assertNotIn('unlink',raw)
        self.assertIn('os.O_RDONLY|os.O_NOFOLLOW',raw)
        self.assertIn('hashlib.sha256(body).hexdigest()==digest',raw)

if __name__=='__main__':unittest.main()
