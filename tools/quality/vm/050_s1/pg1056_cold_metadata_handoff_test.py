"""PT-DEP-1056001..002 fixed metadata-only once target and whole proof binding."""
import ast
import unittest
from pg1056_cold_metadata_handoff import payload


class Metadata(unittest.TestCase):
    def test_fixed_target_once_and_same_original_tree_after(self):
        raw=payload();tree=ast.parse(raw)
        self.assertIn('contract.terminate_once(7427, 1860448',raw)
        self.assertIn("contract.durable_reservation(reservation_fd, '7427.term-reserved.private.json'",raw)
        self.assertIn("assert v == before['base']",raw)
        self.assertIn('not daemon.NameHasOwner(METADATA_BUS)',raw)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='pidfd_send_signal']
        self.assertEqual(1,len(calls))
        self.assertNotIn('SIGKILL',raw)
        self.assertNotIn('pg_terminate_backend',raw)
        self.assertIn("except BaseException as failure:\n    retained_error(failure)",raw)

    def test_all_scope_and_source_proofs_survive_durable_reservation(self):
        raw=payload()
        self.assertIn('assert current == before',raw)
        self.assertIn("'proofSha256': hashlib.sha256(private).hexdigest()",raw)
        self.assertIn("'oldScriptSha256': OLD_SCRIPT_SHA",raw)
        self.assertIn('after = post()',raw)
        self.assertIn('assert after == post()',raw)
        self.assertIn("/tree-preflight-v3/metadata-handoff-v1",raw)
        self.assertIn("assert len(v['fds']) == 349",raw)


if __name__=='__main__':
    unittest.main()
