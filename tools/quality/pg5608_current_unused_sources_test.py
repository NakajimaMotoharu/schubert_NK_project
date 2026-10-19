import ast
import unittest
from pyflakes.api import check,checkPath
import pg5608_current_unused_sources as role


class CurrentUnusedGraph(unittest.TestCase):
    def test_one_pass_roles_and_original_capsule_not_reinterpreted(self):
        raw='CURRENT='+repr(role.previous.CURRENT)+'\nSOURCE='+repr(role.previous.SOURCE)+'\nORACLE='+repr(role.previous.CURRENT)+'\n'
        value=role.bind_preserving_payloads(raw,role.normalized_text);ns={};exec(value,ns)
        self.assertEqual(ns['CURRENT'],role.CURRENT);self.assertEqual(ns['SOURCE'],role.SOURCE)
        self.assertEqual(ns['ORACLE'],role.previous.CURRENT);self.assertNotEqual(role.SOURCE,role.CURRENT)
        self.assertIsInstance(role.SOURCE,str);self.assertIsInstance(role.candidate_bom(),str)

    def test_all18_complete_standalone_namespace_and_full_native_preservation(self):
        values=role.sources();self.assertEqual(len(values),18)
        self.assertIn('Pg5608UnusedStage.java',values)
        self.assertIn("'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))",values['pg5608_native_refs.py'])
        for name,raw in values.items():
            if name.endswith('.py'):
                prelude="BUNDLE_HASH='pending'\n"if name in('pg5608_native_refs.py','pg5608_input_preflight.py')else''
                ast.parse(prelude+raw);self.assertEqual(check(prelude+raw,name),0)
        for path in(role.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
