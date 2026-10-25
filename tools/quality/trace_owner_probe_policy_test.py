"""Metadata-only PG-D673 tests. No Java, fixture/probe callback or database is executed."""
import unittest
import trace_owner_join as owner

PATHS = (
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserCommandFaults.java',
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogJdbcFaults.java',
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/UserQueryFaults.java',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/cleanup/ServiceJdbcProbe.java',
    'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/maintenance/MaintenanceJdbcProbe.java',
    'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/CallerMonitorProbe.java')


class ProbePolicyTest(unittest.TestCase):
    def test_six_explicit_shared_oracle_support_paths_only(self):
        for path in PATHS:
            with self.subTest(path=path):
                result = owner.canonical(path,{})
                self.assertEqual('WBS-G03',result['canonicalOwner'])
                self.assertEqual('WBS-G03',result['canonicalCostOwner'])
                self.assertEqual('NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',result['ownershipStatus'])
                self.assertIn('PGD673_1985_EXACT_SHARED_ORACLE_SUPPORT',result['basis'])

    def test_original_logical_owner_and_cost_always_win(self):
        for path in PATHS:
            logical = {path:dict(path=path,owner='WBS-P010-01',costOwner='WBS-P010-02')}
            result = owner.canonical(path,logical)
            self.assertEqual('WBS-P010-01',result['canonicalOwner'])
            self.assertEqual('WBS-P010-02',result['canonicalCostOwner'])
            self.assertEqual('BASELINE_LOGICAL_REFERENCE',result['ownershipStatus'])

    def test_no_suffix_directory_class_or_business_test_generalization(self):
        for path in PATHS:
            for changed in (path.replace('/src/test/java/','/src/main/java/'),path + '.extra',
                path.replace('.java','Test.java'),path.replace('/dev/codex/','/other/codex/')):
                with self.subTest(path=changed):
                    self.assertIsNone(owner.canonical(changed,{})['canonicalOwner'])
        for path in (
            'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/BorrowedJdbcFatal329Test.java',
            'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/TargetBusinessControllerTest.java'):
            self.assertIsNone(owner.canonical(path,{})['canonicalOwner'])

    def test_change_owner_cannot_replace_canonical_or_reassign_cost(self):
        path = PATHS[0]
        original = [dict(path=path,sha256='a'*64,owner='WBS-P018-09')]
        result = owner.join_rows(original,{}, {path:'a'*64},'WBS-G13.07')
        self.assertEqual('WBS-G03',result[0]['canonicalOwner'])
        self.assertEqual('WBS-G03',result[0]['canonicalCostOwner'])
        self.assertEqual('WBS-G13.07',result[0]['changeOwner'])
        self.assertEqual('WBS-P018-09',result[0]['legacyReportedOwner'])
        self.assertIsNone(result[0]['actualAllocatedPp'])
        self.assertFalse(result[0]['historicalCostsReallocated'])
        self.assertFalse(result[0]['currentSourcePtQualificationInferred'])
        invalid = [dict(result[0],canonicalOwner='WBS-G13.07')]
        with self.assertRaises(ValueError):
            owner.validate(invalid,original,{}, {path:'a'*64},'WBS-G13.07')


if __name__ == '__main__':
    unittest.main()
