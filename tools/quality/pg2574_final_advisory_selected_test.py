import ast
import unittest
from pg2574_final_advisory_selected import native_input, server


class FinalAdvisory(unittest.TestCase):
    def test_actual_reuse_and_nine_input_qualification(self):
        value = native_input()
        self.assertEqual(9, len(value['files']))
        self.assertEqual('2dac6dd0edfdb8d440dcd0f3dcf88d62b859ccc8ce975f2ed27a18c0c4707ff8',
                         value['reuseServerManifestSha256'])

    def test_all_fixed_current_inputs_and_one_method(self):
        raw = server()
        ast.parse(raw)
        for marker in ['PG2574-selected-v1', 'Pg2574FinalAdvisoryLauncher', 'PG2572-selected-v3',
                       'PG2570-selected-v2', 'PG2568-selected-v2', 'PG2564-native-v1',
                       'str(prior_exec),str(guard_exec),str(reuse_exec),str(execfile)',
                       "sha(reuse_exec)==reuse['execSha256']", 'source-full-PG2510']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
