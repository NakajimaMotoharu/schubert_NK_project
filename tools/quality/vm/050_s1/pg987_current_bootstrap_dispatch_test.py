"""New current frozen source/capturedRoot/no old-slot transport pins; no guest effect."""
import unittest
import pg985_current_bootstrap_compile as c
import pg986_current_bootstrap_native as d
class Test(unittest.TestCase):
    def test_all_phase_producer_consumer_slots_match_v3(self):
        raw=d.source()
        self.assertTrue("'pg983-'+action+'-v3'" in raw)
        for phase in ('stage','verify'):
            self.assertTrue('pg983-'+phase+'-v3.exit' in raw)
            self.assertFalse('pg983-'+phase+'-v1.exit' in raw)
        self.assertTrue('pg983-frozen-v3.safe.json' in raw)
        self.assertTrue('pg983-frozen-v3.safe.json' in c.source())
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
