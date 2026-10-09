import ast
import unittest
from pg798_probe_sources import java,helper
from pg798_probe_compile import source as compile_source,refs_source
from pg798_probe_native import source as native_source


class Test(unittest.TestCase):
    def test_actual_assembled_surface(self):
        raw=java();py=helper();ast.parse(py);ast.parse(compile_source());ast.parse(native_source());ast.parse(refs_source())
        for value in ('pg798-scope-tools-v1','pg798-scope-probe-v1','Pg798DatabaseScope','databaseScope.verify();','process.waitFor(250,','count%256==0)pulse()','maxGapNanos=','batchLease.confirmClosed();schemaLease.confirmClosed();'):
            self.assertIn(value,raw)
        for value in ('stop_one',"'stop'",'systemctl stop'):self.assertNotIn(value,py)
        self.assertIn('if(!notified&&!retainPulse())',raw)
        self.assertIn('pulse();parent();pulse();signed();pulse();',raw)
        self.assertNotIn('Pg456SignedMigration.business(db)',raw)
        for value in ('Pg798DatabaseProbeTest.java','Pg798DatabaseScopeTest','Pg798ProbeWiringTest','pg798-frozen-v1.safe.json','pg798-scope-tools-v1'):
            self.assertIn(value,compile_source())
        self.assertIn('pg798-stage-v1.exit',native_source())
        for value in ('pg778','Pg778','PG778','pg798-failed758-tools-v1'):
            self.assertNotIn(value,native_source())


if __name__=='__main__':unittest.main()
