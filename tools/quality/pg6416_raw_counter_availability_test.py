import ast
import copy
import inspect
import unittest
from pyflakes.api import checkPath
import pg5732_enum48_selected as engine
from pg6052_expiry_combined_selected import runner_source


class CounterAvailability(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(inspect.getsource(engine.main))
        self.raw = next(n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == 'target_counters' for t in n.targets))
        self.verdict = next(n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                            and any(isinstance(t, ast.Name) and t.id == 'target100' for t in n.targets))
        self.complete = {k: dict(covered=1, missed=0) for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}

    def project(self, counters):
        return eval(compile(ast.Expression(self.raw), '<actual raw projection>', 'eval'), {'counters': counters})

    def qualified(self, counters, count=14):
        return eval(compile(ast.Expression(self.verdict), '<actual selected verdict>', 'eval'),
                    {'target_counters': {str(i): copy.deepcopy(counters) for i in range(count)}})

    def test_complete_positive_measured_four_and_partial_target_group(self):
        self.assertEqual(self.complete, self.project(self.complete))
        self.assertTrue(self.qualified(self.complete))
        self.assertFalse(self.qualified(self.complete, 13))

    def test_missing_branch_and_all_missing_do_not_create_zero_counters(self):
        raw = dict(self.complete); del raw['BRANCH']
        self.assertNotIn('BRANCH', self.project(raw)); self.assertFalse(self.qualified(self.project(raw)))
        self.assertEqual({}, self.project({})); self.assertFalse(self.qualified({}))

    def test_zero_or_missed_counter_never_becomes100(self):
        for key in self.complete:
            for value in (dict(covered=0, missed=0), dict(covered=0, missed=1), dict(covered=1, missed=1)):
                counters = copy.deepcopy(self.complete); counters[key] = value
                with self.subTest(counter=key, value=value):
                    self.assertFalse(self.qualified(self.project(counters)))

    def test_emitted_profiles_preserve_raw_availability_without_requiring_partial100(self):
        raw = runner_source(25, 11, target_count=1)
        self.assertIn('if k in counters', raw); self.assertNotIn("counters.get(k,{'covered':0,'missed':0})", raw)
        self.assertIn('done=done  # partial coverage is reported,not invented or excluded', raw)
        self.assertIn("c[k]['covered']>0", raw)
        for path in (engine.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
