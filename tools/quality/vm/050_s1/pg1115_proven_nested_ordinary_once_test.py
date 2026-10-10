"""Fixed byte-literal closure and current watch, no extra observer/starter."""
import ast
import unittest
from pg1115_proven_nested_ordinary_once import payload


class Once(unittest.TestCase):
    def test_exact_three_source_bound_directories_and_one_start(self):
        s=payload();t=ast.parse(s)
        proof=next(ast.literal_eval(n.value)for n in t.body if isinstance(n,ast.Assign)and any(isinstance(v,ast.Name)and v.id=='SIBLINGS'for v in n.targets))
        self.assertEqual({'pg1107-observer-v1','pg1108-ordinary-cold-once-v1','pg1112-observer-v1'},set(proof))
        self.assertEqual({},proof['pg1108-ordinary-cold-once-v1'])
        self.assertEqual(3,len(proof['pg1107-observer-v1']));self.assertEqual(3,len(proof['pg1112-observer-v1']))
        self.assertEqual('6ba69b4a19d55c927acb24a0343d26e53511a48a8166bd1d87449b3a5f6ca0ae',proof['pg1112-observer-v1']['pg1112_watch_parent.py'])
        self.assertTrue('proven-nested-once-v1'in s);self.assertTrue('current_watch();assert cross_scope'in s)
        self.assertTrue('sibling_proof.proof'in s);self.assertTrue('h.capture()'in s)
        calls=[n for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='run'
                and n.args and isinstance(n.args[0],ast.List)and any(isinstance(a,ast.Constant)and a.value=='--no-block'for a in n.args[0].elts)]
        self.assertEqual(1,len(calls));self.assertEqual('start',ast.literal_eval(calls[0].args[0])[1])


if __name__=='__main__':unittest.main()
