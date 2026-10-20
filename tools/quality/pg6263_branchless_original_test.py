import copy
import inspect
import json
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

    def actual(self):
        from pg5940_private_lock_compile import BASE
        q=json.loads((BASE/'PG6244-current4034-cases/qualification.json').read_bytes())
        return q['changedOuterCounters'],{k:v['BRANCH']for k,v in q['counterNotApplicable'].items()},q

    def test_actual_returned_counter_shape_is_preserved_without_zero_injection(self):
        targets,proof,q=self.actual();before=copy.deepcopy(targets)
        result=reader.counter_applicability(targets,proof,q['allPhysicalMainSha256'],q['productionSource'],'PG6244')
        self.assertEqual(q['counterNotApplicable'],result)
        self.assertEqual(before,targets)
        for key in proof:self.assertNotIn('BRANCH',targets[key])

    def test_wrong_source_hash_condition_method_count_raw_shape_and_campaign_rejected(self):
        targets,proof,q=self.actual();key=subject.OWNERS[0]
        for field,value in (('source','0'*40),('classSha256','0'*64),('conditionalInstructions',['ifnonnull']),
                            ('methodCount',2),('instructionCount',0),('rawCounterPreserved',False)):
            bad=copy.deepcopy(proof);bad[key][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                reader.counter_applicability(targets,bad,q['allPhysicalMainSha256'],q['productionSource'],'PG6244')
        for campaign in ('PG6212','PG9999'):
            with self.assertRaises(ValueError):reader.counter_applicability(targets,proof,q['allPhysicalMainSha256'],q['productionSource'],campaign)
        with self.assertRaises(ValueError):reader.counter_applicability(targets,{},q['allPhysicalMainSha256'],q['productionSource'],'PG6244')
        extra=copy.deepcopy(targets);extra[key]['BRANCH']={'missed':0,'covered':0}
        with self.assertRaises(ValueError):reader.counter_applicability(extra,proof,q['allPhysicalMainSha256'],q['productionSource'],'PG6244')


if __name__=='__main__':unittest.main()
