import unittest
from pgpt_program_proof_lookup import candidate


class ProgramProofLookupTest(unittest.TestCase):
    def receipt(self):
        return dict(source='old-source',actualExit=0,tests=10,
                    inputHashes={'src/module/src/main/java/pkg/Router.java':'fixed-main'},
                    coverage={'pkg/Router':{key:dict(covered=count,missed=0)
                              for key,count in [('LINE',28),('METHOD',4),('CLASS',1),('BRANCH',8)]}})

    def test_old_source_same_main_is_visible_without_acceptance(self):
        row=candidate(self.receipt(),'Router','fixed-main')
        self.assertTrue(row['currentMainByteEqual'])
        self.assertTrue(row['allFourMissedZero'])
        self.assertFalse(row['acceptanceInferred'])
        self.assertFalse(row['permissionInferred'])

    def test_changed_main_keeps_history_but_cannot_transfer(self):
        self.assertFalse(candidate(self.receipt(),'Router','changed-main')['currentMainByteEqual'])

    def test_partial_missing_and_zero_executable_are_not_full(self):
        for key in ['LINE','METHOD','CLASS','BRANCH']:
            value=self.receipt();value['coverage']['pkg/Router'][key]['missed']=1
            self.assertFalse(candidate(value,'Router','fixed-main')['allFourMissedZero'])
        value=self.receipt();del value['coverage']['pkg/Router']['BRANCH']
        self.assertFalse(candidate(value,'Router','fixed-main')['allFourMissedZero'])
        value=self.receipt();value['coverage']['pkg/Router']['LINE']['covered']=0
        self.assertFalse(candidate(value,'Router','fixed-main')['allFourMissedZero'])

    def test_failure_is_retained_not_success(self):
        value=self.receipt();value['actualExit']=1
        self.assertEqual(1,candidate(value,'Router','fixed-main')['originalExit'])

    def test_exact_class_boundary_and_missing_source_are_not_candidates(self):
        self.assertIsNone(candidate(self.receipt(),'Route','fixed-main'))
        value=self.receipt();value['inputHashes']={}
        self.assertIsNone(candidate(value,'Router','fixed-main'))

    def test_noncoverage_manifest_is_not_candidate(self):
        self.assertIsNone(candidate(dict(actualExit=0,tests=99),'Router','fixed-main'))

    def test_natural_zero_branch_is_visible_without_fake_ratio(self):
        value=self.receipt();value['coverage']['pkg/Router']['BRANCH']['covered']=0
        row=candidate(value,'Router','fixed-main')
        self.assertTrue(row['allFourMissedZero'])
        self.assertNotIn('ratio',row)


if __name__=='__main__':
    unittest.main()
