import ast
import inspect
import json
import unittest
from pyflakes.api import checkPath
import pg5610_current_unused_compile as compiler
import pg5612_current_unused_dispatch as dispatch


class ActualCurrentAbiAndDispatch(unittest.TestCase):
    def test_actual296_abi_and_new0ea_candidates_are_distinct(self):
        raw=compiler.compiler()
        for text in('pg5430-release-v1','pg5498-frozen-v1.safe.json','pg5496-current-owned-tools-v1','Pg5496','pg5598-candidate-build-v1.safe.json','pg5606-current-full-preservation-v2','pg5610-frozen-v1.safe.json'):
            self.assertIn(text,raw)
        self.assertNotIn('pg4980-release-v1',raw);self.assertNotIn('pg5062-frozen-v1',raw)
        compile(raw,'<complete actual ABI producer>','exec')
        self.assertIn('post.payload()',inspect.getsource(compiler.main))

    def test_dispatch_has_single_gate_explicit_action_and_actual_fresh_predicates(self):
        raw=dispatch.source();stage=dispatch.stage_source();compile(raw,'<unused only>','exec');compile(stage,'<new stage only>','exec')
        self.assertNotIn('management_gate',raw)
        before=dispatch.before_record();self.assertTrue(before['allResources0']);self.assertTrue(before['allTenUnitsKernelEmpty'])
        self.assertEqual(before['nativePhysicalFiles'],94)
        candidate=json.loads((dispatch.role.W/'pg5598-candidate-build-v1.safe.json').read_bytes())
        scope=dispatch.runtime_namespace(candidate,before)
        exec(compile(raw,'<not executed unused dispatcher>','exec'),scope)
        self.assertTrue(callable(scope['main']))
        # Merely compile and bind here: do not call stage/place or install input.
        self.assertIn('post.payload()',inspect.getsource(dispatch.main))
        self.assertIsInstance(dispatch.role.SOURCE,str)
        for path in(compiler.__file__,dispatch.__file__,__file__):self.assertEqual(checkPath(path),0)
        forbidden={'StartUnit','StopUnit','KillUnit','RestartUnit','Reload'}
        self.assertFalse([n for n in ast.walk(ast.parse(stage))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in forbidden])


if __name__=='__main__':unittest.main()
