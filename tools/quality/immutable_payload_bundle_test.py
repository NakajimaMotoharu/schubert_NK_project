"""Independent bundle-level history preservation and malicious generator counterexamples."""
import ast
import copy
import inspect
import unittest
import pg2050_fresh_completed_runtime_retirement_sources as legacy
from immutable_payload_binding import transform_bundle_preserving_payloads as bind


def seed():
    raw=inspect.getsource(legacy.sources)
    values=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)and isinstance(n.value,str)and n.value.startswith("values={n.replace('2030'")]
    if len(values)!=1:raise ValueError('one actual inherited seed required')
    return values[0]


def old_transform(values):
    ns={'stop_sources':lambda:values};exec(compile(seed(),'<actual inherited seed>','exec'),ns)
    # A subsequent generator rewrite must also not reach original capsules.
    return {name:raw.replace('pg2030','subsequent-change')for name,raw in ns['values'].items()}


class ImmutableBundle(unittest.TestCase):
    def test_actual_legacy_seed_reproduces_and_new_whole_transform_preserves(self):
        data={'history':[{'text':'pg2030/Pg2030/PG2030','marker':'__pgpt_immutable_bundle_a__'}]}
        raw="TOOLS='pg2030'\nORACLE="+repr('CHAIN='+repr(data)+'\n')+"\nGUARD='pg2030 original guard'\n"
        original={'pg2030_scope.py':raw,'Pg2030.java':'class Pg2030 {}'};before=copy.deepcopy(original)
        self.assertNotEqual(raw,old_transform(original)['pg2050_scope.py'])
        result=bind(original,old_transform)
        values={n.targets[0].id:ast.literal_eval(n.value)for n in ast.parse(result['pg2050_scope.py']).body if isinstance(n,ast.Assign)}
        self.assertEqual('pg2050',values['TOOLS']);self.assertEqual('CHAIN='+repr(data)+'\n',values['ORACLE']);self.assertEqual('pg2030 original guard',values['GUARD'])
        self.assertEqual('class Pg2050 {}',result['Pg2050.java']);self.assertEqual(before,original)

    def test_added_helpers_identical_capsules_and_nested_scope(self):
        raw="def f():\n ORACLE='same pg2030'\n return ORACLE\n"
        def transform(values):return {**{name.replace('2030','2050'):v.replace('pg2030','pg2050')for name,v in values.items()},'helper.py':'def identity(v):return v\n'}
        result=bind({'pg2030_a.py':raw,'pg2030_b.py':raw},transform)
        self.assertEqual(raw,result['pg2050_a.py']);self.assertEqual(raw,result['pg2050_b.py']);self.assertIn('helper.py',result)

    def test_loss_duplicate_comment_move_and_payload_injection_reject(self):
        original={'a.py':"ORACLE='original'\n"}
        transforms=[lambda v:{},lambda v:{'a.py':v['a.py']*2},lambda v:{'a.py':'# '+v['a.py']},lambda v:{'a.py':v['a.py']+"GUARD='new unexpected authority'\n"},lambda v:{'a.java':v['a.py']},lambda v:{'a.py':v['a.py'].replace('__pgpt_immutable_bundle_a__','lost')}]
        for transform in transforms:
            with self.subTest(transform=transform):
                with self.assertRaises(ValueError):bind(original,transform)
        with self.assertRaises(ValueError):bind({'a.py':'not valid Python ;'},lambda v:v)
        with self.assertRaises(ValueError):bind({'a.py':None},lambda v:v)
        with self.assertRaises(ValueError):bind(original,lambda v:None)


if __name__=='__main__':unittest.main()
