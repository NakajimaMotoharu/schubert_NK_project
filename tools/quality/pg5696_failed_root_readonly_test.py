"""FailedRoot reader cannot become a lifecycle action or expose journal messages."""
import ast
import unittest
from pyflakes.api import check,checkPath
from pg5652_current_acceptance_test import independent_observed
import pg5696_failed_root_readonly as entry


class FailureRead(unittest.TestCase):
    def test_readonly_current_generation_private_first_and_allowlisted_summary(self):
        raw=entry.payload(independent_observed());self.assertEqual(0,check(raw,'<failedRoot capture>'));ast.parse(raw)
        for marker in(entry.admission.SOURCE,entry.admission.BOM,"root['ExecMainStatus']=='30'","api['InvocationID']=='4bf2830c7f7f4a56b6168c8b6f815a39'",'repeatable read read only',"'newLifecycleActions':0","'dbWrites':0"):
            self.assertIn(marker,raw)
        self.assertLess(raw.index("raw=command(role+'-journal'"),raw.index('rows=[json.loads(line)for line in raw.splitlines()]'))
        self.assertIn("preserve('current-summary.private.json'",raw)
        for value in('systemctl start','systemctl stop','block_resize','reboot','kill(','unlink(','rmtree(','truncate('):self.assertNotIn(value,raw)
        final=ast.parse(raw).body[-1];self.assertIsInstance(final,ast.Expr)
        self.assertNotIn('messages',ast.unparse(final));self.assertNotIn('locks',ast.unparse(final))
        self.assertEqual(0,checkPath(entry.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
