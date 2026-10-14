import unittest
from pg2608_expiry_handoff_selected import native_input, server


class ExpiryHandoff(unittest.TestCase):
    def test_actual_admission_required(self):
        self.assertEqual('331e4bef18d737d7fd75ac5ad1e1e3a48795ce2f12e4ab1db9dc652871791665',
                         native_input()['expiryServerManifestSha256'])

    def test_whole_current_server(self):
        raw = server()
        for marker in ['PG2608-selected-v1', 'PG2606-selected-v1', 'source-full-PG2600',
                       'Pg2608ExpiryHandoffLauncher', 'str(expiry_exec),str(execfile)']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
