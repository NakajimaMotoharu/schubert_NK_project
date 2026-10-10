import ast
import unittest
from pg1152_native_five_native import source


class TransportTest(unittest.TestCase):
    def test_new_only_slots_current_abi_and_no_guest_fixture(self):
        s=source();ast.parse(s)
        for part in ['pg1151-native-five-frozen-v3.safe.json','pg1148-native-five-tools-v3','pg1152-fixed-stage-v1',"'pg1152-'+action+'-v1'",'len(frozen[\'phases\'])==3','Pg1148NativeRolePreparation']:
            self.assertTrue(part in s,part)
        ns={'__name__':'not_main','__file__':__file__};exec(compile(s,'<contract>','exec'),ns)
        generated=ns['source']();ast.parse(generated)
        self.assertFalse("prefix+'Pg1148NativeRoleDirectoryTest'"in generated)
        self.assertTrue("prefix+'Pg1148NativeRolePreparation '+action"in generated)


if __name__=='__main__':unittest.main()
