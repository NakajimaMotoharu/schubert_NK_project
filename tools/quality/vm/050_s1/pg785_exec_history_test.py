"""Independent live/stopped143/0/cold and foreign/partial history refusal."""
import ast
import unittest
from pg785_exec_history import accepted
from pg785_stopped_baseline import source


class Test(unittest.TestCase):
    def test_literal_history_states_and_all_refusals(self):
        before=('/fixed','/fixed literal','no','start','n/a','7','(null)','0')
        closed={'MainPID':'0','ControlPID':'0','Job':'','InvocationID':'abc','Result':'exit-code','ExecMainCode':'1','ExecMainStatus':'143','ExecMainStartTimestampMonotonic':'10','ExecMainExitTimestampMonotonic':'20'}
        after=('/fixed','/fixed literal','no','start','stop','7','exited','143')
        self.assertTrue(accepted(before,after,closed,dict(closed)));self.assertTrue(accepted(before,before,closed,closed))
        for i in range(8):
            bad=list(after);bad[i]='foreign';self.assertFalse(accepted(before,tuple(bad),closed,closed))
        for k in closed:
            bad={**closed,k:'foreign'};self.assertFalse(accepted(before,after,bad,closed))
        self.assertFalse(accepted(None,after,closed,closed));self.assertFalse(accepted(before,None,closed,closed))
        cold={**closed,'InvocationID':'','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0'}
        idle=before[:3]+('n/a','n/a','0','(null)','0/0');self.assertTrue(accepted(before,idle,cold,closed));self.assertFalse(accepted(before,idle,closed,closed))
        normal={**closed,'Result':'success','ExecMainStatus':'0'};self.assertTrue(accepted(before,after[:-1]+('0',),normal,normal))
        ast.parse(source());self.assertIn('pg785-stopped-current-v1',source())


if __name__=='__main__':unittest.main()
