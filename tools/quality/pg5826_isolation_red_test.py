import unittest
from pg5826_isolation_red import RED_API,RED_WEB,runner_source,expected_assertions


class ExactIsolationRedPlanTest(unittest.TestCase):
    def test_counts_and_preserved_guards(self):
        self.assertEqual((6,2),(len(RED_API),len(RED_WEB)))
        self.assertIn('!=15',runner_source('red-api'));self.assertIn('!=10',runner_source('red-web'))
        for phase in('red-api','red-web'):
            raw=runner_source(phase)
            self.assertIn('target100=False',raw);self.assertNotIn('failIfNoTests=false',raw)
            self.assertNotIn('lan_server',raw);self.assertNotIn('systemctl',raw)

    def test_only_expected_policy_assertions_not_unexpected_fixture_failure(self):
        msg='expected: <false> but was: <true>\nexpected: <1> but was: <0>'
        self.assertTrue(expected_assertions(msg,False))
        self.assertTrue(expected_assertions(msg+'\nexpected: <true> but was: <false>',True))
        self.assertFalse(expected_assertions(msg+'\nexpected: <0> but was: <1>',False))
        self.assertFalse(expected_assertions('expected: <1> but was: <0>',False))


if __name__=='__main__':unittest.main()
