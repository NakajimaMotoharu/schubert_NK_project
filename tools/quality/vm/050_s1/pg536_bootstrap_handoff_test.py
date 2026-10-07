"""Independent fixed-owner shape/field/children and patched-reader scope oracle."""
import ast
import copy
import pathlib
import unittest


class HandoffTest(unittest.TestCase):
    def test_fixed_owner_and_child_field_types_are_fail_closed(self):
        path=pathlib.Path(__file__).with_name('pg536_bootstrap_owned_handoff_v1.py')
        parsed=ast.parse(path.read_text());env={}
        nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name=='identity']
        self.assertEqual(1,len(nodes))
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<independent identity>','exec'),env)
        value={'pid':42,'ticks':123,'parent':7,'argv':'fixed','uid':['0']*4,'children':{43}}
        self.assertTrue(env['identity'](value,42,123,'fixed',7))
        for key in value:
            for fault in ('missing','null','foreign'):
                bad=copy.deepcopy(value)
                if fault=='missing':del bad[key]
                else:bad[key]=None if fault=='null'else 'foreign'
                self.assertFalse(env['identity'](bad,42,123,'fixed',7))
        for key,v in [('pid',True),('ticks',True),('parent',True),('children',{True}),('children',{None}),('uid',['0','0','1','0'])]:
            self.assertFalse(env['identity']({**value,key:v},42,123,'fixed',7))
        self.assertFalse(env['identity']({**value,'extra':0},42,123,'fixed',7))

    def test_reader_changes_only_one_history_comparison_and_never_operates_units(self):
        base=pathlib.Path(__file__).parent
        original=ast.parse((base/'pg535_bootstrap_existing.py').read_text())
        snapshot=next(n for n in ast.walk(original)if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
        comparisons=[n for n in ast.walk(snapshot)if isinstance(n,ast.Compare)
                     and ast.unparse(n)=="configuration == baseline['configuration']"]
        self.assertEqual(1,len(comparisons))
        source=(base/'pg536_bootstrap_readback.py').read_text()
        self.assertIn('require(changed==1)',source)
        self.assertIn("require(values[u] == old)",source)
        self.assertNotIn("'start','--no-block'",source)
        self.assertNotIn("'stop','--no-block'",source)
        action=(base/'pg536_bootstrap_owned_handoff_v1.py').read_text()
        self.assertEqual(2,action.count('signal.pidfd_send_signal'))
        self.assertLess(action.index("save('term-reserved.private.json'"),action.index('signal.pidfd_send_signal(childfd'))
        self.assertLess(action.index('wait_gone(CHILD)'),action.index('signal.pidfd_send_signal(parentfd'))
        self.assertNotIn('systemctl',action)


if __name__=='__main__':
    unittest.main()
