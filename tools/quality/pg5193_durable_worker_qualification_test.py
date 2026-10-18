import unittest
import pg5122_root_elf_public as public


class SeparateQualification(unittest.TestCase):
    def values(self):
        original={'actualExit':1,'phaseExits':[0,0],
            'reasons':['declared semantic changes plus explicitly bounded nested debug candidates only'],
            'sourceSnapshot':'fixed-source','xmlSha256':{'one':'digest'},'tests':684,'suites':85}
        qualified={**original,'actualExit':0,'reasons':[],
            'originalRunnerActualExit':1,'originalManifestSha256':'original-sha'}
        return original,qualified

    def test_explicit_original1_with_successful_maven_is_retained(self):
        original,result=self.values()
        public.validate_separate_qualification(result,original,'original-sha')
        self.assertEqual(original['actualExit'],1)
        self.assertEqual(original['reasons'],['declared semantic changes plus explicitly bounded nested debug candidates only'])

    def test_any_compile_or_pt_failure_cannot_be_relabelled(self):
        for change in ({'phaseExits':[0,1]},{'reasons':['failed testcase']},{'actualExit':0}):
            original,result=self.values();original.update(change)
            with self.assertRaises(ValueError):public.validate_separate_qualification(result,original,'original-sha')

    def test_source_xml_count_or_original_hash_cannot_be_substituted(self):
        for change in ({'sourceSnapshot':'other'},{'xmlSha256':{'one':'changed'}},{'tests':685},
                       {'originalManifestSha256':'wrong'},{'originalRunnerActualExit':0}):
            original,result=self.values();result.update(change)
            with self.assertRaises(ValueError):public.validate_separate_qualification(result,original,'original-sha')


if __name__=='__main__':unittest.main()
