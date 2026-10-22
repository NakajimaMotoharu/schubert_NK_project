import unittest
from unittest.mock import patch
import pg6910_legacy_receipt_selected as p


class LegacyReceiptDefinitionTest(unittest.TestCase):
    def test_real_declarations_and_all_six_guards(self):
        cases, counts = p.inventory()
        self.assertEqual((25, 9), (sum(counts.values()), len(counts)))
        self.assertEqual({'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'}, set(cases))
        with patch.object(p, 'EXPECTED', (25, 8)), self.assertRaises(ValueError):
            p.inventory()

    def test_old_oracles_main_and_gates_fixed(self):
        with patch.object(p.subprocess, 'check_output', side_effect=[p.TEST + '\n', b'']):
            p.guard('candidate')
        for changes in ('', p.TEST + '\nchanged-main.java'):
            with patch.object(p.subprocess, 'check_output', return_value=changes), self.assertRaises(ValueError):
                p.guard('candidate')
        with patch.object(p.subprocess, 'check_output', side_effect=[p.TEST, b'changed gate']), self.assertRaises(ValueError):
            p.guard('candidate')


if __name__ == '__main__':
    unittest.main()
