"""Whole sent post joins old immutable baseline and new completion, scope not weakened."""
import unittest
import pg1388_role_independent_post as p

class Test(unittest.TestCase):
    def test_full_generated_new_post_contract(self):
        raw=p.payload(dict.fromkeys(p.previous.previous.previous.transport.previous.SEALS,'b'*64))
        for fragment in ('pg1344-current-bootstrap-before-v1/after.private.json','pg1388-role-independent-post-v1',"'parentPid1':receipt_rows",'role_policy.delta(initial',"prepared['native']==native",'ROLE_HASHES',"result['nativeNodes']",'allClientAdvisoryFlock0','whole187SignedArtifactBytesVerified',"prepared==closed"):
            self.assertIn(fragment,raw)
        self.assertNotIn('PG1344-current-bootstrap-before-v1',raw)
        self.assertIn('f64ed4689d2c52e2227f771f7870414686ff0e6f52a6dc7b3d1b22313668428d',raw)
        compile(raw,'<whole independent role post>','exec')

if __name__=='__main__':unittest.main()
