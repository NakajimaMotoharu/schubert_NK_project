import unittest
from pg2632_result_oracle_rejection import server


class CorrectedOracle(unittest.TestCase):
    def test_baseline_pass_and_each_mutant_assertion_reject(self):
        raw = server()
        for marker in ["if label=='ORIGINAL'", 'result.returncode==0', 'result.returncode==1',
                       'org.opentest4j.AssertionFailedError', 'mutationsRejected', 'baselineRealTestPassed',
                       "require(not list(out.rglob('*.exec')))", 'PG2632-canary-v1']:
            self.assertIn(marker, raw)
        self.assertNotIn('PG2630-canary-v2', raw)
        self.assertNotIn('-javaagent', raw)


if __name__ == '__main__':
    unittest.main()
