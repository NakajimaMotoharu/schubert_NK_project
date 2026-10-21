import inspect
import unittest
from pyflakes.api import checkPath,check
import pg6318_outbox_graph_green as subject
import pg6320_outbox_graph_qualification as qualification


class Definitions(unittest.TestCase):
    def test_exact86_and_independent_red_source_two_main_only(self):
        cases,counts=subject.inventory()
        self.assertEqual((86,15),(sum(counts.values()),len(counts)))
        self.assertEqual(2,len(subject.MAIN))
        self.assertIn('api.messaging.outbound.OutboxFailureOwnershipTest',cases['api'])
        self.assertIn('web.logging.WebLogReplayWorkerTest',cases['web'])
        raw=subject.red.runner().replace('runner_source(38,9,target_count=16)','runner_source(86,15,target_count=16)').replace('pg6316-outbox-graph-red-v1','pg6318-outbox-graph-selected-v1').replace('def run_red():','def run_green():')
        bindings='from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6318_outbox_graph_green import inventory\n'
        self.assertEqual(0,check(bindings+raw,'<ordinary86 actual bindings>'))
        self.assertIn('pg6318-outbox-graph-selected-v1',raw)
        self.assertIn('(86,15)',inspect.getsource(qualification.main))
        for path in (subject.__file__,qualification.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
