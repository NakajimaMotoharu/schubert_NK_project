"""Independent literal step geometry and strict full24/state gates, no VM effects."""
import ast,unittest
import pg981_current_bootstrap_before_v2 as p
from pg964_current_stop_test import fixture
class Test(unittest.TestCase):
    def test_one_run_geometry_and_old_wrong_count_not_accepted(self):
        expected=584+2+8;self.assertEqual(594,expected);self.assertNotEqual(604,expected)
        raw=p.source();self.assertIn('==594',raw);self.assertNotIn('==604',raw);self.assertIn('pg978-bootstrap-before-v2',raw);self.assertNotIn('pg978-bootstrap-before-v1',raw)
    def test_existing_user_and_complete_afterconditions_are_not_relaxed(self):
        raw=p.source()
        for x in ('pg968-terminal-final-v1','pg960-completed-readonly-v1','proofHashes',"len(value['rows']['schubert.app_users'])==1", "value['rows']['schubert.app_users'][0]['role']=='ADMIN'",'not any(os.path.lexists','parentPid1','namespace'):
            self.assertTrue(x in raw,'missing '+x)
        # Metadata guard lives in composed guest payload, not the host wrapper.
        env={'__file__':str(p.R/'pg981_current_bootstrap_before_v2.py'),'__name__':'inert_fixture'}
        exec(compile(raw,'<inert before definitions>','exec'),env)
        payload=env['payload'](fixture(),{k:'1'*64 for k in ('before.private.json','after.private.json','complete.private','parent.private.jsonl')})
        self.assertTrue('metadata9(p.lstat())==metadata9(s)' in payload)
if __name__=='__main__':unittest.main()
