"""Exact current command/profile admission and immutable four-seal post; no mutation."""
import ast
import unittest
from pyflakes.api import check
import pg2394_current_runtime_retirement_dispatch as p


class Dispatch(unittest.TestCase):
    def test_actual_current_retire_only_and_fixed_post_before_action(self):
        r=p.run_source();compile(r,'<current retirement dispatch>','exec')
        self.assertIn("('stage', 'retire')",r)
        self.assertIn('Pg2392NativeStop retire',r)
        self.assertNotIn('Pg2392NativeStop stop',r)
        self.assertIn("post['proofHashes']['after.private.json']['sha256'] != before",r)
        self.assertIn('pg2394-stage-v1.exit',r)
        self.assertIn(p.ARCHIVE,p.STAGE);self.assertIn(p.GUEST,p.STAGE)
        self.assertIn('b2d6f605-61cf-425f-8fbd-12d606f6ee66',p.STAGE)
        self.assertNotIn('pg2374',p.STAGE+p.PARENT_PREQUAL)
        raw=p.post_payload();self.assertEqual(0,check(raw,'<actual current full pre-retire post>'))
        self.assertIn('pg2368-current-resume-full-seal-v1',raw)
        self.assertEqual(p.SHA,p.context()[0])
        for n in ast.walk(ast.parse(r)):
            if isinstance(n,ast.List):self.assertFalse({'start','restart','reset-failed','stop'}&{getattr(v,'value',None)for v in n.elts if isinstance(v,ast.Constant)})


if __name__=='__main__':unittest.main()
