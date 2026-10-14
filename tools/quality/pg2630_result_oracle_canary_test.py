import unittest
from pyflakes.api import check
from pg2630_result_oracle_canary import SERVER


class OracleCanary(unittest.TestCase):
    def test_isolated_shadow_and_no_coverage_credit(self):
        self.assertEqual(0, check('INPUT={}\n' + SERVER, '<original oracle synthetic canary>'))
        for marker in ['UNAPPROVED_CANARY', '0199', '0101", true', 'coverageCredit',
                       "require(not list(out.rglob('*.exec')))", "result.returncode==0"]:
            self.assertIn(marker, SERVER)
        self.assertIn("engine_version=engines[0].parent.name", SERVER)
        self.assertNotIn('6.0.3', SERVER)
        self.assertNotIn('-javaagent', SERVER)


if __name__ == '__main__':
    unittest.main()
