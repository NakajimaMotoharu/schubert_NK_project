"""Actual fresh/signal phase order and complete generated static scope."""
import ast
import unittest
from pyflakes.api import check
import pg1657_same_connection_fresh_handoff as p


class SameConnectionTest(unittest.TestCase):
    def test_fresh_independent_completion_before_reserved_signal(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<actual same-connection worker>'))
        self.assertLess(raw.index("private('fresh-complete.private'"), raw.index('terminate(289328,5627480,owner'))
        self.assertLess(raw.index("'stage':'FRESH_READONLY_PROOF_COMPLETE'"), raw.index('terminate(289328,5627480,owner'))
        self.assertIn('same_fresh(fresh_actor,json.loads(json.dumps(a)))', raw)
        self.assertIn('same_fresh(fresh_actor,json.loads(json.dumps(actor())))', raw)
        self.assertIn("'oldActor':expected['actor']", raw)
        self.assertIn('fresh_upper_ns=time.time_ns()', raw)
        self.assertNotIn('signal.SIGKILL', raw)
        calls = [ast.unparse(n.func) for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Call)]
        self.assertEqual(1, calls.count('signal.pidfd_send_signal'))

    def test_new_design_only_scope_without_history_collision(self):
        text = '# x\n\nSSC273：fresh\n\nSSC272：history\n'
        self.assertEqual('SSC273：fresh', p.design_scope(text, '343_x.md'))
        text = '# x\n\n## SSC-273（fresh）\n\nbody\n\n## SSC-272（history）\nold'
        self.assertIn('body', p.design_scope(text, 'documents/914_x.md'))
        self.assertNotIn('old', p.design_scope(text, 'documents/914_x.md'))


if __name__ == '__main__':
    unittest.main()
