import unittest
import subprocess
import pg5848_protocol_expression_static as target


class ProtocolExpressionDeltaTest(unittest.TestCase):
    def test_actual_all_source_rewrite_plan_and_no_business_replacement(self):
        from pg5540_snapshot_scratch_selected import ROOT
        self.assertEqual(6,len(target.MODIFIED))
        for path in target.MODIFIED:
            before=subprocess.check_output(['git','show','6b5cea563b6f68b0b604afc06490063793e49662:'+path],cwd=ROOT,text=True);after=target.expected_source(path,before)
            self.assertNotEqual(before,after)
            with self.assertRaises(ValueError):target.expected_source(path,after)
        raw=target.runner_source();self.assertIn("expected_counts['AvoidLiteralsInIfCondition']-=7",raw)
        self.assertIn("expected_counts['AssignmentInOperand']-=1",raw)
        self.assertNotIn('failIfNoTests=false',raw)

    def test_every_outer_required_and_unrelated_owner_byte_change_rejected(self):
        outer={target.class_key(p)for p in target.MODIFIED};old={str(i):'old'for i in range(1666-len(outer)-1)}|{k:'old'for k in outer};nested=next(iter(outer))[:-6]+'$Synthetic.class';old[nested]='old'
        current={**old,**{k:'new'for k in outer},nested:'new'}
        self.assertEqual(7,len(target.class_contract(old,current)))
        with self.assertRaises(ValueError):target.class_contract(old,{**current,'0':'unrelated'})
        name=next(iter(outer))
        with self.assertRaises(ValueError):target.class_contract(old,{**current,name:'old'})


if __name__=='__main__':unittest.main()
