import ast
import unittest
from pg1167_wrong_runtime_compile import source as compiler
from pg1168_wrong_runtime_native import source as transport


class RetireToolTest(unittest.TestCase):
    def test_new_only_slots_source_abi_and_no_start(self):
        s=compiler();ast.parse(s);self.assertTrue('from pg1166_wrong_runtime_sources import files'in s)
        ns={'__file__':__file__,'__name__':'data'};exec(transport(),ns);s=ns['source']();ast.parse(s)
        for p in ['pg1167-runtime-frozen-v1.safe.json','pg1166-runtime-tools-v1','Pg1166WrongRuntimeRetirement','pg1168-fixed-stage-v1']:
            self.assertTrue(p in s,p)
        self.assertFalse('pg1162-'in s)


if __name__=='__main__':unittest.main()
