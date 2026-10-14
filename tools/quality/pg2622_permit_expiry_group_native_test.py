import unittest
from pg2622_permit_expiry_group_native_qualified import server, source


class CurrentNativeFull(unittest.TestCase):
    def test_full3663_all_main_resource_byte_bridge(self):
        raw = server()
        for marker in ['source-full-PG2510', 'source-full-PG2620', 'identical_main==1643',
                       'images[0]==images[1]', '3663', 'qualified2620Tests']:
            self.assertIn(marker, raw)
        self.assertNotIn('3657', raw)

    def test_no_vm_recapture_and_fixed_catalog(self):
        raw = source()
        self.assertNotIn('SSH+', raw)
        for marker in ['pg2564-strict-current-native-qualified-v1',
                       'pg2621-permit-expiry-group-full-qualified-v1',
                       'pg2622-permit-expiry-group-native-qualified-v1']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
