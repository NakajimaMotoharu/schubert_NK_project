"""Independent literal step geometry and strict full24/state gates, no VM effects."""
import ast,unittest
import pg981_current_bootstrap_before_v2 as p
class Test(unittest.TestCase):
    def test_one_run_geometry_and_old_wrong_count_not_accepted(self):
        expected=584+2+8;self.assertEqual(594,expected);self.assertNotEqual(604,expected)
        raw=p.source();self.assertIn('==594',raw);self.assertNotIn('==604',raw);self.assertIn('pg978-bootstrap-before-v2',raw);self.assertNotIn('pg978-bootstrap-before-v1',raw)
    def test_existing_user_and_complete_afterconditions_are_not_relaxed(self):
        raw=p.source()
        for x in ('pg968-terminal-final-v1','pg960-completed-readonly-v1','proofHashes',"len(value['rows']['schubert.app_users'])==1", "value['rows']['schubert.app_users'][0]['role']=='ADMIN'",'not any(os.path.lexists','metadata9','parentPid1','namespace'):
            self.assertIn(x,raw,'missing '+x)
if __name__=='__main__':unittest.main()
