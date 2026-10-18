import ast
import copy
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
from bundle_hash_contract import require_bound
from pg5444_ownership_unused_post_test import capsules
import pg5446_ownership_ro_sources as role
import pg5448_ownership_ro_compile as compiler
import pg5450_ownership_ro_dispatch as dispatch
import pg5452_ownership_ro_post as post


class Ro(unittest.TestCase):
    def test_full88_all18_capsules_and_actual_A2_ABI(self):
        self.assertTrue(role.qualify()['native88Preserved'])
        normal,values=role.unused.sources(),compiler.generated()
        self.assertEqual(len(values),18)
        for suffix in('parent_receipt','warning_parent_projection'):
            self.assertEqual(capsules(normal['pg5438_'+suffix+'.py']),capsules(values['pg5446_'+suffix+'.py']))
        self.assertTrue(require_bound(values['pg5446_native_refs.py'],compiler.sha(compiler.PRIOR/'bundle.safe.json')))
        for name,raw in values.items():
            if name.endswith('.py'):self.assertEqual(check(raw,name),0)
        for marker in('pg5440-frozen-v1.safe.json','pg4980-release-v1/api/api.jar','pg4980-release-v1/operations/batch.jar'):
            self.assertIn(marker,compiler.compiler())

    def test_reject_wrong_source_missing_native_and_foreign_payload(self):
        original=json.loads((role.W/role.post.SLOT/'manifest.safe.json').read_bytes())
        for key,value in(('candidateSource',role.CURRENT),('currentSource',role.SOURCE),('native88Preserved',False),('newTenReferencesReturnedNormally',False),('actualExit',False)):
            bad=copy.deepcopy(original);bad['result'][key]=value
            with self.subTest(key=key),patch.object(role.unused,'qualify'),patch.object(role.json,'loads',return_value=bad),self.assertRaises(ValueError):role.qualify()

    def test_closed_actions_newnamespace_and_held_post(self):
        raw=dispatch.entry_source();ast.parse(raw)
        for marker in('pg5448-frozen-v1.safe.json','pg5450-stage-v1.exit','0.1.0-PG4980','Pg5446OriginalTupleTest'):
            self.assertIn(marker,raw)
        self.assertEqual(raw.count('with management_gate('),1)
        self.assertIn(dispatch.GUEST,dispatch.STAGE);self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        self.assertIn('/pg5446-ownership-ro-tools-v1.tar',dispatch.STAGE)
        with patch.object(dispatch.sys,'argv',['tool','activate']),patch.object(dispatch,'authenticate_host')as auth,self.assertRaises(ValueError):dispatch.main()
        auth.assert_not_called()
        raw=post.payload();self.assertEqual(check(raw,'<complete RO independent post>'),0)
        self.assertEqual(capsules(raw),capsules(post.unused_post.payload()))
        tree=ast.parse(raw);outer=next(n for n in tree.body if isinstance(n,ast.Try)and 'manager.UnrefUnit(u)'in ast.unparse(n.finalbody))
        held=ast.unparse(outer.body)
        for marker in('findmnt','--mountpoint','0.1.0-PG5430',role.SAVE,'candidateReadOnlyVerified=true','allNewScopesReturnedNormally=true','json.loads(before) == expected'):
            self.assertIn(marker,held)
        self.assertGreater(tree.body[-1].lineno,outer.end_lineno)
        self.assertIn("'candidateHostReadonlyVerified': True",ast.unparse(tree.body[-1]))
        for item in(role,compiler,dispatch,post):self.assertEqual(checkPath(item.__file__),0)
        self.assertEqual(checkPath(__file__),0)


if __name__=='__main__':unittest.main()
