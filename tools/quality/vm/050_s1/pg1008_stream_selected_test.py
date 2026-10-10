"""Independent CLI/source/scope binding, no Maven/VM execution."""
import ast
import unittest
from pg1008_stream_selected_v2 import source,selected

class CommandTest(unittest.TestCase):
    def test_current_pinned_reactor_and_exact_four_suites(self):
        raw=source();ast.parse(raw)
        self.assertTrue("'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'"in raw)
        self.assertTrue("'org.jacoco:jacoco-maven-plugin:0.8.15:report'"in raw)
        self.assertFalse("'spotbugs:check'"in raw)
        self.assertFalse("'jacoco:report'"in raw)
        self.assertTrue("'src/schubert-nk-batch', '-am'"in raw)
        self.assertTrue("'run':'PG1008-stream-selected-v2'"in raw)
        self.assertEqual({'batch':['InspectorUnitProbeTest','BrokerJournalQueryTest','InspectorHeldStateContractTest','InspectorUnitSnapshotTest']},selected.TESTS)
        self.assertTrue('40ef6e894573d2ffab1d1732124960f9c98d5f97'in raw)
        self.assertFalse('PG1007-stream-selected-v1'in raw)

if __name__=='__main__':unittest.main()
