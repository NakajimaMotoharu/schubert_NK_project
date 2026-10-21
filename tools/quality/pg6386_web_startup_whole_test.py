import ast
import unittest
import pg6386_web_startup_whole as subject
import pg6388_original4052_artifacts as original
from pg6042_original3976_artifacts import expected_case_keys
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_actual4052_declarations_and_four_new_identities(self):
        self.assertEqual((4052, 608), subject.declared_inventory())
        rows = original.new_case_identities('HEAD')
        self.assertEqual(4, len(expected_case_keys(rows)))
        self.assertEqual(3, len({r['class'] for r in rows}))
        self.assertEqual({'web'}, {r['module'] for r in rows})

    def test_new_only_dimensions_and_no_held_operations(self):
        raw = subject.server_source('a'*40, '0'*64)
        tree = ast.parse(raw)
        for value, count in ((4052, 2), (608, 1), (1667, 1)):
            self.assertEqual(count, sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == value for x in ast.walk(tree)))
        self.assertIn('source-full-PG6386', raw)
        for token in ('systemctl', 'qemu-system', '/opt/schubert-nk/current', '--recover', '--resume'):
            self.assertNotIn(token, raw)
        self.assertIn("'tests': 4052, 'suites': 608, 'mainClasses': 1667", subject.driver_source({}))

    def test_original22_and_jvm_proof_and_original_whole_reader_bindings(self):
        values = subject.definitions()['prerequisites'].__code__.co_consts
        self.assertIn('PG6384-web-fatal-callback-retry-qualification-v1/manifest.json', values)
        self.assertIn('PG6380-web-startup-order-v1/manifest.json', values)
        values = original.definitions()['main'].__code__.co_consts
        for item in ('PG6386-six-v1', 'PG6330-current4048-cases/qualification.json',
                     'PG6384-web-fatal-callback-retry-qualification-v1/manifest.json', 'PG6386-current4052-cases'):
            self.assertIn(item, values)
        for path in (subject.__file__, original.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
