import ast
import unittest
from pg2572_reuse_pair_selected import native_input, server


class ReuseSelection(unittest.TestCase):
    def test_actual_source_prior_guards_and_current_nine(self):
        value = native_input()
        self.assertEqual(9, len(value['files']))
        self.assertEqual('a60e5716fdf0cbb1e2279b82879d01bf19063fe4f5bd4986142ac70acc40617c',
                         value['guardServerManifestSha256'])

    def test_whole_server_exact_prior_bytes_no_old_native(self):
        raw = server()
        ast.parse(raw)
        for marker in ['PG2572-selected-v3', 'Pg2572ReusePairLauncher', 'PG2570-selected-v2',
                       'PG2568-selected-v2', 'PG2564-native-v1', 'source-full-PG2510',
                       "sha(guard_exec)==guard['execSha256']", 'str(prior_exec),str(guard_exec),str(execfile)']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
