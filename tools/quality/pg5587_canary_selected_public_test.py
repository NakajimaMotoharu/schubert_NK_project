import unittest
from pyflakes.api import checkPath
import pg5587_canary_selected_public as entry


class CurrentPublication(unittest.TestCase):
    def test_correct_case_scope_and_receipts_do_not_overwrite_history(self):
        raw=entry.publication_source()
        self.assertIn("load('pg5566-private-monitor-green-v3'",raw)
        self.assertIn("load('pg5568-monitor-bytecode-v3'",raw)
        self.assertIn("'pg5566-private-monitor-green-v2', 'pg5566-private-monitor-green-v3'",raw)
        self.assertIn("'actualCases': 73",raw);self.assertIn("'suites': 9",raw)
        self.assertIn("'criterionTraces': 6",raw);self.assertNotIn("'newCriterionTraces'",raw)
        self.assertEqual(len(entry.IDS),6)
        scope={**vars(entry.previous),'SOURCE':entry.SOURCE,'BASE':entry.BASE,'IDS':entry.IDS}
        exec(compile(raw,'<pure allowlist namespace>','exec'),scope)
        self.assertTrue(callable(scope['main']))
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
