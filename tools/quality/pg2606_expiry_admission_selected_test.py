import unittest
from pg2606_expiry_admission_selected import native_input, server


class ExpiryAdmission(unittest.TestCase):
    def test_actual_permit_db_required(self):
        self.assertEqual('58f250297e5bf168346be061f9d4579f62b9619ba71ae2e23d948d89f8dd30a3',
                         native_input()['permitServerManifestSha256'])

    def test_whole_current_server(self):
        raw = server()
        for marker in ['PG2606-selected-v1', 'PG2604-selected-v1', 'source-full-PG2600',
                       'Pg2606ExpiryAdmissionLauncher', 'str(permit_exec),str(execfile)']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
