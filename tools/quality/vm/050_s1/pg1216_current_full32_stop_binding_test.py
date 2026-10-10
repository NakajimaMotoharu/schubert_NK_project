import ast
import unittest
from pg1208_current_stop_v2_binding_test import fixture as old
import pg1216_current_full32_stop_binding as p


def fixture():
    return dict(old(),full32RecoveryAfterSha256='bc98f52bd67e7b32f54a85d55bf7d8ceb08b97ca6891d081d192d4a4afab935a',full32RecoveryActualExit=0)


class Full32Test(unittest.TestCase):
    def test_same_current_new_full32_seal_not_old20(self):
        v=p.generate(fixture());r=v['pg1216_native_refs.py']
        self.assertTrue(p.BEFORE_PATH in r);self.assertTrue(p.FULL32 in r)
        self.assertFalse('completed-current-before-v1/before.private.json' in r)
        self.assertTrue('config_same(expected,v,exec_record)' in r)
        for name,raw in v.items():
            if name.endswith('.py'):ast.parse(raw)
        for k,value in [('full32RecoveryAfterSha256',None),('full32RecoveryActualExit',143)]:
            f=fixture();f[k]=value
            with self.assertRaises(ValueError):p.generate(f)


if __name__=='__main__':unittest.main()
