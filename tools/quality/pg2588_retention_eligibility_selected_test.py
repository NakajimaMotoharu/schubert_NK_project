import ast
import unittest
from pg2588_retention_eligibility_selected import native_input, server


class CurrentEligibility(unittest.TestCase):
    def test_exact_fresh_full_and_current_nine(self):
        authority = native_input()
        self.assertEqual(9, len(authority['files']))
        self.assertEqual('cd2ca7b69f134e0275e18c33a2a443b8c7eef8e8923d54fb5a6564a3b35eb9d9',
                         authority['manifestSha256'])

    def test_whole_isolated_server_no_old_source_or_native(self):
        raw = server()
        ast.parse(raw)
        for marker in ['PG2588-selected-v1', 'Pg2588RetentionEligibilityLauncher', 'source-full-PG2578',
                       'PG2582-native-v1', "'tests':'1'", 'freshIsolatedPostgres', 'classByteMismatch']:
            self.assertIn(marker, raw)
        self.assertNotIn('PG2284-native-v1', raw)
        self.assertNotIn('source-full-PG2228', raw)


if __name__ == '__main__':
    unittest.main()
