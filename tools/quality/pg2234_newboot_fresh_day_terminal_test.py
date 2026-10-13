import ast
import unittest
from pyflakes.api import check
from pg2021_fresh_resume_terminal_receipt_test import Receipt
import pg2234_newboot_fresh_day_terminal as p


class CurrentTerminal(unittest.TestCase):
    def test_whole_actual_source_and_independent_normal_foreign_vectors(self):
        for code in [0,10]:
            b,s,r,d=Receipt().fixture(code)
            raw=p.payload(dict(b,rootPid=123))
            self.assertEqual(0,check(raw,'<actual full terminal>'))
            self.assertIn('pg2234-newboot-fresh-day-terminal-v1',raw)
            nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name in {'classify','_normal_classify'}]
            ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<independent receipt vectors>','exec'),ns)
            result=ns['classify'](b,s,r,d)
            self.assertEqual(code,result['completionCode'])
            for key,value in [('run','02bddddf-9cd3-4668-9d67-7561232fc4e4'),('activation','20b86040-ffd5-4d17-9fca-5d83048ba905')]:
                with self.assertRaises(ValueError):ns['classify'](dict(b,**{key:value}),s,r,d)
            with self.assertRaises(ValueError):ns['classify'](None,None,None,None)
        self.assertEqual(p.entry().__globals__['SLOT'],p.SLOT)


if __name__=='__main__':unittest.main()
