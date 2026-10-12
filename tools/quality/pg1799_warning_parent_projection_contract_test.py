"""Actual independent normal failure data and every field/GC/foreign counterexample."""
import unittest
from pg1799_warning_parent_projection_contract import qualify_warning_parent


class Parent(unittest.TestCase):
    def fixture(self):
        return {'MainPID':'0','ControlPID':'0','Job':'','ActiveState':'failed','SubState':'failed','Result':'exit-code','ExecMainCode':'1','ExecMainStatus':'10','InvocationID':'b5a12ee25dc44ec49b08f5d084b4052f','ExecMainStartTimestampMonotonic':'81404764713','ExecMainExitTimestampMonotonic':'83018952135','Type':'oneshot','SuccessExitStatus':''}

    def test_warning_original_does_not_make_manager_success(self):
        fields=self.fixture();result=qualify_warning_parent(fields,True)
        self.assertTrue(result['managerFailureRetained']);self.assertFalse(result['genuinePid1StartDone']);self.assertFalse(result['stopAuthority'])
        for key in fields:
            bad={**fields,key:None}
            with self.subTest(key=key),self.assertRaises(ValueError):qualify_warning_parent(bad,True)
        for field,value in [('ActiveState','inactive'),('SubState','dead'),('Result','success'),('ExecMainStatus','30'),('InvocationID',''),('Type','simple'),('SuccessExitStatus','10')]:
            with self.assertRaises(ValueError):qualify_warning_parent({**fields,field:value},True)
        for bad in [None,[],True]:
            with self.assertRaises(ValueError):qualify_warning_parent(bad,True)


if __name__=='__main__':unittest.main()
