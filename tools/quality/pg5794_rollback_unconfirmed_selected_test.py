import unittest
import pg5794_rollback_unconfirmed_selected as target


class FiniteRollbackSelectionTest(unittest.TestCase):
    def test_phase_counts_and_no_hidden_runtime(self):
        api=target.runner_source('red-api');web=target.runner_source('red-web')
        self.assertIn('!=11',api);self.assertIn('!=9',web)
        for value in(api,web):
            self.assertIn("'-fae'",value)
            self.assertNotIn('failIfNoTests=false',value)
            self.assertNotIn('lan_server',value)
            self.assertNotIn('systemctl',value)
            self.assertIn('out.mkdir(mode=0o700)',value)
            self.assertIn('target100=False',value)
        self.assertEqual(3,len(target.RED_API));self.assertEqual(1,len(target.RED_WEB))


if __name__=='__main__':unittest.main()
