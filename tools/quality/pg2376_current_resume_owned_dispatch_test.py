"""Full current stop stage and normal-scope command binding; no guest operation."""
import ast
import unittest
import pg2376_current_resume_owned_dispatch as p
import pg2375_current_resume_owned_compile as compiler


class Dispatch(unittest.TestCase):
    def test_exact_stage_source_namespace_and_signature(self):
        self.assertIn(p.GUEST,p.STAGE);self.assertIn(p.ARCHIVE,p.STAGE)
        self.assertIn('b2d6f605-61cf-425f-8fbd-12d606f6ee66',p.STAGE)
        self.assertNotIn('pg2274',p.STAGE+p.PARENT_PREQUAL)
        s=p.run_source();compile(s,'<current stage/stop entry>','exec')
        for n in ['pg2375-frozen-v1.safe.json','pg2376-stage-v1.exit','pg2377-parent-two-source-prequalification-v1','pg2378-newboot-pre-stop-full-v1','Pg2374NativeStop stop']:self.assertIn(n,s)
        self.assertIn("post['privateBeforeSha256'] != before",s)
        self.assertLess(s.index('PARENT_PREQUAL'),s.index('fresh = post_payload()'))
        self.assertLess(s.index('fresh = post_payload()'),s.index("'Pg2374NativeStop stop'"))
        tree=ast.parse(s)
        for n in ast.walk(tree):
            if isinstance(n,ast.List):
                self.assertFalse({'restart','reload','daemon-reload','start','reset-failed'}&{getattr(v,'value',None)for v in n.elts if isinstance(v,ast.Constant)})
        engine=compiler.previous.prior.prior.prior.old.prior.prior
        self.assertTrue(hasattr(engine.prior.prior,'W'))
        self.assertTrue(hasattr(p.previous.prior.prior.prior.prior,'runner'))


if __name__=='__main__':unittest.main()
