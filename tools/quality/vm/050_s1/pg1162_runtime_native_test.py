import ast
import unittest
from pg1161_runtime_compile import source as compiler
from pg1162_runtime_native import source as transport


class RuntimeToolTest(unittest.TestCase):
    def test_current_new_only_closed_inputs(self):
        c=compiler();ast.parse(c)
        for p in ['from pg1160_runtime_sources import files','pg1160-runtime-tools-v1','pg1161-runtime-frozen-v1',"'pg1160*test.py'",'text.encode()']:
            self.assertTrue(p in c,p)
        self.assertFalse('native-five-directory-oracle'in c)
        n={'__name__':'data','__file__':__file__};exec(transport(),n);s=n['source']();ast.parse(s)
        for p in ['Pg1160RuntimeResume','pg1162-fixed-stage-v1',"'pg1162-'+action+'-v1'","len(frozen['phases'])==2"]:
            self.assertTrue(p in s,p)
        self.assertFalse('pg1158-'in s)


if __name__=='__main__':unittest.main()
