"""Management definitions only; no production test or own fixture execution here."""
import unittest
from unittest.mock import patch
import pg6544_jdbc_transaction_selected as selected
import finite_selected_profile as profile


class TransactionDefinitionTest(unittest.TestCase):
    def test_exact_inventory_compile_before_selected(self):
        _, counts = selected.inventory()
        self.assertEqual((20, 8), (sum(counts.values()), len(counts)))
        raw = profile.runner(20, 8, selected.TARGETS)
        self.assertIn('exits==[0,0,0]', raw)
        self.assertLess(raw.index("['-DskipTests'"), raw.index("['-Dtest='"))

    def test_old_main_and_premature_green_guards(self):
        with patch.object(selected.subprocess, 'check_output', side_effect=[selected.TEST, b'']):
            selected.guard_source('fixture', 'red')
        with patch.object(selected.subprocess, 'check_output', return_value='unrelated Main'):
            with self.assertRaises(ValueError):
                selected.guard_source('fixture', 'red')
        changes = '\n'.join(sorted({selected.TEST} | selected.MAINS))
        with patch.object(selected, 'RED_SOURCE', None), patch.object(selected.subprocess, 'check_output',
                side_effect=[changes, b'']):
            with self.assertRaisesRegex(ValueError, 'oracle bytes'):
                selected.guard_source('fixture', 'green')


if __name__ == '__main__':
    unittest.main()
