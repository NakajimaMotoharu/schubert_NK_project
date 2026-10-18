import ast
import unittest
from pyflakes.api import check,checkPath
import pg5438_ownership_unused_sources as role


class UnusedGraph(unittest.TestCase):
    def test_single_pass_current_candidate_and_protected_capsule(self):
        raw='CURRENT='+repr(role.previous.CURRENT)+'\nSOURCE='+repr(role.previous.SOURCE)+'\nORACLE='+repr(role.previous.CURRENT)+'\n'
        # Already-normalized old graph: apply new single pass through protected boundary.
        result=role.bind_preserving_payloads(raw,role.normalized_text)
        ns={};exec(result,ns)
        self.assertEqual(ns['CURRENT'],role.CURRENT);self.assertEqual(ns['SOURCE'],role.SOURCE)
        self.assertEqual(ns['ORACLE'],role.previous.CURRENT)
        self.assertNotEqual(role.SOURCE,role.CURRENT)

    def test_complete18_syntax_original_tuple_and_native88_capture(self):
        values=role.sources()
        self.assertEqual(len(values),18)
        self.assertIn('Pg5438UnusedStage.java',values)
        self.assertIn("'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))",values['pg5438_native_refs.py'])
        for name,raw in values.items():
            if name.endswith('.py'):
                prelude="BUNDLE_HASH='pending'\n"if name in('pg5438_native_refs.py','pg5438_input_preflight.py')else''
                ast.parse(prelude+raw);self.assertEqual(check(prelude+raw,name),0)
        for path in(role.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
