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

    def legacy(self):
        return dict(source='legacy-source',actualExit=0,tests=4,sourcePhysicalScopeComplete=True,
                    begin=dict(targetPhysicalClasses=['pkg/Port'],targetMainSourceSha256='a'*64,
                               testPath='src/module/src/test/java/pkg/PortContractTest.java'),
                    counters={key:dict(covered=count,missed=0) for key,count in [('LINE',4),('METHOD',1),('CLASS',1)]},
                    branch=dict(covered=0,missed=0,meaning='NATURAL_ZERO_NO_SOURCE_CONDITIONAL_INSTRUCTIONS_NA'))

    def test_legacy_single_target_binds_exact_hash_and_main_module(self):
        row=candidate(self.legacy(),'Port','a'*64)
        self.assertEqual('src/module/src/main/java/pkg/Port.java',row['mainPath'])
        self.assertEqual('SINGLE_TARGET_COUNTERS_BEGIN',row['evidenceSchema'])
        self.assertTrue(row['currentMainByteEqual'])
        self.assertTrue(row['lineMethodClassMissedZero'])
        self.assertEqual('EXPLICIT_NATURAL_ZERO_NOT_BRANCH100',row['branchAssessment'])
        self.assertNotIn('BRANCH',row['fourCounters'])
        self.assertFalse(row['allFourMissedZero'])
        self.assertFalse(row['acceptanceInferred'])
        self.assertFalse(row['permissionInferred'])

    def test_legacy_different_byte_is_history_only(self):
        self.assertFalse(candidate(self.legacy(),'Port','b'*64)['currentMainByteEqual'])

    def test_legacy_multiple_physical_targets_never_split_aggregate(self):
        value=self.legacy();value['begin']['targetPhysicalClasses'].append('pkg/Other')
        self.assertIsNone(candidate(value,'Port','a'*64))

    def test_legacy_missing_hash_or_incomplete_scope_is_not_bound(self):
        for key in ['targetMainSourceSha256','targetPhysicalClasses','testPath']:
            value=self.legacy();del value['begin'][key]
            self.assertIsNone(candidate(value,'Port','a'*64))
        value=self.legacy();value['sourcePhysicalScopeComplete']=False
        self.assertIsNone(candidate(value,'Port','a'*64))

    def test_legacy_unsafe_or_ambiguous_paths_are_rejected(self):
        for key,value in [('testPath','src/module/../src/test/java/pkg/PortTest.java'),
                          ('testPath','elsewhere/pkg/PortTest.java'),
                          ('targetPhysicalClasses',['pkg/../Port']),
                          ('targetMainSourceSha256','unknown')]:
            receipt=self.legacy();receipt['begin'][key]=value
            self.assertIsNone(candidate(receipt,'Port','a'*64))

    def test_missing_natural_zero_evidence_stays_unmeasured(self):
        value=self.legacy();del value['branch']
        self.assertEqual('UNMEASURED',candidate(value,'Port','a'*64)['branchAssessment'])
        value=self.legacy();value['branch']['meaning']='guessed'
        self.assertEqual('UNMEASURED',candidate(value,'Port','a'*64)['branchAssessment'])

    def test_booleans_and_negative_counters_are_not_measured_zero(self):
        for field,bad in [('covered',True),('covered',-1),('missed',False),('missed',1)]:
            value=self.legacy();value['counters']['METHOD'][field]=bad
            self.assertFalse(candidate(value,'Port','a'*64)['lineMethodClassMissedZero'])

    def test_legacy_failure_is_not_converted_to_success(self):
        value=self.legacy();value['actualExit']=143
        self.assertEqual(143,candidate(value,'Port','a'*64)['originalExit'])

    def source_units(self):
        return dict(source='original-unit-source', actualExit=0, tests=14,
                    sourcePins={'src/module/src/main/java/pkg/Port.java': 'a'*64},
                    sourceUnits={'pkg/Port': dict(normalClassSha256='b'*64, crc64='1234567890abcdef',
                        counters={key:dict(covered=count,missed=0) for key,count in
                                  [('LINE',66),('METHOD',10),('CLASS',1),('BRANCH',42)]})})

    def test_source_units_exact_class_pin_and_normal_identity(self):
        row=candidate(self.source_units(),'Port','a'*64)
        self.assertEqual('SOURCE_UNITS_SOURCE_PINS',row['evidenceSchema'])
        self.assertEqual('src/module/src/main/java/pkg/Port.java',row['mainPath'])
        self.assertEqual('b'*64,row['declaredNormalClassSha256'])
        self.assertEqual('1234567890abcdef',row['declaredCrc64'])
        self.assertTrue(row['currentMainByteEqual'])
        self.assertTrue(row['allFourMissedZero'])

    def test_source_units_failure_and_changed_bytes_stay_visible(self):
        value=self.source_units();value['actualExit']=143
        row=candidate(value,'Port','c'*64)
        self.assertEqual(143,row['originalExit'])
        self.assertFalse(row['currentMainByteEqual'])
        self.assertFalse(row['wholeSourceQualificationInferred'])

    def test_source_units_partial_and_missing_branch_are_not_full(self):
        value=self.source_units();value['sourceUnits']['pkg/Port']['counters']['BRANCH']['missed']=1
        self.assertFalse(candidate(value,'Port','a'*64)['allFourMissedZero'])
        del value['sourceUnits']['pkg/Port']['counters']['BRANCH']
        row=candidate(value,'Port','a'*64)
        self.assertFalse(row['allFourMissedZero'])
        self.assertEqual('UNMEASURED',row['branchAssessment'])

    def test_source_units_missing_fields_do_not_fall_back_or_guess(self):
        for key in ['sourceUnits','sourcePins']:
            value=self.source_units();del value[key]
            self.assertIsNone(candidate(value,'Port','a'*64))
        for key in ['normalClassSha256','crc64','counters']:
            value=self.source_units();del value['sourceUnits']['pkg/Port'][key]
            self.assertIsNone(candidate(value,'Port','a'*64))

    def test_source_units_ambiguous_class_and_source_pin_rejected(self):
        value=self.source_units();value['sourceUnits']['other/Port']=value['sourceUnits']['pkg/Port']
        self.assertIsNone(candidate(value,'Port','a'*64))
        value=self.source_units();value['sourcePins']['src/other/src/main/java/pkg/Port.java']='a'*64
        self.assertIsNone(candidate(value,'Port','a'*64))

    def test_source_units_unsafe_paths_or_incorrect_module_namespace_rejected(self):
        for path in ['src/../src/main/java/pkg/Port.java','src/module/src/main/java/pkg/../Port.java',
                     'private/pkg/Port.java','src/module//src/main/java/pkg/Port.java',
                     'src/module/src/main/java/pkg\\Port.java']:
            value=self.source_units();value['sourcePins']={path:'a'*64}
            self.assertIsNone(candidate(value,'Port','a'*64))

    def test_source_units_malformed_hash_crc_and_aggregate_scope_rejected(self):
        for key,bad in [('normalClassSha256','unknown'),('normalClassSha256',None),
                        ('crc64','short'),('crc64',12)]:
            value=self.source_units();value['sourceUnits']['pkg/Port'][key]=bad
            self.assertIsNone(candidate(value,'Port','a'*64))
        for count in [2,True,-1]:
            value=self.source_units();value['sourceUnits']['pkg/Port']['counters']['CLASS']['covered']=count
            self.assertIsNone(candidate(value,'Port','a'*64))
        value=self.source_units();value['sourcePins']['src/module/src/main/java/pkg/Port.java']='unknown'
        self.assertIsNone(candidate(value,'Port','a'*64))

    def test_source_units_tool_main_path_is_explicitly_supported(self):
        value=self.source_units();value['sourcePins']={'program/characterization/src/main/java/pkg/Port.java':'a'*64}
        row=candidate(value,'Port','a'*64)
        self.assertEqual('program/characterization/src/main/java/pkg/Port.java',row['mainPath'])
        self.assertFalse(row['wholeSourceQualificationInferred'])

    def test_source_units_test_pin_cannot_masquerade_as_main(self):
        value=self.source_units();value['sourcePins']={'src/module/src/test/java/pkg/Port.java':'a'*64}
        self.assertIsNone(candidate(value,'Port','a'*64))
        value=self.source_units();value['sourceUnits']={'pkg/Other':value['sourceUnits']['pkg/Port']}
        self.assertIsNone(candidate(value,'Port','a'*64))

    def test_source_units_never_transfer_source_or_permission(self):
        value=self.source_units();value['scope']='FULL_SOURCE_100_AND_ACCEPTED_BY_SOMEONE'
        row=candidate(value,'Port','a'*64)
        self.assertFalse(row['wholeSourceQualificationInferred'])
        self.assertFalse(row['acceptanceInferred'])
        self.assertFalse(row['permissionInferred'])
        self.assertEqual('NAMED_CLASS_OR_METHOD_SUBSET_COUNTERS',row['counterScope'])


    def provenance(self):
        return dict(source='1'*40, actualExit=0, tests=8,
                    inputProvenance=dict(source='1'*40,
                        mainInputPath='src/module/src/main/java/pkg/Sender.java',mainInputHash='a'*64,
                        testInputPath='src/module/src/test/java/pkg/SenderContractTest.java',testInputHash='c'*64),
                    physical={'pkg/Sender':'b'*64},physicalClosureComplete=True,
                    counterExclusions=[],oldExecCombined=False,
                    crc=[['1234567890abcdef','pkg/Sender']],
                    counters={key:dict(covered=count,missed=0) for key,count in
                              [('LINE',49),('METHOD',9),('CLASS',1),('BRANCH',18)]})

    def test_provenance_explicit_single_target_is_visible_without_acceptance(self):
        row=candidate(self.provenance(),'Sender','a'*64)
        self.assertIsNotNone(row)
        self.assertEqual('SINGLE_TARGET_INPUT_PROVENANCE',row['evidenceSchema'])
        self.assertEqual('src/module/src/main/java/pkg/Sender.java',row['mainPath'])
        self.assertEqual('b'*64,row['declaredNormalClassSha256'])
        self.assertEqual('1234567890abcdef',row['declaredCrc64'])
        self.assertTrue(row['currentMainByteEqual'])
        self.assertTrue(row['allFourMissedZero'])
        self.assertFalse(row['wholeSourceQualificationInferred'])
        self.assertFalse(row['acceptanceInferred'])
        self.assertFalse(row['permissionInferred'])

    def test_provenance_failure_partial_and_changed_bytes_remain_history(self):
        value=self.provenance();value['actualExit']=143
        row=candidate(value,'Sender','d'*64)
        self.assertEqual(143,row['originalExit'])
        self.assertFalse(row['currentMainByteEqual'])
        value['counters']['BRANCH']['missed']=1
        self.assertFalse(candidate(value,'Sender','a'*64)['allFourMissedZero'])

    def test_provenance_missing_hash_path_or_physical_never_guesses(self):
        for key in ['mainInputPath','mainInputHash','testInputPath','testInputHash','source']:
            value=self.provenance();del value['inputProvenance'][key]
            self.assertIsNone(candidate(value,'Sender','a'*64),key)
        for key in ['physical','physicalClosureComplete','crc','counterExclusions','oldExecCombined']:
            value=self.provenance();del value[key]
            self.assertIsNone(candidate(value,'Sender','a'*64),key)

    def test_provenance_aggregate_incomplete_excluded_or_combined_scope_is_rejected(self):
        for key,bad in [('physical',{'pkg/Sender':'b'*64,'pkg/Other':'c'*64}),
                        ('physicalClosureComplete',False),('counterExclusions',['private-helper']),
                        ('oldExecCombined',True)]:
            value=self.provenance();value[key]=bad
            self.assertIsNone(candidate(value,'Sender','a'*64),key)
        value=self.provenance();value['counters']['CLASS']['covered']=2
        self.assertIsNone(candidate(value,'Sender','a'*64))

    def test_provenance_unsafe_or_mismatched_source_namespace_is_rejected(self):
        for key,bad in [('mainInputPath','src/module/src/main/java/pkg/../Sender.java'),
                        ('mainInputPath','src/module/src/main/java/elsewhere/Sender.java'),
                        ('mainInputPath','src/module/src/test/java/pkg/Sender.java'),
                        ('testInputPath','src/other/src/test/java/pkg/SenderTest.java'),
                        ('testInputPath','src/module/src/test/java/pkg/../SenderTest.java'),
                        ('mainInputHash','unknown'),('testInputHash','unknown'),('source','2'*40)]:
            value=self.provenance();value['inputProvenance'][key]=bad
            self.assertIsNone(candidate(value,'Sender','a'*64),(key,bad))
        self.assertIsNone(candidate(self.provenance(),'Send','a'*64))
        value=self.provenance();value['physical']={'pkg/Sender':'not-a-hash'}
        self.assertIsNone(candidate(value,'Sender','a'*64))

    def test_provenance_invalid_ambiguous_or_mismatched_crc_is_rejected(self):
        for bad in [None,[],[['unknown','pkg/Sender']], [['1234567890abcdef','pkg/Other']],
                    [['1234567890abcdef','pkg/Sender'],['1234567890abcdef','pkg/Sender']],
                    {'pkg/Sender':'1234567890abcdef'},[['1234567890abcdef']]]:
            value=self.provenance();value['crc']=bad
            self.assertIsNone(candidate(value,'Sender','a'*64),bad)

    def test_provenance_absent_branch_or_malformed_counters_never_means_four100(self):
        value=self.provenance();del value['counters']['BRANCH']
        row=candidate(value,'Sender','a'*64)
        self.assertEqual('UNMEASURED',row['branchAssessment'])
        self.assertFalse(row['allFourMissedZero'])
        for bad in [True,-1,None]:
            value=self.provenance();value['counters']['METHOD']['covered']=bad
            self.assertFalse(candidate(value,'Sender','a'*64)['allFourMissedZero'])

    def test_provenance_invalid_marker_does_not_fall_back_to_guessed_legacy(self):
        value=self.legacy();value['inputProvenance']={}
        self.assertIsNone(candidate(value,'Port','a'*64))


if __name__=='__main__':
    unittest.main()
