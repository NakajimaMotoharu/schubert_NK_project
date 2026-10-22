import unittest
from unittest.mock import patch
import pg6916_observation_values_selected as p


class ObservationValueDefinitionTest(unittest.TestCase):
    def test_actual_two_methods_and_three_related_not_vector_count(self):
        cases, counts = p.inventory()
        self.assertEqual((17, 9), (sum(counts.values()), len(counts)))
        self.assertEqual({'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'}, set(cases))
        with patch.object(p, 'EXPECTED', (18, 9)), self.assertRaises(ValueError):
            p.inventory()

    def test_all_main_old_oracles_and_gates_fixed(self):
        with patch.object(p.subprocess, 'check_output', side_effect=[p.TEST, b'']):
            p.guard('candidate')
        for changed in ('', p.TEST + '\nother.java'):
            with patch.object(p.subprocess, 'check_output', return_value=changed), self.assertRaises(ValueError):
                p.guard('candidate')
        with patch.object(p.subprocess, 'check_output', side_effect=[p.TEST, b'gate changed']), self.assertRaises(ValueError):
            p.guard('candidate')


if __name__ == '__main__':
    unittest.main()
