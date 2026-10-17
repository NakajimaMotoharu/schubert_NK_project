import ast
from collections import Counter
import copy
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
from immutable_payload_binding import PROTECTED
from bundle_hash_contract import require_bound
import pg4872_ssc301_302_ro_sources as role
import pg4874_ssc301_302_ro_compile as compiler
import pg4876_ssc301_302_ro_dispatch as dispatch
import pg4878_ssc301_302_ro_post as post


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n) for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in PROTECTED for t in n.targets))


class Ro(unittest.TestCase):
    def test_actual_post_all18_and_immutable_capsules_one_bundle_current_abi(self):
        self.assertTrue(role.qualify()['native72Preserved'])
        normal=role.unused.sources();values=compiler.generated();self.assertEqual(18,len(values))
        for suffix in ('parent_receipt','warning_parent_projection'):
            self.assertEqual(capsules(normal['pg4864_'+suffix+'.py']),capsules(values['pg4872_'+suffix+'.py']))
        digest=compiler.sha(compiler.PRIOR/'bundle.safe.json')
        self.assertTrue(require_bound(values['pg4872_native_refs.py'],digest))
        self.assertIn("'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))",values['pg4872_native_refs.py'])
        self.assertNotIn('BUNDLE_HASH',values['pg4872_input_preflight.py'])
        for name,raw in values.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<actual RO '+name+'>'))
        for path in ('api/api.jar','operations/batch.jar','api/lib/*','operations/lib/*'):
            self.assertIn('pg4702-release-v1/'+path,compiler.compiler())
        self.assertIn('pg4866-frozen-v1.safe.json',compiler.compiler())

    def test_no_foreign_missing_or_boolean_exit_qualifies(self):
        original=json.loads((role.W/'pg4870-ssc301-302-unused-post-v1/manifest.safe.json').read_bytes())
        for key,value in [('candidateSource',role.CURRENT),('currentSource',role.SOURCE),('native72Preserved',False),('newTenReferencesReturnedNormally',False),('candidateManifestSha256','0'*64),('actualExit',False)]:
            bad=copy.deepcopy(original);bad['result'][key]=value
            with patch.object(role.unused,'qualify'),patch.object(role.json,'loads',return_value=bad),self.subTest(key=key),self.assertRaises(ValueError):role.qualify()

    def test_ro_actual_entry_only_actions_and_same_current(self):
        raw=dispatch.entry_source()
        for literal in ('pg4874-frozen-v1.safe.json','pg4876-stage-v1.exit','0.1.0-PG4702','Pg4872OriginalTupleTest',"['stage'],['prepare-ro']"):
            self.assertIn(literal,raw)
        for old in ('pg3998','pg3784','pg3782','PG3420','--resume'):self.assertNotIn(old,raw)
        self.assertEqual(1,raw.count('with management_gate('))
        self.assertIn(dispatch.GUEST,dispatch.STAGE);self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        with patch.object(dispatch.sys,'argv',['tool','place']),patch.object(dispatch,'authenticate_host') as auth,self.assertRaises(ValueError):dispatch.main()
        auth.assert_not_called()

    def test_pid1_mount_and_receipt_under_refs_success_after_normal_close(self):
        raw=post.payload();self.assertEqual(0,check(raw,'<actual RO complete post>'))
        t=ast.parse(raw);scope=next(n for n in t.body if isinstance(n,ast.Try) and 'manager.UnrefUnit(u)' in ast.unparse(n.finalbody))
        held=ast.unparse(scope.body)
        for text in ('findmnt','--mountpoint','0.1.0-PG4860',role.SAVE,'candidateReadOnlyVerified=true','allNewScopesReturnedNormally=true','json.loads(before) == expected'):
            self.assertIn(text,held)
        self.assertGreater(t.body[-1].lineno,scope.end_lineno)
        self.assertIn("'candidateHostReadonlyVerified': True",ast.unparse(t.body[-1]))
        for path in (role.__file__,compiler.__file__,dispatch.__file__,post.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
