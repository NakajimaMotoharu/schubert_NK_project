import inspect
import unittest
from pyflakes.api import check
import pg2640_wire_oracle_group_full_six as current


class OracleFullPreparation(unittest.TestCase):
    def test_generated_server_source_and_identity(self):
        raw = current.server_source('1' * 40, '2' * 64)
        self.assertEqual(0, check(raw, '<whole oracle full server>'))
        for marker in ['PG2640', '3664', '540', '1643']:
            self.assertIn(marker, raw)
        for old in ['PG2620', '3663', '3657']:
            self.assertNotIn(old, raw)

    def test_source_boundary_only_two_real_tests(self):
        raw = inspect.getsource(current.validate)
        for marker in ['{HEADER, SEMANTIC}', 'normal[\'testSource\']', "mutation['payloadSha256']", "mutationsRejected'] != 36"]:
            self.assertIn(marker, raw)
        self.assertIn('SCOPE', raw)


if __name__ == '__main__':
    unittest.main()
