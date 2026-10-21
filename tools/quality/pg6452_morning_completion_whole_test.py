import ast
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6452_morning_completion_whole as subject
import pg6454_original4056_artifacts as original
from pg6042_original3976_artifacts import expected_case_keys


class Definition(unittest.TestCase):
    def test_actual4056_two_methods_in_one_existing_class(self):
        self.assertEqual((4056, 610), subject.declared_inventory())
        rows = original.new_case_identities('HEAD')
        self.assertEqual(2, len(expected_case_keys(rows)))
        self.assertEqual(1, len({r['class'] for r in rows}))
        self.assertEqual({'batch'}, {r['module'] for r in rows})

    def test_new_only_complete_dimensions_no_held_commands(self):
        raw = subject.server_source('a'*40, '0'*64); tree = ast.parse(raw)
        for value, count in ((4056, 2), (610, 1), (1667, 1)):
            self.assertEqual(count, sum(isinstance(n, ast.Constant) and type(n.value) is int and n.value == value for n in ast.walk(tree)))
        self.assertIn('source-full-PG6452', raw)
        for token in ('systemctl', 'qemu-system', '/opt/schubert-nk/current', '--recover', '--resume'):
            self.assertNotIn(token, raw)
        self.assertIn("'tests': 4056, 'suites': 610, 'mainClasses': 1667", subject.driver_source({}))

    def test_current23_jvm_bound_and_missing_proof_rejects(self):
        with patch.object(subject, 'QSHA', None), patch.object(subject.subprocess, 'check_output', return_value=b''):
            with self.assertRaisesRegex(ValueError, 'genuine current23'):
                subject.prerequisites('a'*40)
        constants = original.definitions()['main'].__code__.co_consts
        for value in ('PG6452-six-v1', 'PG6408-current4054-cases/qualification.json', 'PG6452-current4056-cases'):
            self.assertIn(value, constants)
        for path in (subject.__file__, original.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
