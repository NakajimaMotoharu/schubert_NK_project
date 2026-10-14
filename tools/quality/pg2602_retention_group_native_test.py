import unittest
from pg2602_retention_group_native_qualified import server, source


class RetainedNative(unittest.TestCase):
    def test_all_main_and_resources_equal(self):
        raw = server()
        for marker in ['source-full-PG2510', 'source-full-PG2600', 'identical_main==1643',
                       'images[0]==images[1]', '3657', 'currentNativeStreams']:
            self.assertIn(marker, raw)

    def test_current_retained_catalog_without_recollection(self):
        raw = source()
        self.assertNotIn('SSH+', raw)
        for marker in ['pg2564-strict-current-native-qualified-v1',
                       'pg2601-retention-group-full-qualified-v1',
                       'pg2602-retention-group-native-qualified-v1', 'inputs[\'selected\']!=catalog[\'selected\']']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
