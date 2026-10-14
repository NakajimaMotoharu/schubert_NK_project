import subprocess
import unittest
from pg2620_permit_expiry_group_full_six import validate, server_source
from pg2621_permit_expiry_group_full_qualified import server


class PermitExpiryFull(unittest.TestCase):
    def test_whole_latest_selected_test_source(self):
        validate(subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())

    def test_fixed_full_namespace(self):
        raw = server_source('0' * 40, '1' * 64)
        self.assertIn('PG2620', raw)
        self.assertIn('3663', raw)
        self.assertNotIn('PG2600', raw)

    def test_independent_batch_xml_count(self):
        self.assertIn("'batch':(1266,172,568)", server())


if __name__ == '__main__':
    unittest.main()
