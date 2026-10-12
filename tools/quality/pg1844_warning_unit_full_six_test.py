"""Actual count gate and source labels independently fixed to the Unit candidate."""
import ast
import unittest
from pg1844_warning_unit_full_six import server_source,CANDIDATE,OLD
from pg1845_warning_unit_full_qualification import server


class Full(unittest.TestCase):
    def test_actual_count_gate_rejects_partial_exit_oldcounts_and_class_delta(self):
        raw=server_source('1'*40,'2'*64)
        fn=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='complete_result')
        ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual count>','exec'),ns)
        f=ns['complete_result'];self.assertTrue(f(0,True,[],3618,536,1643))
        for bad in [(1,True,[],3618,536,1643),(0,False,[],3618,536,1643),(0,True,['failure'],3618,536,1643),(0,True,[],3596,536,1643),(0,True,[],3618,532,1643),(0,True,[],3618,536,1642)]:self.assertFalse(f(*bad))
        self.assertIn(CANDIDATE,raw);self.assertNotIn(OLD,raw)
        qualifier=server();self.assertIn(CANDIDATE,qualifier)
        self.assertIn('require(changed==[])',qualifier);self.assertIn('require(added==[])',qualifier)
        self.assertIn('==3618',qualifier);self.assertIn('==536',qualifier)


if __name__=='__main__':unittest.main()
