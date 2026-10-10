import ast
import unittest
from pg1156_native_five_compile_v4 import source as compiler
from pg1158_native_five_native_v2 import source as transport


class NewManagementTest(unittest.TestCase):
    def test_all_slots_and_runtime_save_are_new(self):
        c=compiler();ast.parse(c)
        self.assertTrue(".replace('pg1148-native-five-recovery-v1','pg1148-native-five-recovery-v2')"in c)
        ns={'__file__':__file__,'__name__':'data'};exec(transport(),ns);s=ns['source']();ast.parse(s)
        for part in ['pg1156-native-five-frozen-v4.safe.json','pg1148-native-five-tools-v4','pg1158-fixed-stage-v1',"'pg1158-'+action+'-v1'"]:
            self.assertTrue(part in s,part)
        self.assertFalse('pg1152-'in s)


if __name__=='__main__':unittest.main()
