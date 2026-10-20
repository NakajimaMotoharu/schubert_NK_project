import unittest
import pg6066_original3979_artifacts as t
from pyflakes.api import check


class Current3979ReaderDefinitionTest(unittest.TestCase):
    def test_complete_emitted_namespace_and_localized_no_added_physical(self):
        raw = t.reader.emitted('0'*64, '/home/mini/schubert-nk-pgpt/transfer/PG6066-original3979-v1')
        self.assertEqual(0, check(raw, '<complete configurable original artifact reader>'))
        for prohibited in ('Popen', 'subprocess', 'systemctl', 'qemu-system', 'sudo ', '--recover', '--resume'):
            self.assertNotIn(prohibited, raw)
        owner = 'batch:Expiry.class'
        old = {str(n): 'a' for n in range(1666)} | {owner: 'old'}
        new = old | {owner: 'new'}
        self.assertEqual(([owner], [], 1666), t.reader.physical_difference(old, new, {owner}, [1667, 1667], []))
        for bad in (new | {'0': 'changed'}, new | {'extra': 'new'}, {k: v for k, v in new.items() if k != '0'}):
            with self.assertRaises(ValueError):
                t.reader.physical_difference(old, bad, {owner}, [1667, 1667], [])

    def test_exact_three_new_source_cases_not_inferred_case_arithmetic(self):
        self.assertEqual(t.NEW_METHODS, t.source_test_names(t.ROOT/t.TEST))


if __name__ == '__main__':
    unittest.main()
