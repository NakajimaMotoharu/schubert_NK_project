import unittest
from pg2494_current_boundary_full_six import SOURCE, server_source, validate
import subprocess


class Full(unittest.TestCase):
    def test_exact_selected_source_and_fresh_full_counts(self):
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        validate(head)
        raw = server_source(head, 'a' * 64)
        for marker in ['PG2494', '3649', '1643', SOURCE]:
            self.assertIn(marker, raw)
        self.assertNotIn('source-full-PG2404', raw)
        self.assertNotIn('PG2404-six-v1', raw)


if __name__ == '__main__':
    unittest.main()
