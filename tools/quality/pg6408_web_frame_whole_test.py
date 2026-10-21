import ast
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6408_web_frame_whole as subject
import pg6410_original4054_artifacts as original
from pg6042_original3976_artifacts import expected_case_keys


class Definition(unittest.TestCase):
    def test_actual4054_and_two_new_case_classes_not_arithmetic_pass(self):
        self.assertEqual((4054, 610), subject.declared_inventory())
        rows = original.new_case_identities('HEAD')
        self.assertEqual(2, len(expected_case_keys(rows))); self.assertEqual(2, len({r['class'] for r in rows}))
        self.assertEqual({'web'}, {r['module'] for r in rows})

    def test_new_only_dimensions_and_held_operations_absent(self):
        raw = subject.server_source('a'*40, '0'*64); tree = ast.parse(raw)
        for value, count in ((4054, 2), (610, 1), (1667, 1)):
            self.assertEqual(count, sum(isinstance(n, ast.Constant) and type(n.value) is int and n.value == value for n in ast.walk(tree)))
        self.assertIn('source-full-PG6408', raw)
        for token in ('systemctl', 'qemu-system', '/opt/schubert-nk/current', '--recover', '--resume'):
            self.assertNotIn(token, raw)
        self.assertIn("'tests': 4054, 'suites': 610, 'mainClasses': 1667", subject.driver_source({}))

    def test_original26_jvm_first_and_unbound_branch_proof_fails_closed(self):
        values = subject.definitions()['prerequisites'].__code__.co_consts
        self.assertIn('PG6414-web-frame-pending-qualification-v1/manifest.json', values)
        self.assertIn('PG6402-web-frame-order-v1/manifest.json', values)
        values = original.definitions()['main'].__code__.co_consts
        for item in ('PG6408-six-v1', 'PG6386-current4052-cases/qualification.json', 'PG6408-current4054-cases'):
            self.assertIn(item, values)
        with patch.object(original, 'ORDER_SHA', None), self.assertRaisesRegex(ValueError, 'pin final original26'):
            original.branchless_proof('a'*40)
        for path in (subject.__file__, original.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
