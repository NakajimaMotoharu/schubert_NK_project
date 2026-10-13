"""Full actual positive context and immutable new/old receipt guards, all exports required."""
import unittest
from pg2090_current_newrun_owned_stop_sources import sources,BEFORE,TOOLS


class Stop(unittest.TestCase):
    def test_current_whole_source_and_disjoint_receipt_negatives(self):
        values=sources();self.assertEqual(15,len(values))
        receipt=values['pg2090_parent_receipt.py']
        for marker in ["binding.get('activation')=='e31b627c-c0e2-4120-bd64-c0777479e800'",'9026b2ab-bb42-49cd-a2bd-4c661049dce3','204748','113070840714']:
            self.assertTrue(marker in receipt,marker)
        body='\n'.join(values.values())
        for marker in [BEFORE,TOOLS,'114755353173','646556','647598','649480','605603']:
            self.assertTrue(marker in body,marker)


if __name__=='__main__':unittest.main()
