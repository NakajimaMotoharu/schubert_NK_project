import ast
import unittest
from pg1141_failed_owner_preflight import payload


class PreflightTest(unittest.TestCase):
    def test_fixed_owner_full_metadata_no_business_action_or_signal(self):
        text = payload(); tree = ast.parse(text)
        for value in ['failed-owner-preflight-v1', 'df0b989893adbddd6a539b963c07029222c47e1b557cd572f44fdb8864f1fb01',
                      'cleanup_active=True', '404585,4248646', '404614,4248757', 'resource_zero()',
                      "'30':'012400000'", "'128':'02100000'", 'len(names)==1',
                      'observed=whole();require(observed==whole())', 'require(observed==whole())',
                      'manager.UnrefUnit(u)', 'bus.close()', 'raw-journals.private.json', "'signals0':True"]:
            self.assertIn(value, text)
        for value in ['systemctl stop', 'systemctl start', 'pidfd_send_signal', '.kill(', 'os.kill(']:
            self.assertNotIn(value, text)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'md']
        self.assertGreaterEqual(len(calls), 3)
        self.assertFalse(any(isinstance(n.args[0], ast.Call) and isinstance(n.args[0].func, ast.Attribute) and n.args[0].func.attr == 'lstat' for n in calls))


if __name__ == '__main__': unittest.main()
