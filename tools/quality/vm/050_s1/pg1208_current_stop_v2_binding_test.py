import ast
import unittest
from pg1198_current_stop_binding_test import fixture as initial
import pg1208_current_stop_v2_binding as p


def fixture():
    f=initial();return dict(f,normalMetadataRecoveryAfterSha256='d85fbf1524fc1edae344b349f7828fac6fd8ff6b763fe635dc1c3b30de4c1247',recoveryActualExit=0)


class V2BindingTest(unittest.TestCase):
    def test_actual_constructor_sql_label_and_all_closure(self):
        v=p.generate(fixture());j=v['Pg1208NativeStop.java'];r=v['pg1208_native_refs.py']
        for part in ['lease=new Pg797OwnedDatabase(db,expected(pid))','s.executeQuery(ownershipSql())','"PG998-native-stop"']:
            self.assertTrue(part in j,part)
        self.assertTrue("a.application_name='PG998-native-stop'" in r)
        for raw in v.values():self.assertFalse('PG1208-native-stop' in raw and 'class Pg1208StopLabelTest'not in raw)
        for name,raw in v.items():
            if name.endswith('.py'):ast.parse(raw)
        for key,value in [('normalMetadataRecoveryAfterSha256',None),('recoveryActualExit',143)]:
            f=fixture();f[key]=value
            with self.assertRaises(ValueError):p.generate(f)


if __name__=='__main__':unittest.main()
