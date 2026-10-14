"""Independent current literal ownership and no business/restart surface checks."""
import ast
import unittest
import pg2964_retained_full_pair_proof as proof
import pg2966_retained_pair_owned_handoff as handoff


class CurrentRecovery(unittest.TestCase):
    def test_whole_readonly_and_exact_original_source(self):
        raw = proof.payload()
        ast.parse(raw)
        for token in ['len(rows) == 24', 'len(a[\'fds\']) == 101', '6027336854', '0.1.0-PG2802', "'118988'", '1642861', '3ddd86e5fefbe30d96876a9e8fc9e149dc28e4ab5e00f314f62bf416ebe6ee32']:
            self.assertIn(token, raw)
        for token in ['SIGTERM', 'pidfd_send_signal', '498727', '498758', '498756']:
            self.assertNotIn(token, raw)

    def test_only_current_child_then_parent_term(self):
        raw = handoff.payload()
        calls = [n for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'terminate']
        self.assertEqual([(n.args[0].value, n.args[1].value) for n in calls], [(119019, 1642861), (118988, 1642675)])
        self.assertIn("['31', '90']", raw)
        self.assertNotIn("['29', '32']", raw)
        self.assertIn('parent_after_ref(fresh[\'parent\']', raw)
        self.assertIn("'replayAllowed':False", raw)
        self.assertIn('snapshot()==snapshot()==expected[\'native\']', raw)
        self.assertFalse(any(isinstance(n, ast.Attribute) and n.attr == 'SIGKILL' for n in ast.walk(ast.parse(raw))))
        self.assertNotIn('pg_terminate_backend', raw)
        self.assertNotIn("'daemon-reload'", raw)


if __name__ == '__main__':
    unittest.main()
