"""Actual direct entry AST and readonly proof before normal close; no guest action."""
import ast
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4718_ssc299_ro_dispatch as dispatch
import pg4720_ssc299_ro_post as post


class RoAction(unittest.TestCase):
    def test_actual_entry_fixed_current_source_and_only_ro_actions(self):
        raw=dispatch.entry_source()
        for literal in ['pg4716-frozen-v1.safe.json','pg4718-stage-v1.exit','0.1.0-PG4432',
                        'Pg4714OriginalTupleTest',"['stage'],['prepare-ro']"]:self.assertIn(literal,raw)
        for old in ['pg3998','pg3784','pg3782','PG3420','--resume']:self.assertNotIn(old,raw)
        self.assertEqual(1,raw.count('with management_gate('))
        self.assertIn(dispatch.GUEST,dispatch.STAGE)
        self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        compile(raw,'<actual normal RO entry>','exec')
        with patch.object(dispatch.sys,'argv',['tool','place']),patch.object(dispatch,'authenticate_host')as auth:
            with self.assertRaises(ValueError):dispatch.main()
            auth.assert_not_called()

    def test_pid1_mount_and_normal_receipt_inside_refs_success_after_close(self):
        raw=post.payload();self.assertEqual(0,check(raw,'<complete normalRO proof>'))
        t=ast.parse(raw);scope=next(n for n in t.body if isinstance(n,ast.Try)and 'manager.UnrefUnit(u)'in ast.unparse(n.finalbody))
        body=ast.unparse(scope.body)
        for literal in ['findmnt','--mountpoint','0.1.0-PG4702',post.role.SAVE,'candidateReadOnlyVerified=true','allNewScopesReturnedNormally=true']:
            self.assertIn(literal,body)
        success=next(n for n in t.body if isinstance(n,ast.Assign)and 'candidateHostReadonlyVerified' in ast.unparse(n))
        self.assertGreater(success.lineno,scope.end_lineno)
        for path in [dispatch.__file__,post.__file__,__file__]:self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
