import unittest
import copy
from pg2504_strict_reference_selected import TARGETS, server, validate_method_scope


class Selected(unittest.TestCase):
    def test_exact_changed_methods_and_real_missed_counter_refuse_false_success(self):
        good = {name: {k: {'missed': 0, 'covered': 1} for k in ['LINE', 'METHOD'] + (['BRANCH'] if branch else [])} for name, branch in TARGETS.items()}
        validate_method_scope(good)
        for fault in ['missing', 'unknown', 'missed', 'false', 'zero', 'branch_missing', 'hidden_new_branch']:
            bad = copy.deepcopy(good); first = next(iter(TARGETS))
            if fault == 'missing': del bad[first]
            elif fault == 'unknown': bad['unknown#method'] = bad[first]
            elif fault == 'missed': bad[first]['LINE']['missed'] = 1
            elif fault == 'false': bad[first]['METHOD']['missed'] = False
            elif fault == 'zero': bad[first]['LINE']['covered'] = 0
            elif fault == 'branch_missing': del bad[first]['BRANCH']
            else: bad[[k for k,v in TARGETS.items()if not v][0]]['BRANCH'] = {'missed':1,'covered':1}
            with self.assertRaises(ValueError): validate_method_scope(bad)

    def test_new_main_exact_eight_tests_and_compile_only_dependencies(self):
        raw = server()
        for marker in ['PG2504-selected-v2', 'source-selected-PG2504-v2', 'BrokerJournalEvidenceTest',
                       'mdb2504001CurrentRunReferencePreservesExactIdentityAndRejectsForeignUuid',
                       "'tests':7", "'tests':1", 'dependencyPtCredit', 'sharedCacheWritten',
                       'SCHUBERT_SHELLCHECK', 'nk.pt.node', 'MorningDatabaseSession$Session']:
            self.assertIn(marker, raw)
        self.assertNotIn('CaddyPublicMetadataTest', raw)
        self.assertNotIn('failIfNoSpecifiedTests=false', raw)
        self.assertNotIn('failIfNoTests=false', raw)
        self.assertIn('validate_method_scope(method_scope)', raw)
        self.assertIn("'wholeClassFour100Accepted':False", raw)
        self.assertIn("'nativeNotRun':True", raw)


if __name__ == '__main__':
    unittest.main()
