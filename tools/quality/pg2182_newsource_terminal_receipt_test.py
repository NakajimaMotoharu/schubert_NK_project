import ast
import unittest
from pg2021_fresh_resume_terminal_receipt_test import Receipt
import pg2182_newsource_terminal_receipt as p


class ReceiptTest(unittest.TestCase):
    def test_independent_new_and_old_run_vectors(self):
        for code in [0,10]:
            b,s,r,d=Receipt().fixture(code)
            raw=p.payload(dict(b,rootPid=685621));nodes=ast.parse(raw).body
            self.assertIn('0.1.0-PG2126',raw);self.assertNotIn('0.1.0-PG1846',raw)
            ns={};funcs=[n for n in nodes if isinstance(n,ast.FunctionDef)and n.name in {'classify','_normal_classify'}]
            exec(compile(ast.Module(body=funcs,type_ignores=[]),'<actual pure receipt oracle>','exec'),ns)
            self.assertEqual(ns['classify'](b,s,r,d)['completionCode'],code)
            for key,value in [('run','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'),('activation','9026b2ab-bb42-49cd-a2bd-4c661049dce3')]:
                with self.assertRaises(ValueError):ns['classify'](dict(b,**{key:value}),s,r,d)
            with self.assertRaises(ValueError):ns['classify'](None,None,None,None)
        self.assertEqual(p.entry().__globals__['SOURCE'],'3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8')


if __name__=='__main__':unittest.main()
