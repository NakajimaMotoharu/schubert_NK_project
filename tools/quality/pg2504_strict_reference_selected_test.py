import unittest
from pg2504_strict_reference_selected import server


class Selected(unittest.TestCase):
    def test_new_main_exact_eight_tests_and_compile_only_dependencies(self):
        raw = server()
        for marker in ['PG2504-selected-v1', 'source-selected-PG2504', 'BrokerJournalEvidenceTest',
                       'mdb2504001CurrentRunReferencePreservesExactIdentityAndRejectsForeignUuid',
                       "'tests':7", "'tests':1", 'dependencyPtCredit', 'sharedCacheWritten',
                       'SCHUBERT_SHELLCHECK', 'nk.pt.node', 'MorningDatabaseSession$Session']:
            self.assertIn(marker, raw)
        self.assertNotIn('CaddyPublicMetadataTest', raw)
        self.assertNotIn('failIfNoSpecifiedTests=false', raw)
        self.assertNotIn('failIfNoTests=false', raw)
        self.assertIn("['LINE','METHOD','CLASS','BRANCH']", raw)


if __name__ == '__main__':
    unittest.main()
