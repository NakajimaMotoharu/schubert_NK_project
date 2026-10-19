import ast
import inspect
import symtable
import unittest
from pyflakes.api import check,checkPath
import pg5624_current_publication_sources as role
import pg5626_current_publication_compile as compiler
import pg5628_current_publication_dispatch as dispatch
import pg5630_current_publication_post as post


class CurrentFinitePublication(unittest.TestCase):
    def test_all24_static_and_seven_actual_current_abi_phases(self):
        r=role.qualify();self.assertTrue(r['candidateHostReadonlyVerified']);self.assertEqual(r['nativePhysicalFiles'],94)
        values=compiler.generated();self.assertEqual(len(values),24)
        self.assertIn('Pg5624OrdinaryPublication.java',values)
        for name,raw in values.items():
            if name.endswith('.py'):self.assertEqual(check(raw,name),0)
        raw=compiler.compiler();compile(raw,'<finite seven phases>','exec')
        for marker in('pg5610-frozen-v1.safe.json','pg5430-release-v1/api/api.jar','pg5626-',"('transition','TransitionTest')","'Pg5624'+suffix"):
            self.assertIn(marker,raw)

    def test_finite_entry_exact_namespace_and_pre_mutation_post(self):
        raw=dispatch.source();scope=dispatch.namespace();exec(compile(raw,'<finite not invoked>','exec'),scope)
        required={s.get_name()for s in symtable.symtable(raw,'<finite entry>','exec').get_children()[0].get_symbols()if s.is_global()and s.is_referenced()}
        self.assertFalse(required-set(scope)-set(dir(__import__('builtins'))))
        self.assertIn(dispatch.GUEST,dispatch.STAGE);self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        self.assertIn('pg5624-current-publication-tools-v1.tar',dispatch.STAGE)
        self.assertIn('pg5626-frozen-v1.safe.json',raw);self.assertEqual(raw.count('with management_gate('),1)
        self.assertIn('payload()',inspect.getsource(dispatch.main))

    def test_readonly_post_source_correct_new_current_and_original_full94(self):
        raw=post.readonly_source();compile(raw,'<independent newCurrent readonly fragment>','exec')
        for text in('0.1.0-PG5598',post.FULL_BEFORE,post.FULL_SHA,role.SOURCE,role.BOM):self.assertIn(text,raw)
        self.assertIn('==94)',raw);self.assertNotIn('==88)',raw)
        self.assertNotEqual(role.CURRENT,role.SOURCE)
        for item in(role,compiler,dispatch,post):self.assertEqual(checkPath(item.__file__),0)
        self.assertEqual(checkPath(__file__),0)
        tree=ast.parse(raw)
        self.assertFalse([n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in('StartUnit','StopUnit','KillUnit','RestartUnit')])


if __name__=='__main__':unittest.main()
