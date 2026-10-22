import unittest
import pg6890_data4213_whole as p
import pg6892_original4213_artifacts as original


class Grouped4213DefinitionTest(unittest.TestCase):
    def test_four_declarations_all_old_oracles_fixed(self):
        self.assertEqual((4213, 656), p.declared_inventory())
        self.assertEqual(4, len(original.added_cases('HEAD')))

    def test_exact_original_dimensions_and_real_namespace(self):
        raw = p.server_source('0' * 40, '0' * 64)
        for v in ('4213', '656', '1669', 'PG6890'):
            self.assertIn(v, raw)
        self.assertNotIn('4209', raw)
        namespace = p.definitions()['main'].__globals__
        for name in ('server_source', 'driver_source', 'prerequisites', 'original_source'):
            self.assertIs(getattr(p, name), namespace[name])
        raw = original.emitted('0' * 64, '/home/mini/schubert-nk-pgpt/transfer/PG6892-original4213-v1')
        self.assertIn("('PG6890', (4213, 656, 1669), 0)", raw)
        self.assertIn('changed, added, unchanged = unchanged_physical(', raw)
        before = {str(i): 'same' for i in range(1669)}
        self.assertEqual(([], [], 1669), original.unchanged_physical(before, before, set(), (1669, 1669), []))
        for after, owners, counts, added in (
            (dict(before, **{'0': 'changed'}), set(), (1669, 1669), []),
            ({k: v for k, v in before.items() if k != '0'}, set(), (1669, 1668), []),
            (dict(before, extra='new'), set(), (1669, 1670), []),
            (before, {'0'}, (1669, 1669), []),
            (before, set(), (2, 2), []),
            (before, set(), (1669, 1669), ['extra'])):
            with self.assertRaises(ValueError):
                original.unchanged_physical(before, after, owners, counts, added)


if __name__ == '__main__':
    unittest.main()
