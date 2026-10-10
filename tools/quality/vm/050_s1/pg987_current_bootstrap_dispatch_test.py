"""New current frozen source/capturedRoot/no old-slot transport pins; no guest effect."""
import unittest
import pg985_current_bootstrap_compile as c
import pg986_current_bootstrap_native as d
class Test(unittest.TestCase):
    def test_current_frozen_abi_and_independent_source_test(self):
        raw=c.source()
        for x in ('pg983_current_bootstrap_sources','pg984_current_bootstrap_sources_test.py','pg978-bootstrap-before-v2','pg932-release-v1','pg983-frozen-v3'):
            self.assertTrue(x in raw,'missing '+x)
    def test_current_completion_before_actual_start_and_never_Morning(self):
        raw=d.source()
        for x in ('pg963-stop-v1.exit','pg968-terminal-final-v1.exit','pg960-completed-readonly-v1.safe.json','pg978-bootstrap-before-v2','pg983-bootstrap-tools-v3','pg983-verify-v3.exit'):
            self.assertTrue(x in raw,'missing '+x)
        for old in ('pg894','pg895','PG862','pg983-bootstrap-tools-v1'):self.assertFalse(old in raw,'old '+old)
if __name__=='__main__':unittest.main()
