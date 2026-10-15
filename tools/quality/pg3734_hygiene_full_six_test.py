import ast
import unittest
import pg3734_hygiene_full_six as current


class Whole(unittest.TestCase):
    def test_identity_bindings_gates_and_all_expected_module_counts(self):
        self.assertEqual(current.SOURCE,current.last_main_source(current.ROOT))
        head='3714'+'a'*36;digest='545'+'b'*61
        raw=current.server_source(head,digest);tree=ast.parse(raw);values=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)]
        self.assertIn(head,values);self.assertIn(digest,values);self.assertIn(current.SOURCE,values);self.assertNotIn(current.previous.SOURCE,values)
        self.assertEqual((3714,545,1643),tuple(sum(v[i]for v in current.EXPECTED.values())for i in range(3)))
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='complete_result');ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<independent finite complete gate>','exec'),ns)
        self.assertTrue(ns['complete_result'](0,True,[],3714,545,1643))
        for bad in [(0,True,[],3712,545,1643),(1,True,[],3714,545,1643),(0,False,[],3714,545,1643),(0,True,['unknown'],3714,545,1643),(0,True,[],3714,544,1643),(0,True,[],3714,545,1642)]:self.assertFalse(ns['complete_result'](*bad))


if __name__=='__main__':unittest.main()
