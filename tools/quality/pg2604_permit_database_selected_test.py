import unittest
from pg2604_permit_database_selected import native_input, server


class PermitDatabase(unittest.TestCase):
    def test_current_nine_and_fresh3657(self):
        value = native_input()
        self.assertEqual(9, len(value['files']))
        self.assertEqual('8b989c148bd4612b0328e003c91c9f99a68a805f1e70b6218971a2b8c7f79a93', value['manifestSha256'])

    def test_current_fixture_and_whole_namespace(self):
        raw = server()
        for marker in ['PG2604-selected-v1', 'source-full-PG2600', 'PG2602-native-v1',
                       'MorningExpirySessionTest', 'Pg2604PermitDatabaseLauncher', 'prior_exec']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
