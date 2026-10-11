"""Actual sent new normal receipts stay separate from the old failed prepare."""
import unittest
import pg1395_existing_role_normal_post as p

class Test(unittest.TestCase):
    def test_whole_receipt_and_protected_scope(self):
        raw=p.payload(dict.fromkeys(p.previous.previous.previous.previous.previous.transport.previous.SEALS,'b'*64))
        for s in ('pg1395-existing-role-normal-post-v1','pg1392-bootstrap-role-prepare-v1','pg1392-bootstrap-role-tools-v2',"result['preparationNormalClose']=False", "result['existingRoleVerificationNormalClose']=True",'verified_prepared==verified_closed','verified_initial[\'native\']==verified_prepared[\'native\']==native','role_policy.delta','all24UnchangedTwice','whole187SignedArtifactBytesVerified'):
            self.assertIn(s,raw)
        self.assertNotIn('pg1380-bootstrap-role-tools-v2',raw)
        self.assertNotIn('PG1391-prepared-role-independent-baseline-v1',raw)
        compile(raw,'<complete normal post>','exec')

if __name__=='__main__':unittest.main()
