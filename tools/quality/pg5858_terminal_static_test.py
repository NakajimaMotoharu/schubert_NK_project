import subprocess
import unittest
import pg5858_terminal_static as target


class ExactTerminalHaltTest(unittest.TestCase):
    def test_exact_four_committed_catch_additions_and_rules_unchanged(self):
        self.assertEqual(4,len(target.MODIFIED))
        for path in target.MODIFIED:
            before=subprocess.check_output(['git','show','86287c3fb83b483050b88dce04bc644961682bc4:'+path],cwd=target.engine.ROOT,text=True)
            expected=target.expected_source(path,before)
            self.assertEqual((target.engine.ROOT/path).read_text(),expected)
            self.assertEqual(before.count(OWNERS:=target.OWNERS[path]+'.set(true);')+1,expected.count(OWNERS))
        raw=target.runner_source();self.assertIn("expected_counts=Counter(old['ruleCounts'])",raw)
        self.assertNotIn('failIfNoTests=false',raw)


if __name__=='__main__':unittest.main()
