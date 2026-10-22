import unittest
from unittest.mock import patch
import pg6884_data_boundary_selected as p


class DataBoundaryDefinitionTest(unittest.TestCase):
    def test_actual_declarations_not_vector_counts(self):
        cases, counts = p.inventory()
        self.assertEqual((42, 11), (sum(counts.values()), len(counts)))
        self.assertEqual({'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'}, set(cases))
        with patch.object(p, 'EXPECTED', (42, 10)), self.assertRaises(ValueError):
            p.inventory()

    def test_two_new_tests_only(self):
        changed = '\n'.join(sorted(p.TESTS))
        with patch.object(p.subprocess, 'check_output', side_effect=[changed, b'']):
            p.guard('candidate')
        for bad in ('', changed + '\nunexpected-main.java'):
            with patch.object(p.subprocess, 'check_output', return_value=bad), self.assertRaises(ValueError):
                p.guard('candidate')
        with patch.object(p.subprocess, 'check_output', side_effect=[changed, b'changed']), self.assertRaises(ValueError):
            p.guard('candidate')


if __name__ == '__main__':
    unittest.main()
