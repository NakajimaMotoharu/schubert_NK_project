"""Independent strict current scope, fixed shared ancestor and original Root window."""
import ast
import unittest
from pathlib import Path
from pg1111_nested_ordinary_once import payload
from pg1112_fresh_cold_observer import source


class Nested(unittest.TestCase):
    def test_no_rebase_and_live_nine_field_checks_remain_before_one_start(self):
        s=payload();t=ast.parse(s)
        self.assertTrue('pg1106-ordinary-cold-before-v1/nested-once-v1'in s)
        self.assertTrue('cross_scope(before,ordinary_post())and cross_scope(before,ordinary_post())'in s)
        self.assertTrue('return cross.compare(before,actual,CROSS_BEGIN_NS,time.time_ns(),True)'in s)
        self.assertTrue('h.capture()'in s)
        starts=[n for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='run'
                and n.args and isinstance(n.args[0],ast.List)and any(isinstance(a,ast.Constant)and a.value=='--no-block'for a in n.args[0].elts)]
        self.assertEqual(1,len(starts));self.assertNotIn('--resume',ast.literal_eval(starts[0].args[0]))

    def test_observer_full_root_window_comes_from_actual_start_not_cold_wait(self):
        ns={'__file__':str(Path(__file__).with_name('pg1112_fresh_cold_observer.py')),'__name__':'fixture_only'};exec(source(),ns)
        w=ns['watch']();ast.parse(w)
        self.assertTrue("deadline=int(m['ExecMainStartTimestampMonotonic'])/1e6+1860"in w)
        self.assertFalse('deadline=min('in w)
        self.assertTrue('1900'in w)
        # Literal independently measured fake cold wait does not consume Root's
        # separate 1800-second budget, nor extend it beyond its actual start.
        assignments=[n for n in ast.walk(ast.parse(w))if isinstance(n,ast.Assign)
                     and any(isinstance(t,ast.Name)and t.id=='deadline'for t in n.targets)
                     and isinstance(n.value,ast.BinOp)and any(isinstance(a,ast.Constant)
                     and a.value=='ExecMainStartTimestampMonotonic'for a in ast.walk(n.value))]
        self.assertEqual(1,len(assignments))
        data={'m':{'ExecMainStartTimestampMonotonic':'1200000000'},'deadline':1900}
        exec(compile(ast.fix_missing_locations(ast.Module(body=assignments,type_ignores=[])),
                     'actual-observer-window','exec'),data)
        self.assertEqual(3060,data['deadline'])


if __name__=='__main__':unittest.main()
