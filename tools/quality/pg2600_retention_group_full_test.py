import subprocess
import unittest
from pg2600_retention_group_full_six import validate, server_source
from pg2601_retention_group_full_qualified import server


class RetentionGroupFull(unittest.TestCase):
    def test_actual_same_test_provenance(self):
        validate(subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())

    def test_fixed_counts_and_namespace(self):
        raw = server_source('0' * 40, '1' * 64)
        self.assertIn('PG2600', raw)
        self.assertIn('3657', raw)
        self.assertNotIn('PG2578', raw)

    def test_independent_xml_batch_count(self):
        raw = server()
        self.assertIn("'batch':(1260,172,568)", raw)
        self.assertIn('3657', raw)


if __name__ == '__main__':
    unittest.main()
