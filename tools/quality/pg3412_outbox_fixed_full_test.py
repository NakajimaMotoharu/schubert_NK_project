import ast
import inspect
import unittest

from pyflakes.api import check
import pg3412_outbox_fixed_full as current


class ChangedMainWholeTest(unittest.TestCase):
    def test_actual_bindings_cardinality_and_digest_preserved(self):
        head = '3707' + 'a' * 36; digest = '543' + 'b' * 61
        raw = current.server_source(head, digest); tree = ast.parse(raw)
        values = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)]
        self.assertIn(head, values); self.assertIn(digest, values)
        self.assertIn(current.SOURCE, values); self.assertNotIn(current.previous.SOURCE, values)
        self.assertIn(545, values); self.assertIn(3712, values)
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'complete_result')
        ns = {}; exec(compile(ast.Module(body=[fn], type_ignores=[]), '<whole finite gate>', 'exec'), ns)
        self.assertTrue(ns['complete_result'](0, True, [], 3712, 545, 1643))
        for bad in [(1, True, [], 3712, 545, 1643), (0, True, [], 3707, 543, 1643),
                    (0, True, [], 3712, 543, 1643), (0, False, [], 3712, 545, 1643)]:
            self.assertFalse(ns['complete_result'](*bad))

    def test_independent_namespace_and_not_relabeling_old_native(self):
        raw = '\n'.join(inspect.getsource(f) for f in [current.positions, current.verify_switch_debug,
                          current.require, current.classify, current.independent])
        self.assertEqual(0, check(raw, '<complete independent3712>'))
        self.assertEqual(3712, sum(v[0] for v in current.EXPECTED.values()))
        self.assertEqual(545, sum(v[1] for v in current.EXPECTED.values()))
        self.assertIn("'candidateNativePending': True", raw)
        self.assertIn("'oldNativeImported': False", raw)


if __name__ == '__main__':
    unittest.main()
