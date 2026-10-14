import ast
import unittest
from pg2590_original_reinspection_selected import native_input, server


class OriginalReinspection(unittest.TestCase):
    def test_actual_eligibility_and_current_nine(self):
        authority = native_input()
        self.assertEqual(9, len(authority['files']))
        self.assertEqual('962391e6aba39e6064a64ade131d65a9cd2ca805ab2d07b4910765f26f1cbc35',
                         authority['eligibilityServerManifestSha256'])

    def test_whole_selected_prior_bytes_same_jar_and_isolated_db(self):
        raw = server()
        ast.parse(raw)
        for marker in ['PG2590-selected-v2', 'Pg2590OriginalReinspectionLauncher', 'PG2588-selected-v1',
                       "sha(prior_exec)==prior['execSha256']", 'source-full-PG2578',
                       'PG2582-native-v1', '*hosts,*native_streams,str(prior_exec),str(execfile)']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
