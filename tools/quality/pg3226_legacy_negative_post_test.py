"""Exact successful new-cohort post and no failed-stream transport regression."""
import unittest
from pyflakes.api import check
from pg3226_legacy_negative_post import CODE


class ClosedNewCohort(unittest.TestCase):
    def test_complete_namespace_and_closed_independent_post(self):
        raw = 'HASHES={}\n' + CODE
        self.assertEqual(0, check(raw, '<new-cohort independent post>'))
        compile(raw, '<new-cohort independent post>', 'exec')
        for guard in ["whole['actualExit']==0", "whole['cases']==7", "not(root/'failed.safe.json').exists()", "observer-cohort-v3", "cohort-native-v3.exec", "case-cohort-v3", "schubert-nk-bootstrap-admin.service", "o.database()==before['database']", "['StartUnit','StopUnit']", "'oldFailedNativeImported':False", "'PG3222-LFACT-v3'", 'c.runtime_fixed()']:
            self.assertIn(guard, raw)
        for forbidden in ['cohort-native-v2.exec', 'cohort-native.exec', 'systemctl start', 'systemctl stop', 'extractall', 'password', 'vm-access']:
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__':
    unittest.main()
