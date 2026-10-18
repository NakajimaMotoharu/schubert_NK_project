"""All original functions unchanged; actual recovery and original abnormal exit required."""
import ast
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg5100_retained_pair_independent_post as post


class IndependentPost(unittest.TestCase):
    def test_full_original_functions_and_snapshot_remain_unchanged(self):
        raw=post.payload()
        self.assertEqual(0,check(raw,'<whole independent post>'))
        functions=lambda s:{n.name:ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(s))if isinstance(n,ast.FunctionDef)}
        old,new=functions(post.before.payload()),functions(raw)
        for name,body in old.items():self.assertEqual(body,new[name],name)
        for literal in (post.role.BASELINE,'39c2a0a82ab635f14cbf1f3d79728774a383864619674d75d37d4f282fe543f7',
                        "'retainedVerifyActualExit': 143", "'oldCloseUnknown': True",'parent_after_ref',post.SLOT):
            self.assertTrue(literal in raw,literal)
        for forbidden in ('pidfd_send_signal','StartUnit(','StopUnit(','pg_terminate_backend'):
            self.assertTrue(forbidden not in raw,forbidden)
        for path in (post.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_actual_recovery_required_and_old_exit_never_promoted(self):
        real=Path.read_bytes
        location=post.admission.W/'pg5086-current-bootstrap-verify-v1.safe.json'
        original=json.loads(real(location))
        self.assertEqual(143,original['actualExit'])
        for invalid in (None,False,0,1):
            wrong={**original,'actualExit':invalid}
            with patch.object(Path,'read_bytes',lambda p:json.dumps(wrong).encode()if p==location else real(p)):
                with self.assertRaises(ValueError):post.prerequisites()
        self.assertEqual('39c2a0a82ab635f14cbf1f3d79728774a383864619674d75d37d4f282fe543f7',post.prerequisites())


if __name__=='__main__':unittest.main()
