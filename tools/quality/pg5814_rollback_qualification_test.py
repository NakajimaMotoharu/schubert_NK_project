import unittest
from pg5814_rollback_qualification import PHYSICAL_KINDS,physical_difference,added_cases,emitted


class Original3955QualificationTest(unittest.TestCase):
    def test_exact_added1_modified8_and_foreign_byte_rejected(self):
        old={str(i):'a'*64 for i in range(1656)}|{k:'a'*64 for k,v in PHYSICAL_KINDS.items()if v!='ADDED_UNCONFIRMED_ROLLBACK_TYPE'}
        new={**old,**{k:'b'*64 for k in PHYSICAL_KINDS}}
        changes,same=physical_difference(old,new,new)
        self.assertEqual((9,1656),(len(changes),same))
        self.assertEqual(1,sum(r['action']=='ADDED'for r in changes))
        with self.assertRaises(ValueError):physical_difference(old,{**new,'0':'c'*64},new)
        self.assertEqual(16,len(added_cases()))

    def test_generated_read_only_original_counts_and_core_are_separate(self):
        raw=emitted({})
        self.assertIn("'tests': 3955",raw);self.assertIn("'suites': 587",raw);self.assertIn("'mainClasses': 1665",raw)
        self.assertIn('coreReceiverTargetFour100',raw)
        self.assertIn("runs/PG5808-six-v1",raw);self.assertIn("runs/PG5780-six-v1",raw)
        self.assertNotIn("runs/PG5754-six-v1",raw)


if __name__=='__main__':unittest.main()
