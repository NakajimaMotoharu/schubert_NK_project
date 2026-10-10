import ast
import unittest
from pg1173_runtime_compile import source as compiler
from pg1174_runtime_native import source as transport


class CanonicalRuntimeToolTest(unittest.TestCase):
    def test_exact_new_slots_and_source(self):
        c=compiler();ast.parse(c);self.assertTrue('from pg1172_runtime_sources import files'in c)
        ns={'__name__':'data','__file__':__file__};exec(transport(),ns);s=ns['source']();ast.parse(s)
        for p in ['pg1173-runtime-frozen-v1.safe.json','pg1172-runtime-tools-v1','Pg1172RuntimeResume','pg1174-fixed-stage-v1']:
            self.assertTrue(p in s,p)
        self.assertFalse('pg1162-'in s)


if __name__=='__main__':unittest.main()
