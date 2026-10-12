import ast
import unittest
from pg1500_retained_pair_owned_handoff_retry import payload

class HandoffPrefixTest(unittest.TestCase):
    def test_peer_sql_numeric_keyword_boundary(self):
        from pg1501_retained_pair_owned_handoff_retry import payload as newest
        f=next(n for n in ast.parse(newest()).body if isinstance(n,ast.FunctionDef)and n.name=='same_peer')
        assign=f.body[0];self.assertIsInstance(assign,ast.Assign)
        for pid in (2,2147483646):
            sql=eval(compile(ast.Expression(body=assign.value),'<query expression>','eval'),{'BACKEND':pid})
            self.assertIn('where pid='+str(pid)+" and usename='schubert_batch'",sql)
            self.assertIn('begin read only;',sql);self.assertTrue(sql.endswith(';commit;'))
    def test_existing_input_new_output_and_callback_interface(self):
        s=payload();compile(s,'<handoff>','exec')
        self.assertIn('require(os.path.isdir(PAIR_SAVE))',s)
        self.assertNotIn('require(not os.path.lexists(PAIR_SAVE))',s)
        self.assertIn('require(not os.path.lexists(HANDOFF))',s)
        self.assertIn('b76ba20d9c058cbf07f37f47356ba472bc33270d6bfdac9a804a64584923efba',s)
        self.assertIn('pg1500-retained-publication-pair-handoff-v2',s)
        self.assertLess(s.index('contract.terminate_once(92323'),s.index('contract.terminate_once(92297'))
        f={n.name:n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
        for name in ('reserve','before_child','parent_after_child'):self.assertEqual(2,len(f[name].args.args))
        self.assertTrue(any(isinstance(n,ast.Return)and isinstance(n.value,ast.Constant)and n.value.value is True for n in ast.walk(f['wait'])))
        for name in ('before_child','parent_after_child'):self.assertIn('same_peer()',ast.unparse(f[name]))

if __name__=='__main__':unittest.main()
