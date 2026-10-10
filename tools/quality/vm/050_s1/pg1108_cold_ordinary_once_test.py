"""Independent fixed before scope/order/single external start and observer source."""
import ast
import unittest
from pathlib import Path
from pg1106_ordinary_cold_before import payload as before
from pg1107_cold_current_observer import source as observer
from pg1108_cold_ordinary_once import payload as once


def pins(code):
    return [ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(code))
            if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='pin']


class Ordinary(unittest.TestCase):
    def test_scope_matches_before_and_durable_guard_precedes_one_start(self):
        b=before();s=once();self.assertEqual(pins(b),pins(s))
        t=ast.parse(s)
        starts=[n for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='run'
                and n.args and isinstance(n.args[0],ast.List)and any(isinstance(a,ast.Constant)and a.value=='--no-block'for a in n.args[0].elts)]
        self.assertEqual(1,len(starts));self.assertEqual(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],ast.literal_eval(starts[0].args[0]))
        guards=[n for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='persist'
                and n.args and isinstance(n.args[0],ast.Constant)and n.args[0].value=='external-start-guard.private.json']
        self.assertEqual(1,len(guards));self.assertLess(guards[0].lineno,starts[0].lineno)
        self.assertTrue('oldCompletedRunNotResumed'in s)
        self.assertTrue('originalBudgetSeconds'in s)
        self.assertTrue("assert ordinary_post()==before==ordinary_post()"in s)
        self.assertTrue("assert ordinary_post()==before"in s)

    def test_new_observer_binds_actual_boot_source_and_read_only_behavior(self):
        ns={'__file__':str(Path(__file__).with_name('pg1107_cold_current_observer.py')),'__name__':'fixture_only'}
        exec(observer(),ns);w=ns['watch']()
        self.assertTrue('cbca8738-3b24-4090-b77c-bf029677cdd6'in w)
        self.assertTrue('PG1068'in w);self.assertFalse('cc9ed874'in w)
        self.assertEqual('d5b00104280028d9ea81b44c1d1c805f3c2861ed',ns['SOURCE'])
        self.assertEqual('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',ns['DIGEST'])
        tree=ast.parse(w);commands=[ast.literal_eval(n)for n in ast.walk(tree)if isinstance(n,ast.List)and n.elts and all(isinstance(a,ast.Constant)for a in n.elts)]
        self.assertFalse(any('start'in c or 'stop'in c or 'restart'in c for c in commands))


if __name__=='__main__':unittest.main()
