"""Independent actual full-source completion gate: never a limited/native surrogate."""
import ast
import unittest
import pg1633_api_boundary_full_six as p


class FullSixGateTest(unittest.TestCase):
    def test_actual_counts_and_failure_cases_without_execution(self):
        raw=p.server_source('a'*40,'b'*64);tree=ast.parse(raw)
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='complete_result')
        scope={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual whole-source gate>','exec'),scope)
        check=scope['complete_result'];self.assertTrue(check(0,True,[],3596,532,1643))
        for args in [(143,True,[],3596,532,1643),(0,False,[],3596,532,1643),(0,True,['failed'],3596,532,1643),(0,True,[],13,4,321),(0,True,[],3595,532,1643),(0,True,[],3596,531,1643),(0,True,[],3596,532,1642),(False,True,[],3596,532,1643)]:self.assertFalse(check(*args))
        self.assertNotIn('-DfailIfNoTests=false',raw);self.assertNotIn('-Dtest=',raw)
        self.assertIn(p.PRODUCTION,raw)


if __name__=='__main__':unittest.main()
