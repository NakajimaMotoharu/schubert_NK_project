import ast
import unittest
from pg2570_failed_guard_selected import native_input, server


class FinalGuardSelection(unittest.TestCase):
    def test_same_current_nine_and_independently_qualified_prior_input(self):
        authority = native_input()
        self.assertEqual(9, len(authority['files']))
        self.assertEqual('137494b161e926bff2a44ce318e49bfbd71dcc0fdb068d15267ec13d6b0a5f5b',
                         authority['priorServerManifestSha256'])

    def test_fresh_one_test_and_prior_exec_have_exact_full_jar_authority(self):
        raw = server()
        ast.parse(raw)
        for marker in ['PG2570-selected-v1', 'Pg2570FailedGuardLauncher', 'PG2568-selected-v2',
                       "prior['input']['full']['jarHashes']==INPUT['full']['jarHashes']",
                       "sha(prior_exec)==prior['execSha256']", '*hosts,*native_streams,str(prior_exec),str(execfile)',
                       "'tests':'1'", 'freshIsolatedPostgres', 'source-full-PG2510']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
