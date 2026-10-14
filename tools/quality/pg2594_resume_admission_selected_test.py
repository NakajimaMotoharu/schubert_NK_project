import ast
import unittest
from pg2594_resume_admission_selected import native_input, server


class ResumeAdmission(unittest.TestCase):
    def test_actual_pair_qualification(self):
        self.assertEqual('5ce2518481a638191b455ef05e37fb5b5a623699972f288e1a0b662ddcabdc05',
                         native_input()['pairServerManifestSha256'])

    def test_whole_server_frozen_same_main(self):
        raw = server()
        ast.parse(raw)
        for marker in ['PG2594-selected-v1', 'PG2592-selected-v2', 'PG2590-selected-v3',
                       'Pg2594ResumeAdmissionLauncher', "sha(pair_exec)==pair['execSha256']",
                       'str(prior_exec),str(original_exec),str(pair_exec),str(execfile)']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
