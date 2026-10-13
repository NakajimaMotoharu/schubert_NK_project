import unittest
from pg2229_root_host_integration_full_qualification import server,qualified_snapshot,validate_test_append,TEST_PATH,production
from pathlib import Path
import subprocess
from pyflakes.api import check


class CurrentFullQualification(unittest.TestCase):
    def test_actual_fixed_append_and_foreign_byte_refused(self):
        root=Path(__file__).resolve().parents[2]
        snapshot='17692bb48193c665072ede64c50c85003a86d1f8'
        old=subprocess.check_output(['git','show',production()+':'+TEST_PATH],cwd=root)
        new=subprocess.check_output(['git','show',snapshot+':'+TEST_PATH],cwd=root)
        self.assertIsNone(validate_test_append(old,new))
        self.assertFalse(qualified_snapshot(root,snapshot))
        for a,b in [(old,new+b' '),(old.replace(b'ROOTCTX',b'OTHER'),new),(old,old),(b'',new)]:
            with self.assertRaises(ValueError):validate_test_append(a,b)
        with self.assertRaises(ValueError):qualified_snapshot(root,production())

    def test_exact_batch_plus_two_and_all_main_physical_delta(self):
        s=server()
        self.assertEqual(0,check(s,'<whole current provenance>'))
        for v in ['PG2228','3633',"'batch':(1236,172,568)",'540','1643',
          'RootStartupContext$NativeIo.class','debugLineQualification','semanticChangedClasses','debugOnlyChangedClasses']:
            self.assertIn(v,s)
        self.assertNotIn('source-full-PG2124',s)
        self.assertNotIn('==3631',s)


if __name__=='__main__':unittest.main()
