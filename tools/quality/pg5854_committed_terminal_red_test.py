import unittest
from pg5854_committed_terminal_red import RED_API,RED_WEB,runner_source,expected_assertions


class TerminalRedProfileTest(unittest.TestCase):
    def test_exact_four_policy_reds_and_unchanged_guards(self):
        self.assertEqual((3,1),(len(RED_API),len(RED_WEB)))
        for phase,count in(('red-api',11),('red-web',9)):
            raw=runner_source(phase);self.assertIn('!='+str(count),raw)
            self.assertIn('target100=False',raw);self.assertNotIn('failIfNoTests=false',raw)
            self.assertNotIn('lan_server',raw);self.assertNotIn('systemctl',raw)

    def test_only_three_postterminal_processing_counts_are_the_red(self):
        for method,actual in(('term001SyncCommitStopsAllFourContextAdmissions','5'),('term002QuestionCommitStopsFurtherAdmissions','2'),('term004ReplyCommitStopsFurtherAdmissions','2')):
            msg=('expected: <1> but was: <'+actual+'>\n')*3
            self.assertTrue(expected_assertions(msg,method))
            self.assertFalse(expected_assertions(msg+'expected: <0> but was: <1>',method))
            self.assertFalse(expected_assertions(msg[:msg.find('\n')],method))


if __name__=='__main__':unittest.main()
