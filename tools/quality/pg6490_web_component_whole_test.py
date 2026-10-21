import ast
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6490_web_component_whole as subject
import pg6492_original4064_artifacts as original
from pg6042_original3976_artifacts import expected_case_keys


class Definition(unittest.TestCase):
    def test_actual4064_eight_methods_two_new_classes(self):
        self.assertEqual((4064, 612), subject.declared_inventory())
        rows = original.new_case_identities('HEAD')
        self.assertEqual(8, len(expected_case_keys(rows)))
        self.assertEqual(2, len({r['class'] for r in rows}))
        self.assertEqual({'batch', 'web'}, {r['module'] for r in rows})

    def test_new_only_complete_dimensions_no_held_commands(self):
        raw = subject.server_source('a'*40, '0'*64); tree = ast.parse(raw)
        for value, count in ((4064, 2), (612, 1), (1667, 1)):
            self.assertEqual(count, sum(isinstance(n, ast.Constant) and type(n.value) is int and n.value == value for n in ast.walk(tree)))
        self.assertIn('source-full-PG6490', raw)
        for token in ('systemctl', 'qemu-system', '/opt/schubert-nk/current', '--recover', '--resume'):
            self.assertNotIn(token, raw)
        driver = subject.driver_source({})
        self.assertIn("'tests': 4064, 'suites': 612, 'mainClasses': 1667", driver)
        self.assertIn('Original27 all-six three-phase qualification', driver)
        self.assertNotIn('Original59', driver)

    def test_genuine27_jvm_required_missing_proof_rejected(self):
        with patch.object(subject, 'QSHA', None), patch.object(subject.subprocess, 'check_output', return_value=b''):
            with self.assertRaisesRegex(ValueError, 'genuine current27'):
                subject.prerequisites('a'*40)
        constants = original.definitions()['main'].__code__.co_consts
        for value in ('PG6490-six-v1', 'PG6452-current4056-cases/qualification.json', 'PG6490-current4064-cases'):
            self.assertIn(value, constants)
        for path in (subject.__file__, original.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__': unittest.main()
