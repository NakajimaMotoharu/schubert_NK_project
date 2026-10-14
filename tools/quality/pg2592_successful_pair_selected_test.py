import ast
import unittest
from pg2592_successful_pair_selected import native_input, server


class SuccessfulPair(unittest.TestCase):
    def test_actual_prior_qualification(self):
        value = native_input()
        self.assertEqual(9, len(value['files']))
        self.assertEqual('31be524c6d9b860289878a2a9445cad90381b07a39f956aaaad75066301a741b',
                         value['originalServerManifestSha256'])

    def test_whole_server_isolated_and_exact_bytes(self):
        raw = server()
        ast.parse(raw)
        for marker in ['PG2592-selected-v2', 'PG2590-selected-v3', 'PG2588-selected-v1',
                       'Pg2592SuccessfulPairLauncher', "sha(original_exec)==original['execSha256']",
                       '*hosts,*native_streams,str(prior_exec),str(original_exec),str(execfile)']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
