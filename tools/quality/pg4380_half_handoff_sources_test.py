import ast
import unittest
from pyflakes.api import check
import pg4380_half_handoff_sources as subject


class RemainingSources(unittest.TestCase):
    def test_whole_emitted_and_global_field_invariant(self):
        raw = subject.payload(); compile(raw, '<remaining controller>', 'exec'); self.assertEqual(0, check(raw, '<remaining controller>'))
        nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'fields' for t in n.targets)]
        self.assertEqual(1, len(nodes)); self.assertIsInstance(nodes[0].value, ast.Constant)
        self.assertIs(type(nodes[0].value.value), str)

    def test_two_exact_signals_metadata_continuity_and_frozen_partial(self):
        raw = subject.payload(); tree = ast.parse(raw)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'terminate']
        self.assertEqual([(815643, 15408795), (817783, 15666115)], [(ast.literal_eval(n.args[0]), ast.literal_eval(n.args[1])) for n in calls])
        for text in ['manager.RefUnit(unit)', 'manager.UnrefUnit(unit)', 'SSC294_OLD_PYTHON_GONE',
                     'SSC294_OLD_METADATA_GONE', "'javaSignalsIssued':0", "'oldScopesNormal':False", 'oldRetainerTransportExit',
                     '213f3a1e8e5f61a43d3a42b2ba0a86369b33fd45facf9747a09e0b3bdd95bab6',
                     'd64b8c588d337609a9b788f7540df50de2fb61dd69e9351ef2745d536bf7835b']:
            self.assertIn(text, raw)
        self.assertLess(raw.index("frame('SSC294_OLD_METADATA_GONE"), raw.index("inspect_result=job("))
        self.assertLess(raw.index("post_result=job("), raw.rindex('manager.UnrefUnit(unit)'))


if __name__ == '__main__':
    unittest.main()
