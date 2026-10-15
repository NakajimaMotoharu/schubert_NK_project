"""Current actual selected bytes, exact grouped count, whole namespace/source."""
import subprocess
import unittest
from pyflakes.api import check
from pg3248_cycle_group_full_six import validate, server_source
from pg3250_cycle_group_full_qualified import server


class WholeGroup(unittest.TestCase):
    def test_actual_selected_bytes_match_current_snapshot(self):
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        validate(head)

    def test_3697_server_and_independent_batch_count(self):
        raw = server_source('0' * 40, '1' * 64)
        self.assertIn('PG3248', raw)
        self.assertNotIn('PG3204', raw)
        self.assertIn('3697', raw)
        # Full source contains the existing complete namespace supplied by the builder.
        self.assertEqual(0, check(raw, '<necessary whole3697>'))
        proof = server()
        self.assertIn("'batch':(1297,173,568)", proof)
        self.assertIn('PG3248', proof)


if __name__ == '__main__':
    unittest.main()
