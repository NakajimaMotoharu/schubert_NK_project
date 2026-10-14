import ast
import unittest
from pg2568_abandoned_pair_selected import native_input, server, SOURCE


class SelectedMatrix(unittest.TestCase):
    def test_actual_current_full_and_nine_latest_never_old_source(self):
        authority = native_input()
        self.assertEqual(9, len(authority['files']))
        self.assertEqual(64, len(authority['manifestSha256']))
        self.assertEqual('a79b45b5858a186fa82bec1ff36882271ab996a4', SOURCE)

    def test_one_selected_test_immutable_main_and_isolated_db(self):
        raw = server()
        ast.parse(raw)
        for marker in ['source-full-PG2510', 'PG2564-native-v1', 'PG2568-selected-v1',
                       'Pg2568AbandonedPairLauncher', "'tests':'1'", 'freshIsolatedPostgres',
                       'classByteMismatch', 'fixturesUnchanged', 'SCHUBERT_PG_ROOT']:
            self.assertIn(marker, raw)
        self.assertNotIn('PG2284-native-v1', raw)
        self.assertNotIn('source-full-PG2228', raw)
        self.assertNotIn('Pg2292MorningGuardLauncher', raw)


if __name__ == '__main__':
    unittest.main()
