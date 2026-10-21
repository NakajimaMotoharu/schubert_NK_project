"""Definition and hostile-fixture checks, not a whole-run or PT acceptance."""
import ast
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg6524_finite_defaults_whole as whole
import pg6526_original4073_artifacts as original


class IntegratedFiniteDefinitionTest(unittest.TestCase):
    def test_actual_declarations_and_nine_new_identities(self):
        self.assertEqual((4073, 614), whole.declared_inventory())
        rows = original.new_case_identities('HEAD')
        self.assertEqual(9, len(original.reader.expected_case_keys(rows)))
        self.assertEqual(3, len({r['class'] for r in rows}))
        self.assertEqual({'bootstrap'}, {r['module'] for r in rows})

    def test_complete_dimensions_and_finite_commands(self):
        raw = whole.server_source('a'*40, '0'*64)
        tree = ast.parse(raw)
        for value, count in ((4073, 2), (614, 1), (1667, 1)):
            self.assertEqual(count, sum(isinstance(n, ast.Constant) and type(n.value) is int
                                       and n.value == value for n in ast.walk(tree)))
        for token in ('systemctl', 'qemu-system', '/opt/schubert-nk/current', '--recover', '--resume'):
            self.assertNotIn(token, raw)
        driver = whole.driver_source({})
        self.assertIn("'tests': 4073, 'suites': 614, 'mainClasses': 1667", driver)
        self.assertIn('All three selected originals qualified', driver)
        self.assertNotIn('Original59', driver)

    def test_empty_owner_requires_every_original_byte_identical(self):
        raw = original.emitted('0'*64, '/own/new-only-reader')
        self.assertEqual(0, check(raw, '<original4073 namespace>'))
        node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef)
                    and n.name == 'physical_difference')
        scope = {}
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<exact physical fixture>', 'exec'), scope)
        compare = scope['physical_difference']
        before = {str(i): 'same' for i in range(1667)}
        self.assertEqual(([], [], 1667), compare(before, dict(before), set(), (1667, 1667), []))
        for after in (dict(before, **{'0': 'changed'}), {k:v for k,v in before.items() if k != '0'},
                      dict(before, extra='new')):
            with self.assertRaises(ValueError):
                compare(before, after, set(), (1667, 1667), [])
        with self.assertRaises(ValueError):
            compare(before, dict(before), set(), (1667, 1667), None)
        self.assertNotIn('PG6524', original.reader.emitted('0'*64))

    def test_missing_current_qualification_cannot_launch(self):
        with patch.object(whole, 'QSHA', None), patch.object(whole.subprocess, 'check_output', return_value=b''):
            with self.assertRaisesRegex(ValueError, 'genuine current reader15'):
                whole.prerequisites('a'*40)
        constants = original.definitions()['main'].__code__.co_consts
        self.assertIn('PG6524-six-v1', constants)
        self.assertIn('PG6490-current4064-cases/qualification.json', constants)
        self.assertIn('PG6524-current4073-cases', constants)


if __name__ == '__main__':
    unittest.main()
