"""Current Root/post/hash pins and original existingADMIN/no credential input."""
import unittest
import pg978_current_bootstrap_before as p
class Test(unittest.TestCase):
    def test_current_independent_snapshot_and_after_hash_pins(self):
        raw=p.source()
        for x in ('pg968_current_terminal_final','pg960-completed-readonly-v1','pg963-native-tools-v1/pg963_parent_receipt.py','40ef6e894573d2ffab1d1732124960f9c98d5f97','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524',"==604","len(value['rows']['schubert.app_users'])==1","value['rows']['schubert.app_users'][0]['role']=='ADMIN'",'bootstrap-admin-username','bootstrap-admin-password','not any(os.path.lexists'):
            self.assertIn(x,raw,'missing '+x)
        for old in ('pg895','pg890','pg885','pg887','e01612fcd7f2752df5ae0836b78538fd5e87f120'):self.assertNotIn(old,raw)
if __name__=='__main__':unittest.main()
