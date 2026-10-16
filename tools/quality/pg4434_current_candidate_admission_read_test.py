"""Scope change only: old143/epoch/native/full invariants stay fail-closed."""
import ast
import unittest
import pg4360_pool_bound_partial_sources as original
import pg4434_current_candidate_admission_read as subject


class CurrentAdmission(unittest.TestCase):
    def test_only_new_namespace_and_final_safe_fields_differ_from_frozen_profile(self):
        before = original.files()['post.py']; after = subject.payload()
        a = ast.parse(before); b = ast.parse(after)
        # One new final dictionary update. All original imports/functions/guards
        # remain textually identical apart from the evidence directory literal.
        additions = [n for n in b.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                     and isinstance(n.value.func, ast.Attribute) and isinstance(n.value.func.value, ast.Name)
                     and n.value.func.value.id == 'value' and n.value.func.attr == 'update']
        self.assertEqual(1, len(additions)); b.body.remove(additions[0])
        class Namespace(ast.NodeTransformer):
            def visit_Constant(self, node):
                if node.value == subject.SLOT: node.value = 'pg4362-pool-bound-post-v3'
                return node
        self.assertEqual(ast.dump(a, include_attributes=False), ast.dump(Namespace().visit(b), include_attributes=False))
        for invariant in ['parent143StillFailed', 'newMARDDBTenRefNormalClose', 'former_issued', 'ABORT', 'normal_terminal']:
            self.assertIn(invariant, after)
        self.assertNotIn("['systemctl','start'", after)
        self.assertNotIn("['systemctl','stop'", after)


if __name__ == '__main__':
    unittest.main()
