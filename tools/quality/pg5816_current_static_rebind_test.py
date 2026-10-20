import unittest
from pg5816_current_static_rebind import rebind_source


class Current467ReauthenticationTest(unittest.TestCase):
    def test_exact_prior_and_current_artifact_no_old_pt_import(self):
        raw=rebind_source()
        self.assertIn('len(used)!=467',raw);self.assertIn('len(held)!=13',raw)
        self.assertIn("'currentRawFindings':1595",raw)
        self.assertIn('PG5798-lifetime-empty4-v1',raw)
        self.assertIn('PG5810-rollback-static-reauth-v1',raw)
        self.assertIn('currentWholeCaseRefs=[]',raw)
        self.assertNotIn('lan_server',raw);self.assertNotIn('subprocess',raw)


if __name__=='__main__':unittest.main()
