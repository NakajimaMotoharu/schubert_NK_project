"""Actual full read-only scope and fixed identity, never a signal test stub."""
import ast
import unittest
from pyflakes.api import check
import pg1650_retained_no_db_readonly_proof as p


class RetainedReadonlyProofTest(unittest.TestCase):
    def test_actual_no_db_owner_checks_and_no_mutating_call(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<actual noDB retained proof>'))
        for literal in ['5627480', '/proc/289328', 'EXPECTED_ARGV', "children", 'require(not children)', 'TOOL_HASHES', "==after['runtime']", 'len(rows)==24', 'owned_lock(name)', "'candidateNotPlaced':True"]:
            self.assertIn(literal, raw)
        tree = ast.parse(raw)
        calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]
        for name in ['os.kill', 'signal.pidfd_send_signal', 'os.pidfd_open', 'manager.StartUnit', 'manager.StopUnit']:
            self.assertNotIn(name, calls)
        for text in ['systemctl start', 'systemctl stop', 'daemon-reload', 'UPDATE schubert', 'INSERT INTO']:
            self.assertNotIn(text, raw)


if __name__ == '__main__':
    unittest.main()
