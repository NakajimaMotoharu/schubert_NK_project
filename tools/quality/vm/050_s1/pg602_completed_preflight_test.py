"""Closed payload binding, no guest or business action."""
import ast
import unittest
import pg602_completed_preflight as subject


class PayloadContract(unittest.TestCase):
    def test_single_new_save_and_result_keeps_original_scope_checks(self):
        code = subject.payload()
        ast.parse(code)
        self.assertEqual(1, code.count("save=base/'pg602-completed-preflight-v1'"))
        self.assertEqual(1, code.count("'run':'PG602-completed-preflight-v1'"))
        self.assertNotIn("save=base/'pg580-terminal-final-v1'", code)
        self.assertIn("before.private.json','3a302026", code)
        self.assertIn("after.private.json','cb5951e3", code)
        self.assertIn("normalPG579NewScopesSealed", code)
        self.assertIn("'startsStopsReloadsSqlWrites':0", code)
        self.assertIn("native=snapshot();require(native==snapshot())", code)
        self.assertIn("candidateWhole187SignatureVerified", code)
        self.assertIn("/opt/schubert-nk/releases/0.1.0-PG600", code)


if __name__ == '__main__': unittest.main()
