import ast
import unittest
from pg796_candidate_contract import MODULES,CHANGED,ADDED,verify_delta
from pg796_candidate_build import source


class Test(unittest.TestCase):
    def test_literal_delta_and_reject_every_foreign_module(self):
        old={m:{'literal.class':'1'*64}for m in MODULES};old['batch'].update({n:'2'*64 for n in CHANGED['batch']})
        new={m:dict(v)for m,v in old.items()};new['batch'].update({n:'3'*64 for n in CHANGED['batch']});new['batch'].update({n:'4'*64 for n in ADDED['batch']})
        self.assertEqual(11,verify_delta(old,new))
        for m in MODULES:
            bad={k:dict(v)for k,v in new.items()};bad[m]['literal.class']='5'*64
            with self.assertRaises(ValueError):verify_delta(old,bad)
        for n in ADDED['batch']:
            bad={k:dict(v)for k,v in new.items()};bad['batch'].pop(n)
            with self.assertRaises(ValueError):verify_delta(old,bad)
        raw=source();ast.parse(raw)
        for literal in ('pg750-release-v1','pg796-release-v1','pg794-completion-six-host-v1',"SOURCE = '102cdf1d365ab321f74b523237590eee764ae858'", "OLD_SOURCE = '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'",'gate[\'tests\'] == 3517','gate[\'suites\'] == 520',"'addedAbstractInterfaces': 2, 'addedInternalClasses': 2"):
            self.assertIn(literal,raw)
        self.assertNotIn('NEXT_',raw)


if __name__=='__main__':unittest.main()
