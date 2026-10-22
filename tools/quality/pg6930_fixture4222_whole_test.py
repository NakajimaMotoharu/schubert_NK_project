import ast
import unittest
import pg6930_fixture4222_whole as p
import pg6932_original4222_artifacts as original


class Fixture4222DefinitionTest(unittest.TestCase):
    def test_actual_full_inventory_and_test_only_diff(self):
        self.assertEqual((4222, 660), p.declared_inventory())
        p.guard('e7d64fda2')
        self.assertEqual(9, len(original.added_cases('e7d64fda2')))

    def test_real_runner_namespace_and_dimensions(self):
        raw = p.server_source('0' * 40, '0' * 64)
        ast.parse(raw)
        for value in ('4222', '660', '1669', 'PG6930'):
            self.assertIn(value, raw)
        self.assertNotIn('4213', raw)
        namespace = p.definitions()['main'].__globals__
        for name in ('server_source', 'driver_source', 'prerequisites', 'original_source'):
            self.assertIs(getattr(p, name), namespace[name])
        raw = original.emitted('0' * 64, '/home/mini/schubert-nk-pgpt/transfer/PG6932-original4222-v1')
        self.assertIn("('PG6930', (4222, 660, 1669), 0)", raw)
        self.assertIn('changed, added, unchanged = unchanged_physical(', raw)


if __name__ == '__main__':
    unittest.main()
