"""Actual emitted final full-source count schema and corruption negatives."""
import ast
import unittest
from pg1754_host_boundary_full_six import server_source

class Count(unittest.TestCase):
    def test_actual_complete_predicate_requires_all_counts_and_clean_exit(self):
        tree=ast.parse(server_source('1'*40,'2'*64)); fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='complete_result')
        ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual emitted count gate>','exec'),ns)
        f=ns['complete_result'];self.assertTrue(f(0,True,[],3618,536,1643))
        for bad in [(1,True,[],3618,536,1643),(0,False,[],3618,536,1643),(0,True,['failure'],3618,536,1643),(0,True,[],3596,536,1643),(0,True,[],3618,532,1643),(0,True,[],3618,536,1642)]: self.assertFalse(f(*bad))

if __name__=='__main__':unittest.main()
