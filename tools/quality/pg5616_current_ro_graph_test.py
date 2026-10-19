import ast
import inspect
import symtable
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
from bundle_hash_contract import require_bound
import pg5616_current_ro_sources as role
import pg5618_current_ro_compile as compiler
import pg5620_current_ro_dispatch as dispatch
import pg5622_current_ro_post as post


class CurrentRoGraph(unittest.TestCase):
    def test_all18_exact_frozen_bundle_and_actual_current_abi(self):
        values=compiler.generated();self.assertEqual(len(values),18)
        self.assertTrue(require_bound(values['pg5616_native_refs.py'],compiler.sha(compiler.PRIOR/'bundle.safe.json')))
        for name,raw in values.items():
            if name.endswith('.py'):self.assertEqual(check(raw,name),0)
        for marker in('pg5610-frozen-v1.safe.json','pg5430-release-v1/api/api.jar','pg5430-release-v1/operations/batch.jar'):
            self.assertIn(marker,compiler.compiler())
        self.assertIn('post.payload()',inspect.getsource(compiler.main))

    def test_only_closed_ro_actions_new_output_and_single_management_gate(self):
        raw=dispatch.entry_source();ast.parse(raw)
        for marker in('pg5618-frozen-v1.safe.json','pg5620-stage-v1.exit','0.1.0-PG5430','Pg5616OriginalTupleTest'):self.assertIn(marker,raw)
        self.assertEqual(raw.count('with management_gate('),1)
        self.assertIn(dispatch.GUEST,dispatch.STAGE);self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        self.assertIn('/pg5616-current-ro-tools-v1.tar',dispatch.STAGE)
        scope=dispatch.namespace();exec(compile(raw,'<RO entry not invoked>','exec'),scope)
        required={s.get_name()for s in symtable.symtable(raw,'<RO entry>','exec').get_children()[0].get_symbols()if s.is_global()and s.is_referenced()}
        self.assertFalse(required-set(scope)-set(dir(__import__('builtins'))))
        with patch.object(dispatch.sys,'argv',['tool','activate']),patch.object(dispatch,'authenticate_host')as auth,self.assertRaises(ValueError):dispatch.main()
        auth.assert_not_called()

    def test_independent_held_pid1_ro_and_all_current_preservation(self):
        raw=post.payload();self.assertEqual(check(raw,'<new complete RO post>'),0)
        for marker in('findmnt','--mountpoint','0.1.0-PG5598',role.SAVE,'candidateReadOnlyVerified=true','allNewScopesReturnedNormally=true','json.loads(before_raw)==captured',"'nativePhysicalFiles':94","'candidateHostReadonlyVerified':True"):
            self.assertIn(marker,raw)
        self.assertIn('EXPECTED_CURRENT_SOURCE='+repr(role.CURRENT),raw)
        self.assertIn('EXPECTED_CANDIDATE_SOURCE='+repr(role.SOURCE),raw)
        tree=ast.parse(raw);outer=next(n for n in tree.body if isinstance(n,ast.Try)and 'manager.UnrefUnit(u)'in ast.unparse(n.finalbody))
        self.assertIn('findmnt',ast.unparse(outer.body));self.assertGreater(tree.body[-1].lineno,outer.end_lineno)
        for item in(role,compiler,dispatch,post):self.assertEqual(checkPath(item.__file__),0)
        self.assertEqual(checkPath(__file__),0)


if __name__=='__main__':unittest.main()
