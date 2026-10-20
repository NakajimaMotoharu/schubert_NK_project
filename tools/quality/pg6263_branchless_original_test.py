import inspect
import unittest
from pyflakes.api import check
import pg6263_branchless_original as subject
import pg6042_original3976_artifacts as reader


class Shape(unittest.TestCase):
    def test_no_methods_is_not_proof(self):
        with self.assertRaises(ValueError):subject.no_branches({})

    def test_every_conditional_or_switch_forbids_na(self):
        for op in ('ifeq','ifnonnull','if_icmpeq','if_acmpne','tableswitch','lookupswitch'):
            with self.subTest(op=op),self.assertRaises(ValueError):
                subject.no_branches({'method':'    0: '+op+' 5\n    5: return\n'})

    def test_real_three_method_twenty_six_instruction_shapes(self):
        from pg6248_normal_phase_qualification import original_source
        proof=subject.proof(original_source())
        self.assertEqual(set(subject.OWNERS),set(proof))
        for item in proof.values():
            self.assertEqual((3,26,[]),(item['methodCount'],item['instructionCount'],item['conditionalInstructions']))
            self.assertTrue(item['rawCounterPreserved'])

    def test_emitted_original_reader_keeps_all_strict_bindings(self):
        raw=reader.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6263-definition-only')
        self.assertEqual(0,check(raw,'<original reader>'))
        for token in ("value['classSha256'] != physical[key]","set(branchless) != permitted",
                      "value['conditionalInstructions'] != []","counterNotApplicable=not_applicable"):
            self.assertIn(token,raw)
        source=inspect.getsource(reader.global_four100)
        self.assertIn("('LINE', 'METHOD', 'CLASS', 'BRANCH')",source)


if __name__=='__main__':unittest.main()
