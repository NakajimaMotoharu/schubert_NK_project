"""Independent new source/post provenance, captured20 before permitted GC/current Ref scope."""
import unittest
from pg964_current_stop_test import fixture
import pg989_current_bootstrap_post as p
import pg991_current_bootstrap_post_v4 as v
class Test(unittest.TestCase):
    def test_post_run_and_slot_same_version_not_before_label(self):
        raw=v.payload(fixture(),{k:'1'*64 for k in ('before.private.json','after.private.json','parent.private.jsonl','complete.private')})
        self.assertTrue("'run':'PG989-bootstrap-post-v4'" in raw)
        self.assertFalse("'run':'PG978-bootstrap-before-v2'" in raw)
        self.assertTrue("save=base/'pg989-bootstrap-post-v4'" in raw)
    def test_captured20_original_tuple_new_seals_and_slot(self):
        raw=p.payload(fixture(),{k:'1'*64 for k in ('before.private.json','after.private.json','parent.private.jsonl','complete.private')})
        for x in ('pg983-bootstrap-existing-v3','pg978-bootstrap-before-v2','pg989-bootstrap-post-v3','40ef6e894573d2ffab1d1732124960f9c98d5f97','same_terminal_cohort','capturedNormal20VerifiedBeforeCurrent','ExecMainStatus','current_normal_or_gc','pg983-bootstrap-tools-v3'):
            self.assertTrue(x in raw,'missing '+x)
        self.assertLess(raw.index('manager.LoadUnit(u)'),raw.index('current_bootstrap=show'))
        self.assertLess(raw.index('current_bootstrap=show'),raw.index(' def snapshot():'))
        for old in ('pg894','pg895','pg887','e01612fcd7f2752df5ae0836b78538fd5e87f120'):self.assertFalse(old in raw,'old '+old)
if __name__=='__main__':unittest.main()
