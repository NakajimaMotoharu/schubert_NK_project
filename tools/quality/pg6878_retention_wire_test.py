import unittest
from unittest.mock import patch
import pg6878_retention_wire_selected as p


class RetentionWireDefinitionTest(unittest.TestCase):
    def test_actual_declarations_not_vectors_or_module_count(self):
        cases, counts = p.inventory()
        self.assertEqual((29, 10), (sum(counts.values()), len(counts)))
        self.assertEqual({'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'}, set(cases))
        with patch.object(p, 'EXPECTED', (29, 9)), self.assertRaises(ValueError):
            p.inventory()

    def test_no_main_old_oracle_or_gate_change(self):
        with patch.object(p.subprocess, 'check_output', side_effect=[p.TEST + '\n', b'']) as calls:
            p.guard('candidate')
            self.assertEqual(2, calls.call_count)
        for changed in ('', p.TEST + '\nother-main.java\n'):
            with patch.object(p.subprocess, 'check_output', return_value=changed), self.assertRaises(ValueError):
                p.guard('candidate')
        with patch.object(p.subprocess, 'check_output', side_effect=[p.TEST + '\n', b'changed']), self.assertRaises(ValueError):
            p.guard('candidate')


if __name__ == '__main__':
    unittest.main()
