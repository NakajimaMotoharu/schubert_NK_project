import unittest
from pyflakes.api import check
import pg6018_pure_rethrow_facts as t
from source_pure_rethrow_inventory_test import facts


class ActualPureMainInputAndSchemaTest(unittest.TestCase):
    def test_all851_input_namespace_and_no_old_source_binding(self):
        raw=t.input_source();names=sorted(k for k in vars(t.input_engine)if k.isidentifier()and not k.startswith('__')and k!='inputs')
        self.assertEqual(0,check('='.join(names)+'=None\nSTATIC_SHA=None\n'+raw,'<pure current Main namespace>'))
        self.assertIn('len(current)!=851',raw);self.assertIn('len(physical)!=1666',raw)
        self.assertIn('PG6008-api-bounds-static-v1',raw);self.assertIn('pg6006-api-bounds-selected1021-v1/source',raw)

    def test_bad_extents_or_proposal_flags_are_rejected(self):
        row=['PURE_RETHROW','A.java','A#method()','java.lang.RuntimeException','1','1','2','12','3','5','6','12','0','20','true','true','false','true','true','0','1','1','false','true']
        self.assertEqual(1,len(facts('\t'.join(row))))
        for index,value in ((6,'-1'),(8,'13'),(14,'false'),(16,'true'),(19,'2')):
            bad=row.copy();bad[index]=value
            with self.assertRaises(ValueError):facts('\t'.join(bad))


if __name__=='__main__':unittest.main()
