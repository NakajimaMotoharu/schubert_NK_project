"""Independent tool boundary cases; no Product/classfile/VM/file operations in fixtures."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools/quality"))
from pgpt_positive_target_contract import validate_positive_targets as check

class ContractTests(unittest.TestCase):
    def test_mixed_code_and_abstract_targets_stay_in_measurement(self):
        result=check(['A','B'],{'A':{'methods':[{'hasCode':True}]},'B':{'methods':[{'hasCode':False}]}},{'A'})
        self.assertEqual(['A'],result['executableTargets']);self.assertEqual(['B'],result['naturalNoCodeTargets']);self.assertEqual(['A','B'],result['measurementTargetsPreserved']);self.assertEqual([],result['coverageExclusions'])
    def test_missing_executable_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'missing positive'):check(['A'],{'A':{'methods':[{'hasCode':True}]}},set())
    def test_empty_method_annotation_type_is_natural_nocode(self):
        result=check(['A'],{'A':{'methods':[]}},set());self.assertEqual([],result['executableTargets']);self.assertEqual(['A'],result['naturalNoCodeTargets'])
    def test_impossible_positive_nocode_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'contradict'):check(['A'],{'A':{'methods':[{'hasCode':False}]}},{'A'})
    def test_unknown_target_is_not_treated_as_nocode(self):
        with self.assertRaisesRegex(ValueError,'bound classfile'):check(['Unknown'],{},set())
    def test_missing_methods_is_not_treated_as_nocode(self):
        with self.assertRaisesRegex(ValueError,'bound classfile'):check(['A'],{'A':{}},set())
    def test_nonboolean_metadata_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'boolean Code'):check(['A'],{'A':{'methods':[{'hasCode':0}]}},set())
    def test_one_executable_method_among_abstract_methods_requires_probe(self):
        inventory={'A':{'methods':[{'hasCode':False},{'hasCode':True}]}}
        with self.assertRaisesRegex(ValueError,'missing positive'):check(['A'],inventory,set())
        self.assertEqual(['A'],check(['A'],inventory,{'A'})['executableTargets'])

if __name__=='__main__':unittest.main()
